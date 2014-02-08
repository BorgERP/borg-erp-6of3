# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012- 2014 DECODIO Slobodni programi d.o.o., Zagreb, www.slobodni-programi.hr
#    Author: Goran Kliska
#    Contributions:
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields, orm
import decimal_precision as dp


class doc_line_mixin(osv.AbstractModel):
    _name = 'doc.line.mixin'
    _inherit = ['product.mixin']

    _columns = {
            'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of lines."),
            # FROM  'product.mixin'
            # 'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=False,),  # TODO required=True
            # 'quantity': fields.float('Quantity', required=False, help='Quantity in UOM'),  # TODO required=True
            # 'base_uom_id': fields.related('product_id', 'uom_id', type='many2one',relation='product.uom',string='Base UOM', required=True, readonly=True),
            # 'base_uom_coeff': fields.float('Unit of Measure Coefficient', digits=(12, 12), help='Coefficient used to convert Unit of Measure into Base Unit of Measure'' uos = uom * coeff'),
            # 'base_uom_qty': fields.float('Base UOM Quantity',digits_compute=dp.get_precision('Product UoS'),  help='Quantity in the base UoM of the product')

            'price_unit': fields.float('List Price', required=True, digits=(16, 8)),  # unrounded
            # new fields
            'discount1_percent': fields.float('Discount', digits=(12, 2), help='1. Line Discount percent'),
            'discount2_percent': fields.float('Second discount', digits=(12, 2), help='2. Line Discount percent'),
            'global_discount_percent': fields.float('Global discount', digits=(12, 2), readonly=True, help='Discount from document header. Calculated as 3.discount percent'),
            # 'global_discount_percent': fields.related('order_id', 'global_discount_percent',
            #                            type='float', relation='app.document', string='Global discount',
            #                            store=True, , readonly=True, help='Discount from document header. Calculated as 3.discount percent'),
            # override/add
            'discount': fields.float('Total Discount(%)', digits=(16, 4), readonly=True,),
            'discount_amount': fields.float('Discount by amount', digits=(16, 8), digits_compute=dp.get_precision('Account')),
            'discount_total': fields.float('Total Discount', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),
            'base_price': fields.float('Base price', digits=(16, 8), readonly=False, digits_compute=dp.get_precision('Account')),
            'amount': fields.float('Line value', required=False, digits_compute=dp.get_precision('Account'), help="Base price * Quantity"),  # rounded
            'amount_tax': fields.float('Line value w. tax', required=False, digits_compute=dp.get_precision('Account')),  # notrounded
            # 'price_subtotal': fields.function(_amount_line, string='Subtotal', type="float",
            # => (price_unit * (1-(line.discount or 0.0)/100.0) * quantity)  +/- account.tax.(compute_all)->'total':Total without taxes
            # --> sum(price_subtotal)->amount_untaxed

            # CCURRENCY
            'ccurrency_price_subtotal': fields.float('Untaxed', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),
            'ccurrency_base_price': fields.float('Untaxed', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),
            'ccurrency_amount': fields.float('Line value w/o tax', required=True, digits_compute=dp.get_precision('Account')),  # rounded
            'ccurrency_amount_tax': fields.float('Line value w tax', required=True, digits_compute=dp.get_precision('Account')),  # notrounded

            # 'invoice_date': fields.related('invoice_id','date_invoice',type='date',string='Invoice Date'),

            'supplier_cost': fields.float('Supplier amount', readonly=True,
                             help="IN:=> line value in ccurrency, OUT:=> 0.00 or last supplier cost as info"),
            'landed_costs' : fields.float('Landed Costs', readonly=True,
                             help="IN:=> sum of costs for line in ccurrency, OUT:=> last IN landed cost as info"),
            'total_costs'  : fields.float('Total costs', readonly=True,
                             help="IN=> supplier_cost+landed_costs, OUT:=> calculated Brutto cost in ccurrency"),

            'margin_brutto1'  : fields.float('Margin', readonly=True, help="IN=> 0.0, OUT:=>ccurrency_amount - total_costs in ccurrency"),
            'margin_brutto1_percent'  : fields.float('Margin%', readonly=True, help="IN=> 0.0, OUT:=>ccurrency_amount - total_costs in %"),

            'overhead_cost': fields.float('Overhead cost', readonly=True, help="IN:=> 0.00, OUT:=> 0.00 TODO in ccurrency"),
            'margin_brutto2'  : fields.float('Margin', readonly=True, help="IN=> 0.0, OUT:=>ccurrency_amount - total_costs-overhead_costi n ccurrency"),
            'margin_brutto2_percent'  : fields.float('Margin%', readonly=True, help="IN=> 0.0, OUT:=>ccurrency_amount - total_costs-overhead_cost in %"),
            }

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def create(self, cr, uid, vals, context=None):
        res = super(doc_line_mixin, self).create(cr, uid, vals, context=context)
        self._calc_line_vals(cr, uid, [res], context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        ''' Overide to set base product uom '''
        if not context:
            context = {}
        res = super(doc_line_mixin, self).write(cr, uid, ids, vals, context)
        if not context.get('_calc_line_vals'):
            self._calc_line_vals(cr, uid, ids, context=context)
        return res

    def _uom_id_change(self, cr, uid, ids, uom_id, product_id,
                        entry_type='price',
                        context=None):
        vals = {'uom_id': uom_id, 'product_id': product_id}
        self._get_base_uom_vals(self, cr, uid, id, vals, context=context)
        return vals

    def _calc_discount_percent(self, cr, uid, ids, discount1, discount2=0.0, global_discount=0.0):
        return 100 - ((100.00 - discount1) * (100.00 - discount2) * (100.00 - global_discount) / 10000)

    def discount_change(self, cr, uid, ids,
                        discount1, discount2=0.0, global_discount=0.0, discount_amount=0.0,
                        quantity=0.0, price_unit=0.0, base_price=0.0, amount=0.0, amount_tax=0.0,
                        entry_type='price',
                        context=None):
        if context is None:
            context = {}
        values = {}
        domain = {}
        warning = {}
        discount_percent = self._calc_discount_percent(cr, uid, ids,
                                                       discount1, discount2, global_discount)
        values['global_discount_percent'] = global_discount
        values['discount'] = discount_percent
        entry_type = entry_type or 'price'
        if entry_type == 'price':
            base_price = price_unit * (1.0 - discount_percent / 100.0)
            values['base_price'] = base_price
            values['amount'] = base_price * quantity
            values['discount_total'] = (price_unit - base_price) * quantity

        if entry_type == 'amount':  # TODO
            base_price = price_unit * (1.0 - discount_percent / 100.0)
            values['price_unit'] = price_unit * quantity
        if entry_type == 'amount_tax':  # TODO
            base_price = price_unit * (1.0 - discount_percent / 100.0)
            values['price_unit'] = price_unit * quantity

        return {'value': values, 'domain': domain, 'warning': warning}

    def _get_header_fld(self, cr, uid, context=None):
        if self._table in ('purchase_order_line', 'sale_order_line'):
            return 'order_id'
        if self._table in ('stock_move',):
            return 'picking_id'

    def _calc_line_vals(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        values = {}
        header_fld = self._get_header_fld(cr, uid, context=context) or 'order_id'
        for line in self.browse(cr, uid, ids, context=None):
            vals = self.discount_change(cr, uid, ids,
                        discount1=line.discount1_percent,
                        discount2=line.discount2_percent,
                        global_discount=line.global_discount_percent,
                        discount_amount=line.discount_amount,
                        quantity=line.quantity,
                        price_unit=line.price_unit,
                        base_price=line.base_price,
                        amount=line.amount,
                        amount_tax=line.amount_tax,
                        entry_type=header_fld and line[header_fld].entry_type or 'price',
                        context=context)['value']
            '''
            if inv_line.invoice_id.date_invoice:
                context['date'] = inv_line.invoice_id.date_invoice
                context['force_currency_inv_rate'] = inv_line.invoice_id.ccurrency_rate
            result[inv_line.id] = {
                'ccurrency_price_subtotal': currency_obj.compute(cr, uid, src_cur, company_cur,
                                                                                   inv_line.price_subtotal, context=context),
                'ccurrency_price_unit': currency_obj.compute(cr, uid, src_cur, company_cur,
                                                                               inv_line.price_unit, context=context)
           '''

            ctx = context.copy()
            ctx['_calc_line_vals'] = True
            self.write(cr, uid, line.id, vals, context=ctx)

    '''
    <field name="product_id" on_change="
       product_id_change(product_id, uos_id, quantity, name, parent.type, parent.partner_id, parent.fiscal_position, price_unit, parent.address_invoice_id, parent.currency_id, context, parent.company_id)"
    '''

    def Xinvoice_lineX_product_id_change(self, cr, uid, ids,  # from invoice_line
                     product_id, uom_id, quantity=0, name='',

                     type='out', company_id=None, fposition_id=False, currency_id=False,
                     partner_id=False, address_id=False,
                     global_discount_percent=False,
                     entry_type='price',

                     list_price=False,
                     price_unit=False,
                     amount=False,
                     amount_tax=False,
                     discount1_percent=False, discount2_percent=False, discount_amount=False,
                     context=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id', False)
        context = dict(context)
        context.update({'company_id': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined !'), _("You must first select a partner !"))

        if not product_id:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain': {'uom_id': []}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain': {'uom_id': []}}

        partner = self.pool.get('product.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
        if partner.lang:
            context.update({'lang': partner.lang})

        result = {}
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)

        if type in ('out_invoice', 'out_refund'):
            a = product.product_tmpl_id.property_account_income.id
            if not a:
                a = product.categ_id.property_account_income_categ.id
        else:
            a = product.product_tmpl_id.property_account_expense.id
            if not a:
                a = product.categ_id.property_account_expense_categ.id

        if context.get('account_id', False):
            # this is set by onchange_account_id() to force the account choosen by the
            # user - to get defaults taxes when product_id have no tax defined.
            a = context['account_id']

        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        if type in ('out', 'out_invoice', 'out_refund'):
            taxes = product.taxes_id and product.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = product.supplier_taxes_id and product.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
        result['invoice_line_tax_id'] = tax_id
        warning = {}
        # When product_id changes, price ALWAYS need to be reset. If not price
        # found in product_id, or pricelist, it should become False. Only if
        # product_id has been cleared by user, we will leave price_unit as is.
        if  product_id:
            price_unit, pu_warning = self._price_unit_get(
                cr, uid, product_id, uom_id, quantity, type, partner_id,
                currency_id, context=context)
            result['price_unit'] = price_unit  # might be False
            warning.update(pu_warning)

        # KGBif type in ('in_invoice', 'in_refund'):
        #    result.update( {'price_unit': price_unit or product.standard_price,'invoice_line_tax_id': tax_id} )
        # else:
        #    result.update({'price_unit': product.list_price, 'invoice_line_tax_id': tax_id})

        result['name'] = product.partner_ref

        domain = {}
        result['uos_id'] = product.uom_id.id or uom_id or False
        result['note'] = product.description
        if result['uos_id']:
            res2 = product.uom_id.category_id.id
            if res2:
                domain = {'uos_id':[('category_id', '=', res2)]}

        res_final = {'value':result, 'domain':domain, 'warning': warning}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('product.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('product.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            if type in ('in', 'in_invoice', 'in_refund'):
                res_final['value']['price_unit'] = product.standard_price
            # KGB TODO force rate maybe?
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if uom_id:
            uom_id = self.pool.get('product_id.uom_id').browse(cr, uid, uom_id, context=context)
            if product.uom_id.category_id.id == uom_id.category_id.id:
                new_price = res_final['value']['price_unit'] * uom_id.factor_inv
                res_final['value']['price_unit'] = new_price
        return res_final

    def Xinvoice_lineX_invoice_line_price_unit_get(
            self, cr, uid, product_id, uom_id, qty, invoice_type, partner_id,
            currency_id, context=None):
        price_unit = False
        warning = {}
        standard_currency_id = currency_id
        partner_model = self.pool.get('res.partner')
        partner_obj = partner_model.browse(
            cr, uid, partner_id, context=context)
        assert partner_obj, _('No partner found for id %d') % partner_id
        if invoice_type in ('in', 'in_invoice', 'in_refund'):
            field = 'list_price'
            pricelist_property = 'property_product_pricelist_purchase'
        else:
            field = 'standard_price'
            pricelist_property = 'property_product_pricelist'
        if  pricelist_property in partner_obj:
            pricelist_id = partner_obj[pricelist_property].id
        else:
            pricelist_id = False
        # Check whether standard price p.u. modified by pricelist
        if  pricelist_id:
            pricelist_model = self.pool.get('product.pricelist')
            price_unit = pricelist_model.price_get(
                cr, uid, [pricelist_id], product_id, qty or 1.0, partner_id,
                {'uom': uom_id})[pricelist_id]
            if  price_unit is False:  # 0.0 is OK, we night have free products
                warning = {
                   'title': _('No valid pricelist line found!'),
                   'message':
                    _("Couldn't find a pricelist line matching this product"
                    " and quantity.\n"
                    "You have to change either the product, the quantity or"
                    " the pricelist.")
                }
            # Pricelist converts price from standard currency to pricelist
            # currency. We have to convert this to the invoice currency.
            # In practice that will often mean undoing the conversion
            # done by the pricelist object
            pricelist_obj = pricelist_model.browse(cr, uid, pricelist_id)
            if  (pricelist_obj and pricelist_obj.currency_id and
                 pricelist_obj.currency_id.id):
                standard_currency_id = pricelist_obj.currency_id.id
        else:
            # Take standard price per unit directly from product
            product_model = self.pool.get('product.product')
            product_obj = product_model.browse(
                cr, uid, product_id, context=context)
            assert product_obj, _('No product found for id %d') % product_id
            assert field in product_obj, _(
                'Field %s not found in product') % field
            price_unit = product_obj[field]
            # If price_unit not taken from price-list, we still have to
            # take unit of measurement into account
            if  uom_id:
                uom_model = self.pool.get('product.uom')
                uom_obj = uom_model.browse(cr, uid, uom_id)
                p_uom_category_id = product_obj.uom_id.category_id.id
                if  p_uom_category_id == uom_obj.category_id.id:
                    price_unit = price_unit * uom_obj.factor_inv
            # When price not taken from pricelist, the currency is
            # determined by the price_type:
            price_type_model = self.pool.get('product.price.type')
            price_type_ids = price_type_model.search(
                cr, uid, [('field', '=', field)])
            if  price_type_ids:
                price_type_obj = price_type_model.browse(
                    cr, uid, price_type_ids[0])
                if  (price_type_obj and price_type_obj.currency_id and
                     price_type_obj.currency_id.id):
                    standard_currency_id = price_type_obj.currency_id.id
        # convert price_unit to currency of invoice
        if  standard_currency_id != currency_id:
            currency_model = self.pool.get('res.currency')
            price_unit = currency_model.compute(
                cr, uid, standard_currency_id, currency_id,
                price_unit, round=True, context=context)
        return price_unit, warning

    def Xinvoice_lineXuom_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id', False)
        context = dict(context)
        context.update({'company_id': company_id})
        warning = {}
        res = self.product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, address_invoice_id, currency_id, context=context)
        if 'uos_id' in res['value']:
            del res['value']['uos_id']
        if not uom:
            res['value']['price_unit'] = 0.0
        if product and uom:
            prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
            prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                warning = {
                    'title': _('Warning!'),
                    'message': _('You selected an Unit of Measure which is not compatible with the product.')
                    }
            return {'value': res['value'], 'warning': warning}
        return res




        # TODO
        # 'document_state': fields.related('invoice_id', 'state', type='selection', readonly=True, string="Invoice state",   help='The parent invoice state',
        #                                        selection=[('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('paid','Paid'),('cancel','Cancelled')],),
        # 'document_type': fields.related('invoice_id', 'type', type='selection', store=True, readonly=True, string="Invoice type", help='The parent invoice type',
        #                                        selection=[('out_invoice','Customer Invoice'),('in_invoice','Supplier Invoice'),('out_refund','Customer Refund'),('in_refund','Supplier Refund'),],),
        # 'document_user_id': fields.related('invoice_id','user_id',type='many2one',relation='res.users',string='Salesman', store=True),
        # 'document_date': fields.related('invoice_id','date_invoice',type='date',string='Invoice Date'),



        # Purchase 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Purchase Price')),
        # Sale 'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        # Sale 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Sale Price')),




"""TODO
            #new fields
           'ccurrency_price_subtotal': fields.function(_compute_amount_in_ccurrency,
             method=True, multi='currencyinvline', type='float', digits_compute=dp.get_precision('Account'),
             string='Subtotal in company currency', store={
            #'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit', 'quantity', 'discount', 'invoice_id'], 10),
            'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, None, 100),
            #'account.invoice': (_get_invoice_lines_from_invoices, ['move_id'], 200),
            'account.invoice': (_get_invoice_lines_from_invoices, None, 200),
            }),
        # In the trigger object for invalidation of these function fields,
        # why do I have accout.invoice -> move_id, and not 'res.currency.rate' ?
        # Answer : because, in the accounting entries, the computation of currency conversion
        # takes place when the accountings entries are created, i.e. when the invoice goes
        # from 'draft' to 'open'. It is not re-computed every time a new currency rate is
        # entered. So we want to compute the currency conversion simultaneously with the
        # accounting entries. That's why we trigger on move_id field on account.invoice.
        'ccurrency_price_unit': fields.function(_compute_amount_in_ccurrency, 
            method=True, multi='currencyinvline', type='float', digits_compute=dp.get_precision('Account'), 
            string='Unit price in company currency',
            store={ 
                   #'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit', 'quantity', 'discount', 'invoice_id'], 10),
                   'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, None, 100),
                   #'account.invoice': (_get_invoice_lines_from_invoices, ['move_id'], 200),
                   'account.invoice': (_get_invoice_lines_from_invoices, None, 200),
            }
"""

""" from product_historical_margin
        'subtotal_cost_price_company': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Cost',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The cost subtotal of the line at the time of the creation of the invoice, "
                                              "express in the company currency."),
        'subtotal_cost_price': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Cost in currency',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The cost subtotal of the line at the time of the creation of the invoice, "
                                              "express in the invoice currency."),
        'subtotal_company': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Net Sales',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The subtotal (VAT excluded) of the line at the time of the creation of the invoice, "
                                              "express in the company currency (computed with the rate at invoice creation time, as we "
                                              "don't have the cost price of the product at the date of the invoice)."),
        'margin_absolute': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Real Margin',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The Real Margin [ net sale - cost ] of the line."),
        'margin_relative': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Real Margin (%)',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The Real Margin % [ (Real Margin / net sale) * 100 ] of the line."
                                              "If no real margin set, will display 999.0 (if not invoiced yet for example)."),

        # Those field are here to better report to the user from where the margin is computed
        # this will allow him to understand why a margin is of that amount using the link
        # from product to invoice lines
        'invoice_state': fields.related('invoice_id', 'state', type='selection',
                                                selection=[
                                                    ('draft','Draft'),
                                                    ('proforma','Pro-forma'),
                                                    ('proforma2','Pro-forma'),
                                                    ('open','Open'),
                                                    ('paid','Paid'),
                                                    ('cancel','Cancelled')
                                                    ],
                                                readonly=True, string="Invoice state",
                                                help='The parent invoice state'),
        'invoice_type': fields.related('invoice_id', 'type', type='selection', store=True,
                                                selection=[
                                                    ('out_invoice','Customer Invoice'),
                                                    ('in_invoice','Supplier Invoice'),
                                                    ('out_refund','Customer Refund'),
                                                    ('in_refund','Supplier Refund'),
                                                    ],
                                                readonly=True, string="Invoice type",
                                                help='The parent invoice type'),
        'invoice_user_id': fields.related('invoice_id','user_id',type='many2one',relation='res.users',string='Salesman', store=True),
        'invoice_date': fields.related('invoice_id','date_invoice',type='date',string='Invoice Date'),
"""

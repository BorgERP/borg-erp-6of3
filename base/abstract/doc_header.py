# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Goran Kliska
#    mail:   goran.kliska AT slobodni-programi.hr
#    Copyright (C) 2012- Slobodni programi d.o.o., Zagreb, www.slobodni-programi.hr
#    Contributions:
# invoice_doppio_sconto Copyright (C) 2012 Andrea Cometa. All Rights Reserved.
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
# cc Company Currency fields
##############################################################################
#    Copyright (C) 2004-2011
#        Pexego Sistemas Informáticos. (http://pexego.es) All Rights Reserved
#        Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    account_invoice_currency module
##############################################################################
#    bi_invoice_company_currency module for OpenERP
#    Copyright (C) 2011 Akretion (http://www.akretion.com/) All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
##############################################################################
from openerp.osv import osv, fields, orm
import decimal_precision as dp
from tools.translate import _
import addons


class doc_header_mixin(osv.AbstractModel):
    _name = 'doc.header.mixin'

    def _auto_init(self, cr, context=None):
        res = super(doc_header_mixin, self)._auto_init(cr, context=context)
        f = addons.get_module_resource('abstract', 'sql', 'oe_line_calc_1.sql')
        sql = open(f).read()
        cr.execute(sql)
        return res

    _columns = {
        'entry_type': fields.selection([('price', 'Price'),  # Default
                                        ('amount', 'Value'),
                                        ('amount_tax', 'Value w tax'),
                                       ], 'Entry type',),
        'name_draft': fields.char('Draft No.', size=64,  # required=True,
            readonly=True, states={'draft': [('readonly', False)]}, select=True),

        'global_discount_percent': fields.float('Global discount', digits=(12, 2),
                                        help='Global discount applied as 3. discount on the document lines'),

        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position',
                                           readonly=True, states={'draft': [('readonly', False)]}),
        'currency_id': fields.many2one('res.currency', 'Currency',  # required=False,
                                        readonly=True, states={'draft':[('readonly', False)]}),
        'journal_id': fields.many2one('account.journal', 'Journal',  # required=False,
                                       readonly=True, states={'draft':[('readonly', False)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True,
                                      readonly=True, states={'draft':[('readonly', False)]}),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',
            help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Supplier Refund, otherwise a Partner bank account number.', readonly=True, states={'draft':[('readonly', False)]}),

        'payment_term': fields.many2one('account.payment.term', 'Payment Term',
                                        readonly=True, states={'draft': [('readonly', False)]},
                                        help="If you use payment terms, the due date will be computed automatically at the generation "\
                                             "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
                                             "The payment term may compute several due dates, for example 50% now, 50% in one month."),
        'list_amount': fields.float('List Amount', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),
        'discount_amount': fields.float('Discount Amount', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),
        # SO & PO
        # 'amount_tax' sum('account.tax').compute_all) # on invoice = sum(invoice.tax_line.amount) TODO for ALL
        # 'amount_untaxed' =sum(line.price_subtotal) # HMmmm to add amount_base for cases when tax is in price?
        # 'amount_total'='amount_untaxed' + 'amount_tax'
        'ccurrency_rate': fields.float('Force Exchange Rate', digits=(16, 8), required=False, readonly=True, states={'draft': [('readonly', False)]},
            help='The specific rate that will be used, in this invoice, between the selected invoice currency and the company currency.'),
        'ccurrency_amount_untaxed': fields.float('Untaxed', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),
        'ccurrency_amount_tax': fields.float('Tax', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),
        'ccurrency_amount_total': fields.float('Total', digits=(16, 8), readonly=True, digits_compute=dp.get_precision('Account')),

        'supplier_cost': fields.float('Supplier cost', readonly=True, help='Supplier Cost', digits_compute=dp.get_precision('Purchase Price'),),
        'landed_cost': fields.float('LC Total', readonly=True, help='Landed Costs in cc', digits_compute=dp.get_precision('Purchase Price'),),
        'total_cost': fields.float('Total costs', readonly=True, help='Total costs', digits_compute=dp.get_precision('Purchase Price'),),
        }

    _defaults = {'entry_type': 'price',
                 'name_draft': '/',
                 }

    def create(self, cr, uid, vals, context=None):
        if ('name_draft' not in vals) or (vals.get('name_draft') == '/'):
            if vals.get('name', '/') != '/':
                vals['name_draft'] = vals.get('name', '/')
                vals['name'] = '*' + vals['name_draft']  # TODO not all documents follow this *!
        new_id = super(doc_header_mixin, self).create(cr, uid, vals, context)
        self._calc_doc_vals(cr, uid, [new_id], context=context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(doc_header_mixin, self).write(cr, uid, ids, vals, context)
        self._calc_doc_vals(cr, uid, ids, context=context)
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        if ('name_draft' not in default) or (default.get('name_draft') == '/'):
            default['name_draft'] = default.get('name', '/')
        if ('name' not in default) or (default.get('name') == '/'):
            default['name'] = '*' + default['name_draft']
        return super(doc_header_mixin, self).copy(cr, uid, id, default, context=context)

    def _calc_doc_vals(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for id in ids:
            f_map = self.pool.get('product.mixin')._get_field_map(cr, uid)
            head_map = f_map[self._table]
            lines_obj = self.pool.get(head_map['lines_obj'])
            line_map = f_map[lines_obj._table]
            ccurrency = self.browse(cr, uid, [id])[0].company_id.currency_id.id
            curr_date = head_map['curr_date'][0]  # TODO
            # Update lines with header values, calc basic values up to supplier_cost
            sql_line_1 = """
               UPDATE %(line_table)s ln SET
                      --currency_id = h.currency_id
                      discount1_percent = r.r_discount1_percent
                     ,discount2_percent = r.r_discount2_percent
                     ,global_discount_percent = r.r_global_discount_percent
                     ,discount = r.r_discount
                     ,discount_amount = r.r_discount_amount
                     ,discount_total = r.r_discount_total
                     ,base_price = r.r_base_price
                     ,amount = r.r_amount
                     ,ccurrency_price_subtotal = r.r_ccurrency_price_subtotal
                     ,ccurrency_base_price = r.r_ccurrency_base_price
                     ,ccurrency_amount = r.r_ccurrency_amount
                     ,supplier_cost = r.r_supplier_cost
                 FROM %(head_table)s h
                     ,oe_line_calc_1(
                           ln.price_unit ::numeric
                          ,ln.quantity ::numeric
                          ,ln.discount1_percent ::numeric
                          ,ln.discount2_percent ::numeric
                          ,h.global_discount_percent ::numeric
                          ,ln.discount_amount ::numeric
                          ,'wholesale' --calc_type
                          ,h.currency_id::integer
                          ,h.company_id::integer
                          ,h.ccurrency_rate::numeric
                          --,h.currency_date::date
                      ) r
                WHERE h.id = ln.%(header_field)s
                  AND ln.%(header_field)s = %(doc_id)s
            """ % {'line_table': lines_obj._table,
                   'head_table': self._table,
                   'header_field': line_map['header_field'],
                   'doc_id': id,
                  }

            sql_head_1 = """
                WITH s AS (
                    SELECT
                         sum(discount_total) discount_amount
                        ,sum(round(cast(price_unit * quantity as numeric),2)) list_amount
                        ,sum(amount) amount
                        ,sum(ccurrency_price_subtotal) ccurrency_price_subtotal
                        ,sum(ccurrency_base_price) ccurrency_base_price
                        ,sum(ccurrency_amount) ccurrency_amount
                        ,sum(supplier_cost) supplier_cost
                     FROM %(line_table)s where %(header_field)s=%(doc_id)s
                )
                UPDATE %(head_table)s SET
                       discount_amount = s.discount_amount
                      ,list_amount = s.list_amount
                      ,amount_untaxed = s.amount -- base_amount
                      ,ccurrency_amount_untaxed = s.ccurrency_amount
                      ,ccurrency_amount_tax = oe_currency_compute(
                                               from_currency:=currency_id, to_currency:=%(ccurrency)s
                                              ,from_amount:= amount_tax
                                              ,company:=company_id, for_date:= coalesce(%(curr_date)s::date, now())::date )
                      ,supplier_cost = s.supplier_cost
                FROM s
                WHERE id=%(doc_id)s
            """ % {'line_table': lines_obj._table,
                   'head_table': self._table,
                   'header_field': line_map['header_field'],
                   'doc_id': id,
                   'curr_date': curr_date,
                   'ccurrency': ccurrency,
                  }

            # remove print
            print sql_line_1
            cr.execute(sql_line_1)
            print sql_head_1
            cr.execute(sql_head_1)

        return True





    ''' purchase_order
    'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Untaxed Amount',
        store={ 'purchase.order.line': (_get_order, None, 10),            }, multi="sums", help="The amount without tax"),
    'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Taxes',
        store={ 'purchase.order.line': (_get_order, None, 10),            }, multi="sums", help="The tax amount"),
    'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Total',
    '''
    ''' sale_order
        'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Sale Price'), string='Untaxed Amount',
            store = {'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10), 'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),            },
            multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Sale Price'), string='Taxes',
            store = { 'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Sale Price'), string='Total',
            store = {          'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),   },
            multi='sums', help="The total amount."),
    '''

    """ TODO
        'tax_line': fields.one2many('account.invoice.tax', 'invoice_id', 'Tax Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'check_total': fields.float('Verification Total', digits_compute=dp.get_precision('Account'), states={'open':[('readonly',True)],'close':[('readonly',True)]}),
    """


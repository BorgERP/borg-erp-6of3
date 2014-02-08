# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Slobodni Programi d.o.o. (<http://slobodni-programi.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import osv, fields
import netsvc
import pooler
from tools.translate import _
import decimal_precision as dp
from osv.orm import browse_record, browse_null
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class purchase_order(osv.Model):
    _name = 'purchase.order'
    _inherit = ['doc.header.mixin', 'purchase.order']
    _columns = {
            }
    _defaults = {
            }

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        if not partner_id:
            return {'value':{'partner_address_id': False, 'fiscal_position': False}}
        supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        pricelist = supplier.property_product_pricelist_purchase.id
        fiscal_position = supplier.property_account_position and supplier.property_account_position.id or False
        return {'value': {'partner_address_id': supplier_address['default'],
                          'pricelist_id': pricelist,
                          'fiscal_position': fiscal_position,
                          # TODO 'partner_bank_id': partner_bank_id,  # NEW!
                          # TODO 'payment_term': payment_term,  # NEW!
                          # TODO 'journal_id': journal_id,  # NEW!
                          # TODO 'global_discount_percent': global_discount,  # NEW!
                         }}


class purchase_order_line(osv.Model):
    _name = 'purchase.order.line'
    _inherit = ['doc.line.mixin', 'purchase.order.line']

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)  # NEW
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id,
                                        price,  # NEW
                                        line.product_qty)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal',
                                          digits_compute=dp.get_precision('Purchase Price'),
                                          store=True),  # NEW
        # Owerride doc_line_mixin
        'global_discount_percent': fields.related('order_id', 'global_discount_percent',
                                   string='Global discount',
                                   store=True, readonly=True, type='float',
                                   help='Discount from document header. Calculated as 3.discount percent'),

            }
    _defaults = {
            }

    def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, notes=False, context=None,
            list_price=False,  # NEW
            base_uom_coeff=False,  # NEW
            ):
        """
        onchange handler of product_uom.
            """
        if not uom_id:
            return {'value': {'price_unit': price_unit or 0.0,
                              'name': name or '', 'notes': notes or'',
                              'product_uom': uom_id or False,
                              'uom_id': uom_id or False,  # NEW!
                              'list_price': list_price or price_unit or 0.0,  # NEW!
                              'base_uom_id': False,  # NEW!
                              'base_uom_qty': False,  # NEW!
                              'base_uom_coeff': False,  # NEW!
                             }}
        return self.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, notes=notes, context=context)

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, notes=False, context=None,
            list_price=False,  # NEW
            base_uom_coeff=False,  # NEW
            ):

        """
        onchange handler of product_id.

        :param dict context: 'force_product_uom' key in context override
                             default onchange behaviour to force using the UoM
                             defined on the provided product
        """
        if context is None:
            context = {}

        res = {'value': {'price_unit': price_unit or 0.0,
                         'list_price': list_price or price_unit or 0.0,
                         'name': name or '',
                         'notes': notes or '',
                         'product_uom': uom_id or False,
                         'uom_id': uom_id or False,  # NEW!
                         }}
        if not product_id:
            return res

        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        # - check for the presence of partner_id and pricelist_id
        if not pricelist_id:
            raise osv.except_osv(_('No Pricelist !'), _('You have to select a pricelist or a supplier in the purchase form !\nPlease set one before choosing a product.'))
        if not partner_id:
            raise osv.except_osv(_('No Partner!'), _('You have to select a partner in the purchase form !\nPlease set one partner before choosing a product.'))

        # - determine name and notes based on product in partner lang.
        lang = res_partner.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        res['value'].update({'name': product.partner_ref, 'notes': notes or product.description_purchase})

        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id', '=', product.uom_id.category_id.id)],
                         'uom_id': [('category_id', '=', product.uom_id.category_id.id)]  # NEW!
                        }

        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id or context.get('force_product_uom'):
            uom_id = product_uom_po_id

        # NEW! start
        uom_ids = []
        if not product.uom_alternatives:
            # - set a domain on product_uom
            res['domain'] = {'product_uom': [('id', '=', product.uom_id.id)],
                             'uom_id': [('id', '=', product.uom_id.id)]  # NEW!
                            }
            # if product.uom_id != uom_id:
            #    res['warning'] = {'title': _('Warning'), 'message': _('Product does not allow Alternative UOMs')}
        elif len(product.uom_ids_domain) > 1:
            uom_ids = map(int, product.uom_ids_domain.split(','))
            uom_domain = [('id', 'in', uom_ids)]
            res['domain'] = {'product_uom': uom_domain,
                             'uom_id': uom_domain,  # NEW!
                            }
        # NEW! end
        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if not product.uom_id.category_id.id in uom_ids:
                # res['warning'] = {'title': _('Warning'), 'message': _('Selected UOM does not belong to the same category as the product UOM')}
                uom_id = product_uom_po_id

        res['value'].update({'product_uom': uom_id,
                             'uom_id': uom_id,  # NEW!
                           })

        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.date.context_today(cr, uid, context=context)

        qty = qty or 1.0
        supplierinfo = False
        supplierinfo_ids = product_supplierinfo.search(cr, uid, [('name', '=', partner_id), ('product_id', '=', product.id)])
        if supplierinfo_ids:
            supplierinfo = product_supplierinfo.browse(cr, uid, supplierinfo_ids[0], context=context)
            if supplierinfo.product_uom.id != uom_id:
                res['warning'] = {'title': _('Warning'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
            min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
            if qty < min_qty:  # If the supplier quantity is greater than entered from user, set minimal.
                res['warning'] = {'title': _('Warning'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                qty = min_qty

        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        res['value'].update({'date_planned': date_planned or dt,
                             'product_qty': qty,
                             'quantity': qty,  # NEW!
                            })

        res['value'].update(self._get_base_uom_qty(cr, uid, product_id,
                                     uom_id, qty, base_uom_coeff, context=context))  # NEW!

        # - determine price_unit and taxes_id
        price = product_pricelist.price_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id, {'uom': uom_id, 'date': date_order})[pricelist_id]

        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        a = product.product_tmpl_id.property_account_expense.id
        if not a:
            a = product.categ_id.property_account_expense_categ.id
        a = account_fiscal_position.map_account(cr, uid, fpos, a)
        taxes = product.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids)
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price,
                             'list_price': price,  # NEW!
                             'taxes_id': taxes_ids,
                             })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

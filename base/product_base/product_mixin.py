# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Goran Kliska
#    mail:   goran.kliska AT slobodni-programi.hr
#    Copyright (C) 2012- Slobodni programi d.o.o., Zagreb, www.slobodni-programi.hr
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


class product_mixin(orm.AbstractModel):
    _name = 'product.mixin'

    _columns = {
            'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=False,),  # TODO required=True
            'quantity': fields.float('Quantity', required=False, help='Quantity in UOM'),  # TODO required=True

            'base_uom_id': fields.related('product_id', 'uom_id', type='many2one',
                                          relation='product.uom',
                                          string='Base UOM',
                                          required=True, readonly=True),
            'base_uom_coeff': fields.float('Unit of Measure Coefficient', digits=(12, 12),
                                            help='Coefficient used to convert Unit of Measure into Base Unit of Measure'
                                            ' uos = uom * coeff'),
            'base_uom_qty': fields.float('Base UOM Quantity',
                                         # readonly=True,  #function
                                         digits_compute=dp.get_precision('Product UoS'),
                                         help='Quantity in the base UoM of the product'),

            # document line fields UOM
            # 'product_id': fields.many2one('product.product', 'Product', select=True,),
            #
            #
    }

    def create(self, cr, uid, vals, context=None):
        ''' Overide to set base product uom '''
        if not context:
            context = {}
        self._get_base_uom_vals(cr, uid, False, vals, context=context)
        return super(product_mixin, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        ''' Overide to set base product uom '''
        if not context:
            context = {}
        field_map = self._get_field_map(cr, uid).get(self._table, False)
        flds = field_map['uom'] + field_map['qty']
        if any(f in vals for f in flds):
            for id in ids:
                self._get_base_uom_vals(cr, uid, id, vals, context=context)
        return super(product_mixin, self).write(cr, uid, ids, vals, context)


    def _get_base_uom(self, cr, uid, id, product_id, uom_id, context=None):
        product = self.pool.get('product.product').browse(cr, uid, id, [product_id])[0]
        return product.uom_id

    def _get_base_uom_qty(self, cr, uid, product_id, doc_uom_id,
                          doc_qty=0.0, uom_coeff=False, context=None):
        # base_uom = self._get_base_uom(cr, uid, id, product_id, uom_id, context=context)
        product = self.pool.get('product.product').browse(cr, uid, [product_id])[0]
        base_uom_coeff = 1.0
        base_uom_qty = doc_qty
        base_uom_id = product.uom_id.id
        if base_uom_id != doc_uom_id:
            if product.mes_type == 'variable' and uom_coeff:
                base_uom_coeff = uom_coeff
                base_uom_qty = doc_qty * base_uom_coeff
            else:
                base_uom_qty = self.pool.get('product.uom')._compute_qty(cr, uid,
                                  doc_uom_id, doc_qty, base_uom_id, product_id=product_id)
                base_uom_coeff = doc_qty / base_uom_qty
        return {'base_uom_id': base_uom_id,
                'base_uom_qty': base_uom_qty,
                'base_uom_coeff': base_uom_coeff,
                }

    def _get_field_map(self, cr, uid, context=None):
        return {
                'sale_order': {
                    'lines_field': 'order_line',
                    'lines_obj': 'sale.order.line',
                    'curr_date': ['date_order', 'now'],
                    'date': ['date_order'],
                    },
                'sale_order_line': {
                    'uom': ['uom_id', 'product_uom', 'product_uos'],
                    'qty': ['quantity', 'product_uom_qty', 'product_uos_qty'],
                    'price': ['price_unit', ],
                    'header_field': 'order_id',
                    },
                'purchase_order': {
                    'lines_field': 'order_line',
                    'lines_obj': 'purchase.order.line',
                    'curr_date': ['date_order', 'now'],
                    },
                'purchase_order_line': {
                    'uom': ['uom_id', 'product_uom'],
                    'qty': ['quantity', 'product_qty'],
                    'price': ['price_unit', ],
                    'header_field': 'order_id',
                    },
                'stock_picking': {
                    'lines_field': 'move_lines',
                    'lines_obj': 'stock.move',
                    'curr_date': ['date', 'now'],
                    },
                'stock_move': {
                    'uom': ['uom_id', 'product_uom', 'product_uos'],
                    'qty': ['quantity', 'product_uom_qty', 'product_uos_qty'],
                    'price': ['price_unit', ],
                    'currency': ['price_currency_id', ],
                    'base_uom_qty': ['product_qty', ],
                    'other': ['remaining_qty', 'unassigned_qty'],
                    'header_field': 'picking_id',
                    },
                'account_invoice': {
                    'lines_field': 'invoice_line',
                    'lines_obj': 'account.invoice.line',
                    'curr_date': ['date_invoice', 'now'],
                    },
                'account_invoice_line': {
                    'uom': ['uom_id', 'uos_id', ],
                    'qty': ['quantity', ],
                    'price': ['price_unit', ],
                    'header_field': 'invoice_id',
                    },



                'procurement_order': {
                    'uom': ['uom_id', 'product_uom', 'product_uos'],
                    'qty': ['quantity', 'product_qty', 'product_uos_qty'],
                    },
                'stock_warehouse_orderpoint': {
                    'uom': ['uom_id', 'product_uom'],
                    'other': ['product_min_qty', 'product_max_qty'],
                    },
                'product_supplierinfo': {
                    'uom': ['uom_id', 'product_uom'],
                    'other': ['qty', 'min_qty'],
                    },
                'stock_inventory_line': {
                    'uom': ['uom_id', 'product_uom'],
                    'qty': ['quantity', 'product_qty'],
                    'price': ['force_price_unit', ],
                    'other': ['th_qty'],
                    },
                'account_move_line': {
                    'uom': ['uom_id', 'product_uom_id'],
                    'qty': ['quantity', 'debit_qty', 'credit_qty'],
                    'value': ['debit', 'credit'],
                    'currency': ['currency_id', ],
                    },
                'account_analytic_line': {
                    'uom': ['uom_id', 'product_uom_id'],
                    'qty': ['quantity', 'unit_amount'],
                    'value': ['amount', 'amount_currency'],
                    'currency': ['currency_id', ],
                                          },
                }

    def _get_base_uom_vals(self, cr, uid, id, vals, context=None):
        ''' Update vals from onchange, create/write methods
            1. Make document uom/uos fields the same (first found wins)
            2. Calc/Write base_uom_* fields
        '''
        # vals from write don't have all data
        row = id and self.browse(cr, uid, [id], context=context)[0] or False
        product_id = vals.get('product_id', False) or (row and row.product_id and row.product_id.id) or False
        field_map = self._get_field_map(cr, uid).get(self._table, False)
        if not (field_map and vals.get('product_id', False)):
            return vals
        product = self.pool.get('product.product').browse(cr, uid, [product_id])[0]
        # get first document uom/qty
        doc_uom_id = False
        doc_qty = 0
        # doc_uom_id = vals.get('uom_id') or (row and row['uom_id'].id) or False
        # doc_qty = vals.get('quantity') or (row and row['quantity']) or doc_qty
        if not doc_uom_id:
            for i in range(0, len(field_map['uom'])):
                uom_fld = field_map['uom'][i]
                qty_fld = field_map['qty'][i]
                doc_uom_id = vals.get(uom_fld) or (row and row[uom_fld].id) or False
                doc_qty = vals.get(qty_fld) or (row and row[qty_fld]) or doc_qty
                if doc_uom_id:
                    break
        doc_uom_id = doc_uom_id or product.uom_id.id
        # all document uom/uos and qty's equal
        for i in range(0, len(field_map['uom'])):
            uom_fld = field_map['uom'][i]
            qty_fld = field_map['qty'][i]
            vals[uom_fld] = doc_uom_id
            vals[qty_fld] = doc_qty

        base_uom_coeff = 1.0
        base_uom_qty = doc_qty
        base_uom_id = product.uom_id.id
        if base_uom_id != doc_uom_id:
            if product.mes_type == 'variable' and vals.get('base_uom_coeff', False):
                base_uom_coeff = vals.get('base_uom_coeff')
                base_uom_qty = doc_qty * base_uom_coeff
            else:
                base_uom_qty = self.pool.get('product.uom')._compute_qty(cr, uid,
                                  doc_uom_id, doc_qty, base_uom_id, product_id=product_id)
                base_uom_coeff = doc_qty / base_uom_qty
        vals['base_uom_coeff'] = base_uom_coeff
        vals['base_uom_qty'] = base_uom_qty
        vals['base_uom_id'] = base_uom_id
        return vals

    # WIP


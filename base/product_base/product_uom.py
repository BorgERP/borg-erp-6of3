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
from openerp.osv import osv, fields
import decimal_precision as dp
from tools.translate import _

def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r


class product_uom_alternative(osv.Model):
    _name = 'product.uom.alternative'
    _description = 'Alternative Units of Measure'
    _rec_name = 'alt_uom_id'

    def _compute_factor_inv(self, factor):
        return factor and (1.0 / factor) or 0.0

    def _factor_inv(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for uom in self.browse(cursor, user, ids, context=context):
            res[uom.id] = self._compute_factor_inv(uom.factor)
        return res

    def create(self, cr, uid, data, context=None):
        if 'factor_inv' in data:
            if data['factor_inv'] != 1 and data['factor_inv'] != 0:
                data['factor'] = self._compute_factor_inv(data['factor_inv'])
            del(data['factor_inv'])
        return super(product_uom_alternative, self).create(cr, uid, data, context)

    def _factor_inv_write(self, cursor, user, id, name, value, arg, context=None):
        return self.write(cursor, user, id, {'factor': self._compute_factor_inv(value)}, context=context)

    _columns = {
        'product_id': fields.many2one('product.template', 'Product', required=True, select=True,),
        'alt_uom_id': fields.many2one('product.uom', 'Alternative UOM', required=True,
                          help="Alternative UOM."),
        'factor': fields.float('Ratio', required=True, digits=(12, 12),
            help='How much bigger or smaller this unit is compared to the reference Unit of Measure for this category:\n'\
                    '1 * (reference unit) = ratio * (this unit)'),
        'factor_inv': fields.function(_factor_inv, digits=(12, 12),
            fnct_inv=_factor_inv_write,  # readonly=True,
            string='Bigger Ratio',
            help='How many times this Unit of Measure is bigger than the reference Unit of Measure in this category:\n'\
                    '1 * (this unit) = ratio * (reference unit)', required=True),
        'rounding': fields.float('Rounding Precision', digits_compute=dp.get_precision('Product Unit of Measure'), required=True,
            help="The computed quantity will be a multiple of this value. "\
                 "Use 1.0 for a Unit of Measure that cannot be further split, such as a piece."),
        'active': fields.boolean('Active', help="By unchecking the active field you can disable a unit of measure without deleting it."),
        # NOT IMPLEMENTED!
        'mes_type': fields.selection((('fixed', 'Fixed'), ('variable', 'Variable')), 'Measure Type'),
        'category_id': fields.related('alt_uom_id', 'category_id', type='many2one',
                                      relation='product.uom.categ', string='UoM Category', readonly=True),
        'all_from_category': fields.boolean('All category UOMs', help="Use all UOMs from this category"),
    }

    _defaults = {'active': True,
                 'rounding': 0.01,
                 'all_from_category': False,
                 'mes_type': 'fixed',
                 }

    _sql_constraints = [
        ('factor_not_zero', 'CHECK (factor>0)', 'The conversion ratio for a unit of measure cannot be 0!')
    ]


class product_uom(osv.Model):
    _inherit = 'product.uom'

    def _compute_qty(self, cr, uid, from_uom_id, qty, to_uom_id=False, round=True,
                     product_id=False, context=None):  # add product_id and context
        if context is None:
            context = {}
        product_id = product_id or context.get('product_id', False)
        if not from_uom_id or not qty or not to_uom_id:
            return qty
        uoms = self.browse(cr, uid, [from_uom_id, to_uom_id])
        if uoms[0].id == from_uom_id:
            from_unit, to_unit = uoms[0], uoms[-1]
        else:
            from_unit, to_unit = uoms[-1], uoms[0]
        return self._compute_qty_obj(cr, uid, from_unit, qty, to_unit, round=round,
                                     product_id=product_id, context=context)  # add product_id and context

    def _compute_qty_obj(self, cr, uid, from_unit, qty, to_unit, round=True,
                         product_id=False, context=None):
        if context is None:
            context = {}
        product_id = product_id or context.get('product_id', False)

        if from_unit.category_id.id != to_unit.category_id.id:
            return self._compute_alt_qty_obj(cr, uid, from_unit, qty, to_unit, round,
                                             product_id, context=context)
        amount = qty / from_unit.factor
        if to_unit:
            amount = amount * to_unit.factor
            if round:
                amount = rounding(amount, to_unit.rounding)
        return amount

    def _compute_alt_qty_obj(self, cr, uid, from_unit, amount, to_unit, round=True,
                         product_id=False, context=None):
        """ If From_UoM != To_UoM check uom.alternatives of product
        """
        if context is None:
            context = {}
        product_id = product_id or context.get('product_id', False)
        alt_obj = self.pool.get('product.uom.alternative')
        if not (product_id and from_unit and to_unit):
            return amount
        alt_ids = product_id and alt_obj.search(cr, uid,
                                 [('product_id', '=', product_id),
                                  ('alt_uom_id', 'in', [from_unit.id, to_unit.id])]) or False
        if not alt_ids:
            if context.get('raise-exception', True):
                raise osv.except_osv(_('Error!'), _('Conversion from UoM %s to UoM %s is not possible as they belong to different Category!.') % (from_unit.name, to_unit.name,))
            else:
                return amount
        alt_uom = alt_obj.browse(cr, uid, alt_ids[0], context=context)
        if to_unit.id == alt_uom.product_id.uom_id.id:
            factor = alt_uom.factor
        elif from_unit.id == alt_uom.product_id.uom_id.id:
            factor = alt_uom.factor_inv
        else:
            if context.get('raise-exception', True):
                raise osv.except_osv(_('Error!'), _('Conversion from UoM %s to UoM %s is not defined in alternative UoMs!.') % (from_unit.name, to_unit.name,))
            else:
                return amount
        amount = amount * factor
        if round:
            amount = rounding(amount, alt_uom.rounding)
        return amount

    def _compute_price(self, cr, uid, from_uom_id, price, to_uom_id=False,
                       product_id=False, context=None):
        if context is None:
            context = {}
        product_id = product_id or context.get('product_id', False)
        if not from_uom_id or not price or not to_uom_id:
            return price
        uoms = self.browse(cr, uid, [from_uom_id, to_uom_id])
        if uoms[0].id == from_uom_id:
            from_unit, to_unit = uoms[0], uoms[-1]
        else:
            from_unit, to_unit = uoms[-1], uoms[0]
        if from_unit.category_id.id != to_unit.category_id.id:
            # original: return price
            return self._compute_alt_qty_obj(cr, uid, from_unit, price, to_unit, round,
                                 product_id, context={'raise-exception': False})
        amount = price * from_unit.factor
        if to_uom_id:
            amount = amount / to_unit.factor
        return amount


class product_template(osv.Model):
    _inherit = "product.template"

    _columns = {
        # original fields
        'volume': fields.float('Volume', help="The volume in m3."),
        'weight': fields.float('Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The gross weight in Kg."),
        'weight_net': fields.float('Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),

        'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True,
                                  help="Default Unit of Measure used for all operations."),
        'uom_po_id': fields.many2one('product.uom', 'Purchase Unit of Measure', required=True,
                                     domain="[('id', 'in', uom_ids_domain)]",
                                     help="Default Unit of Measure used for purchase operations."),
        'mes_type': fields.selection((('fixed', 'Fixed'), ('variable', 'Variable')), 'Measure Type'),
        # new fields
        'uom_alternatives': fields.boolean('Alternative UOMs', help="Use Alternative UOMs for this product"),
        'uom_so_id': fields.many2one('product.uom', 'Sales Unit of Measure', required=False,
                                     domain="[('id', 'in', uom_ids_domain)]",
                                     help="Default Unit of Measure in sales operations."),

        'uom_alternative_ids': fields.one2many('product.uom.alternative', 'product_id', string='Alternative Units of Measure'),
        # Dummy :(
        'uom_ids_domain': fields.text('Valid Units of Measure', help='Technical fields representing domain for Valid UOMs as coma delimited string '),

        # TODO, not in use yet!!!
        # 'weight_uom_id': fields.many2one('product.uom', 'Sales Unit of Measure', required=False,
        #                 default 'kg'            domain="[('category', '=', 'Weight')]",
        # 'volume_uom_id': fields.many2one('product.uom', 'Sales Unit of Measure', required=False,
        #                 default 'm2'            domain="[('category', '=', 'volume')]",

        # Depreciate
        'uos_id': fields.many2one('product.uom', 'Unit of Sale',
            help='Specify a unit of measure here if invoicing is made in another unit of measure than inventory. Keep empty to use the default unit of measure.'),
        'uos_coeff': fields.float('Unit of Measure -> UOS Coeff', digits_compute=dp.get_precision('Product UoS'),
            help='Coefficient to convert default Unit of Measure to Unit of Sale\n'
            ' uos = uom * coeff'),
    }

    _defaults = {'uom_alternatives': False,
                 }

    def _check_uom(self, cursor, user, ids, context=None):
        for product in self.browse(cursor, user, ids, context=context):
            if product.uom_po_id.id != product.uom_id.id and \
                product.uom_po_id.id not in map(int, product.uom_ids_domain.split(',')):
                return False
            if product.uom_so_id and product.uom_so_id.id != product.uom_id.id and \
                product.uom_po_id.id not in map(int, product.uom_ids_domain.split(',')):
                return False
        return True

    def _check_uos(self, cursor, user, ids, context=None):
        """ UOS == UOM until depreciated """
        for product in self.browse(cursor, user, ids, context=context):
            if product.uos_id and product.uos_id.id != product.uom_id.id:
                return False
        return True

    _constraints = [
        (_check_uom, 'Error: The default UOM and the purchase UOM must be in the same category.', ['uom_id']),
    ]

    def _get_valid_uom_ids(self, cr, uid, id, uom_id,
                     uom_alternatives=False, uom_alternative_ids=[],
                     context=None, from_update=False):
        uom_ids = []
        if uom_id:
            uom_brw = self.pool.get('product.uom').browse(cr, uid, [uom_id])[0]
            cr.execute('''SELECT pu.id FROM product_uom AS pu
                           WHERE pu.category_id = %s''',
                        (uom_brw.category_id.id,))
            uom_ids = [item[0] for item in cr.fetchall()]
            if uom_alternatives and isinstance(uom_alternative_ids, (list,)) and not from_update:
                for alt_uom in self.resolve_2many_commands(cr, uid, 'uom_alternative_ids',
                                   uom_alternative_ids, fields=['alt_uom_id'], context=context):
                    if isinstance(alt_uom.get('alt_uom_id', 0), (int, long)):
                        uom_ids.append(alt_uom.get('alt_uom_id', 0))
                    else:
                        uom_ids.append(alt_uom.get('alt_uom_id', 0)[0])
            elif uom_alternatives:  # browse_list_object from update
                for uom_alternative_id in uom_alternative_ids:
                    uom_ids.append(uom_alternative_id.alt_uom_id.id)
        return uom_ids

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        uom_ids_domain = self._get_valid_uom_ids(cr, uid, id,
                                uom_id=vals.get('uom_id', False),
                                uom_alternatives=vals.get('uom_alternatives', False),
                                uom_alternative_ids=vals.get('uom_alternative_ids', False),
                                context=context)
        vals['uom_ids_domain'] = str(uom_ids_domain)[1:-1]
        if 'uom_alternatives' in vals and not vals['uom_alternatives']:
            # read-only fields are not sent from client
            vals['uom_po_id'] = vals['uom_id']
            vals['uom_so_id'] = vals['uom_id']
        return super(product_template, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        if 'uom_alternatives' in vals and not vals['uom_alternatives']:
            # read-only fields are not sent from client
            uom_id = vals.get('uom_id', False) or self.browse(cr, uid, ids)[0].uom_id.id
            vals['uom_po_id'] = uom_id
            vals['uom_so_id'] = uom_id
        res = super(osv.Model, self).write(cr, uid, ids, vals, context=context)
        if any(f in vals for f in ['uom_alternatives', 'uom_id', 'uom_alternative_ids']):
            for product in self.browse(cr, uid, ids, context=context):
                uom_ids_domain = self._get_valid_uom_ids(cr, uid, id,
                                 uom_id=vals.get('uom_id', False) or product.uom_id.id,
                                 uom_alternatives=vals.get('uom_alternatives', False) or product.uom_alternatives,
                                 uom_alternative_ids=product.uom_alternative_ids,
                                 from_update=True,
                                 context=context)
                if str(uom_ids_domain)[1:-1] != product.uom_ids_domain:
                    self.write(cr, uid, [product.id],
                               {'uom_ids_domain': str(uom_ids_domain)[1:-1]},
                               context=None)
        return res

    def onchange_uom(self, cursor, user, ids, uom_id, uom_po_id):
        if uom_id:
            return {'value': {'uom_po_id': uom_id, 'uom_so_id': uom_id, }
                    }
        return {}

    def _check_uom(self, cursor, user, ids, context=None):
        return True
        # for product in self.browse(cursor, user, ids, context=context):
        #    if product.uom_id.category_id.id != product.uom_po_id.category_id.id:
        #        return False
        # return True


class product_product(osv.Model):
    _inherit = 'product.product'

    def _get_valid_uom_ids(self, cr, uid, id, uom_id,
                     uom_alternatives=False, uom_alternative_ids=[],
                     context=None):
        return self.pool.get('product.template')._get_valid_uom_ids(cr, uid, id, uom_id,
                     uom_alternatives=uom_alternatives, uom_alternative_ids=uom_alternative_ids,
                     context=context)

    def onchange_uom(self, cursor, user, ids, uom_id, uom_po_id, uom_so_id,
                     uom_alternatives=False, uom_alternative_ids=[], context=None):
        value = {}
        d = []
        if uom_id:
            value = {'uom_po_id': uom_id, 'uom_so_id': uom_id, }
            if uom_alternatives:
                ids = [0, ]
                for alt_uom in self.resolve_2many_commands(cursor, user, 'uom_alternative_ids',
                                   uom_alternative_ids, fields=['alt_uom_id'], context=context):
                    if isinstance(alt_uom.get('alt_uom_id', 0), (int, long)):
                        ids.append(alt_uom.get('alt_uom_id', 0))
                    else:
                        ids.append(alt_uom.get('alt_uom_id', 0)[0])
                uom_brw = self.pool.get('product.uom').browse(cursor, user, [uom_id])[0]
                d = ['|', ('category_id', '=', uom_brw.category_id.id), ('id', 'in', ids)]
        return {'value': value,
                'domain': {'uom_po_id': d, 'uom_so_id': d, }, }

    def onchange_uom_alternative_ids(self, cr, uid, ids, uom_id,
                     uom_alternatives=False, uom_alternative_ids=[], context=None):
        d = []
        if uom_id and uom_alternatives:
            ids = [0, ]
            for alt_uom in self.resolve_2many_commands(cr, uid, 'uom_alternative_ids',
                               uom_alternative_ids, fields=['alt_uom_id'], context=context):
                if isinstance(alt_uom.get('alt_uom_id', 0), (int, long)):
                    ids.append(alt_uom.get('alt_uom_id', 0))
                else:
                    ids.append(alt_uom.get('alt_uom_id', 0)[0])
            uom_brw = self.pool.get('product.uom').browse(cr, uid, [uom_id])[0]
            d = ['|', ('category_id', '=', uom_brw.category_id.id), ('id', 'in', ids)]
        return {'domain': {'uom_po_id': d, 'uom_so_id': d, }, }


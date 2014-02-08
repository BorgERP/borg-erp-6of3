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
{
    'name': 'Product base with mixins',
    'version': '6.3.1',
    'category': 'Base/Borg',
    'author': 'Decodio, Slobodni programi d.o.o.',
    'website': 'http://www.slobodni-programi.hr',
    'depends': [
        'base_base',  # not directly
        'product',
        ],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'product_view.xml',
        ],
    # 'active': False,
    'installable': True,
#    'auto_install': True,
    'description': '''
     Product
         Depreciates: UOS(uos_id and uos_coeff).
         New:
             + Alternative UOMs: 
                 - when False only default UOM is used for a product
                 - when True allows UOMs from same UOM Category as base UOM
                   and allows entering Alternative Units of Measure
             + Sales Unit of Measure as default for sales operations (like Purchase Unit of Measure)
             + Alternative Units of Measure per Product
               TODO: add Usage selection 'both', 'sale', 'purchase'
               TODO: implement 'variable' 'Measure Type'
     Product Mixin
         Abstract class designed for document lines with product and uom.
         Depreciates: UOS on document lines, but keeps compatibility making UOS == UOM
         Document lines: Sale Order line, Stock move, Invoice line, PO line ...
         New:
             + Base UOM          (base_uom_id: fields.related, not stored?)
             + Base UOM Quantity (base_uom_qty: fields.float, calculated on change and create/write)
             + UOM Coefficient   (base_uom_coeff: fields.float, calculated on change and create/write
                                                  for for Measure Type = 'fixed', TOOD variable)

    ''',
}

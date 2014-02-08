# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Decodio / Slobodni Programi d.o.o. (<http://slobodni-programi.com>).
#    Author: Goran Kliska
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


{
    'name': 'Web Base',
    'version': '6.3.1.0',
    'category': 'Base/Borg',
    'complexity': "normal",
    "depends": [
        # 'base_base',
        'web',
    ],
    "js": [
        'static/src/js/view_form_base.js',
        # 'static/src/js/view_list_base.js',
    ],
    'qweb': [
        # 'static/xml/*.xml',
    ],
    'css': [
        # 'static/css/*.css',
    ],
    'author': 'Decodio - Slobodni programi d.o.o.',
    'website': 'http://slobodni-programi.com',
    'installable' : True,
    'active' : False,
    'auto_install': True,
    'description':
    """
    1. Fixing Wishlist: Fields with attribute readonly=True do not preserve on_change values
         https://bugs.launchpad.net/openerp-web/+bug/378824 Reported by Ferdinand on 2009-05-20
         If field is (readonly and required and dirty) then it is "readonly_writable". 3 LOC
         Example:
                 <field name="uom_id"  on_change="onchange_product_uom( ...
                 <field name="base_uom_qty" readonly="1" required="1"/>
                 Method onchange_product_uom(...) is calculating and changing value of
                 "base_uom_qty" field and making it "dirty". 
                 Field is readonly and required and it will be saved in the client dataset
                 and sent to orm create and write methods.
                 It is good practice to recalculate all important fields again in create and write methods.

    2. Allowing parent.field for in attrs 
         Example: <field name="amount" attrs="{'readonly':[('parent.entry_type','!=','amount')],'required':[('parent.entry_type','!=','amount')]}"/>
    """,
    'data': [],
    'demo_xml': [],
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

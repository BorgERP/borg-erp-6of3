# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Slobodni Programi d.o.o. (<http://slobodni-programi.com>).
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
    'name': 'Purchase Base',
    'version': '6.3.1.0',
    'category': 'Base/Borg',
    'complexity': "normal",
    'author': 'Slobodni Programi d.o.o.',
    'website': 'http://slobodni-programi.com',
    'depends': [
                'abstract',
                'purchase',
                ],
    'data': [
                  'purchase_view.xml'
                   ],
    'demo_xml': [],
    'installable': True,
    # 'auto_install': True,
    'images': [],
    'description':
    """
    Adds abstract doc_header and line

    """,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

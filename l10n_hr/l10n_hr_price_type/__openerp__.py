# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_price_type
#    Copyright (C) 2013- Slobodni programi d.o.o., Zagreb
#    Contributions:
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
    "name": "Change Price Type Currency",
    "description": """
Croatian localisation.
======================

Author:
        http://www.slobodni-programi.hr


Description:
        Change currency on produtc price type to HRK

""",
    "version": "1.0",
    "author": "Slobodni Programi d.o.o.",
    "category": 'Localization',
    "website": "http://www.slobodni-programi.hr",

    'depends': [
                'product',
                'l10n_hr_base',
                ],
    'data': [
                'l10n_hr_price_type.xml',
            ],
    "demo": [],
    'test': [],
    "installable": True,
    "auto_install": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

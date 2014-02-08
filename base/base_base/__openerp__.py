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
    'name': 'Base Base',
    'version': '6.3.1.0',
    'category': 'Base/Borg',
    'complexity': "normal",
    'author': 'Slobodni Programi d.o.o.',
    'website': 'http://slobodni-programi.com',
    'depends': [
        "base",
        "decimal_precision_base",
    ],
    # 'init_xml': [],
    "data": [
        "security/base_security.xml",
        "security/ir.model.access.csv",

        "ir/ir_config_parameter_view.xml",
        "ir/ir_cron_view.xml",

        "res/data/res_currency_rate_type.xml",
        "res/data/res_currency_data.xml",

        "res/res_currency_view.xml",
        "res/res_currency_rate_update_view.xml",
        "res/res_company_view.xml",
        "res/res_bank_view.xml",
        "res/wizard/res_currency_rate_update_wizard.xml",
    ],
    'demo_xml': [],
    'installable': True,
    # 'auto_install': True,
    'images': [],
    'description':
    """
Includes modules:
    ir_config_parameter_viewer: Author Nicolas Bessi, Camptocamp SA
        Create view to inspect/change technical parameters
    cron_run_manually:  Author Therp BV
        This module adds a button to the cron scheduled task form in OpenERP
        that allows the administrator to run the job immediately, independently
        of the scheduler.
    currency_rate_update: Author:
    """,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: 
#    mail:   
#    Copyright: 
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
    "name" : "Croatia - vat special",
    "description" : """
Croatian localisation.
======================

Author: 
Contributions: 

Description:
PDV obrazac , Knjiga ura/ira

""",
    "version" : "1",
    "author" : "Croatian community",
    "category" : "Localisation/Croatia",
    "website": "https://launchpad.net/openobject-croatia",

    'depends': [
                'account_tax_payment',
                'base_vat',
                'base_iban',
                #'account_chart',
                'l10n_hr_base',
                ],
    'init_xml': [],
    'update_xml': [
                'security/ir.model.access.csv',
                'account_view.xml',
                'pdv_knjiga_view.xml',
                'pdv_config_view.xml',
                'wizard/wizard_pdv_obrazac_view.xml',
                'wizard/wizard_pdv_knjiga_view.xml',
                #'data/l10n_hr_pdv.knjiga.csv',  #import manualy or new module
                #'data/l10n_hr_pdv.report.obrazac.csv', #fails on mc now on Verso HR 
                #'data/l10n_hr_pdv.report.knjiga.csv', #import manualy or new module  
                   ],
    "demo_xml" : [],
    'test' : [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

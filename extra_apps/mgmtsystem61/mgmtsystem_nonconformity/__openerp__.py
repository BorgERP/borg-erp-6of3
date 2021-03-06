# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
    "name" : "Management System - Nonconformity",
    "version" : "1.0",
    "author" : "Savoir-faire Linux",
    "website" : "http://www.savoirfairelinux.com",
    "license" : "AGPL-3",
    "category" : "Management System",
    "description": """\
This module enables you to manage the nonconformities of your management 
system : quality (ISO9001), environment (ISO14001) or security (ISO27001).	

WARNING: when upgrading from v0.1, data conversion is required, since there are subtancial changes to the data structure.
    """,
    "depends" : [
        'mgmtsystem_action',
        'wiki_procedure',
    ],
    "data" : [
        'security/ir.model.access.csv',
        'mgmtsystem_nonconformity.xml',
        'mgmtsystem_nonconformity_workflow.xml',
        'nonconformity_sequence.xml',
        'board_mgmtsystem_nonconformity.xml',
        'mgmtsystem_nonconformity_data.xml',
    ],
    "demo" : [
        'demo_nonconformity.xml',
    ],
    "installable" : True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


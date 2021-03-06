# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.techreceptives.com>)
#    Special Credit and Thanks to Thymbra Latinoamericana S.A.
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
#/#############################################################################
from osv import osv
from osv import fields


class OeMedicalMedicament(osv.osv):
    _name = 'oemedical.medicament'

    _columns = {
        'name': fields.char(string='Name', size=264, required=True),
        'category': fields.many2one('oemedical.medicament.category',
                                    'Category',select=True),
        'indications': fields.text(string='Indication', help='Indications'),
        'therapeutic_action': fields.char(size=256,
                                          string='Therapeutic effect', 
                                          help='Therapeutic action'),
        'product': fields.many2one('product.product', string='Product', 
                                   help='Product Name'),
        'pregnancy_category': fields.selection([
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
            ('X', 'X'),
            ('N', 'N'),
            ], string='Pregnancy Category', 
            help='** FDA Pregancy Categories ***\n'\
        'CATEGORY A :Adequate and well-controlled human studies have failed'\
        ' to demonstrate a risk to the fetus in the first trimester of'\
        ' pregnancy (and there is no evidence of risk in later'\
        ' trimesters).\n\n'\
        'CATEGORY B : Animal reproduction studies have failed todemonstrate a'\
        ' risk to the fetus and there are no adequate and well-controlled'\
        ' studies in pregnant women OR Animal studies have shown an adverse'\
        ' effect, but adequate and well-controlled studies in pregnant women'\
        ' have failed to demonstrate a risk to the fetus in any'\
        ' trimester.\n\n'
        'CATEGORY C : Animal reproduction studies have shown an adverse'\
        ' effect on the fetus and there are no adequate and well-controlled'\
        ' studies in humans, but potential benefits may warrant use of the'\
        ' drug in pregnant women despite potential risks. \n\n '\
        'CATEGORY D : There is positive evidence of human fetal  risk based'\
        ' on adverse reaction data from investigational or marketing'\
        ' experience or studies in humans, but potential benefits may warrant'\
        ' use of the drug in pregnant women despite potential risks.\n\n'\
        'CATEGORY X : Studies in animals or humans have demonstrated fetal'\
        ' abnormalities and/or there is positive evidence of human fetal risk'\
        ' based on adverse reaction data from investigational or marketing'\
        ' experience, and the risks involved in use of the drug in pregnant'\
        ' women clearly outweigh potential benefits.\n\n'\
        'CATEGORY N : Not yet classified'),
                
        'overdosage': fields.text(string='Overdosage', help='Overdosage'),
        'pregnancy_warning': fields.boolean(string='Pregnancy Warning', 
                    help='The drug represents risk to pregnancy or lactancy'),
        'notes': fields.text(string='Extra Info'),
        'storage': fields.text(string='Storage Conditions'),
        'adverse_reaction': fields.text(string='Adverse Reactions'),
        'active_component': fields.char(size=256, string='Active component',
                                        translate=True, 
                                        help='Active Component'),
        'dosage': fields.text(string='Dosage Instructions', 
                              help='Dosage / Indications'),
        'pregnancy': fields.text(string='Pregnancy and Lactancy', 
                                 help='Warnings for Pregnant Women'),
        'presentation': fields.text(string='Presentation'),
        'composition': fields.text(string='Composition', help='Components'),
    }

OeMedicalMedicament()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

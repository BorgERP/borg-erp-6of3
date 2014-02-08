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
import time
import math
from osv import osv
from osv import fields
from datetime import datetime
from dateutil import relativedelta as rdelta


class OeMedicalPatient(osv.osv):
    _name='oemedical.patient'
    _inherits={
        'res.partner': 'partner_id',
    }
    def _compute_age(self, dob):
        DATETIME_FORMAT = "%Y-%m-%d"
        now = datetime.now()
        birth_date = datetime.strptime(dob, DATETIME_FORMAT)
        timedelta = rdelta.relativedelta(now,birth_date)
        years_num = timedelta.years
        return (years_num)
    
    _columns={
        'partner_id': fields.many2one(
            'res.partner', 'Related Partner', required=False,
            ondelete='cascade', help='Partner-related data of the patient',domain="[('is_patient','=',True)]"),
        'family': fields.many2one('oemedical.family', string='Family',
                                  help='Family Code'),
        'photo': fields.binary(string='Picture'),
        'sex': fields.selection([('m', 'Male'), ('f', 'Female'), ],
                                string='Sex'),
        'blood_type': fields.selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'),
                                        ('O', 'O'), ], string='Blood Type'),
        'general_info': fields.text(string='General Information',
                                help='General information about the patient'),
        'primary_care_doctor': fields.many2one('oemedical.physician',
                                               'Primary Care Doctor',
                                help='Current primary care / family doctor'),
        'childbearing_age': fields.boolean('Potential for Childbearing'),
        'medications': fields.one2many('oemedical.patient.medication',
                                       'patient_id', string='Medications',),
        'evaluations': fields.one2many('oemedical.patient.evaluation',
                                       'patient_id', string='Evaluations',),
        'critical_info': fields.text(
            string='Important disease, allergy or procedures information',
            help='Write any important information on the patient\'s disease,'\
            ' surgeries, allergies, ...'),
        'rh': fields.selection([('+', '+'), ('-', '-'), ], string='Rh'),
        'current_address': fields.many2one('res.partner', string='Address',
        help='Contact information. You may choose from the different contacts'\
        ' and addresses this patient has.'),
        'diseases': fields.one2many('oemedical.patient.disease',
                                    'patient_id', string='Diseases',
                                    help='Mark if the patient has died'),
        'lastname': fields.char(size=256, string='Lastname',),
        'ethnic_group': fields.many2one('oemedical.ethnicity',
                                        string='Ethnic group',),
        'ssn': fields.char(size=256, string='SSN',),
        'vaccinations': fields.one2many('oemedical.vaccination', 'patient_id',
                                        'Vaccinations',),
        'dob': fields.date(string='DoB'),
        'age': fields.char(size=256, string='Age'),
        'marital_status': fields.selection([('s', 'Single'), ('m', 'Married'),
                                            ('w', 'Widowed'),
                                            ('d', 'Divorced'),
                                            ('x', 'Separated'), ],
                                           string='Marital Status', sort=False),
        'dod': fields.datetime(string='Date of Death'),
        'current_insurance': fields.many2one('oemedical.insurance',
                                             string='Insurance',
                help='Insurance information. You may choose from the different'\
        ' insurances belonging to the patient'),
        'cod': fields.many2one('oemedical.pathology',
                               string='Cause of Death',),
        'identification_code': fields.char('Reference', size=64, select=1, readonly=True),
        'deceased': fields.boolean(string='Deceased'),
        'date_registered': fields.date('Date Registered'),
        'profession': fields.char(size=256, string='Profession'),
        'mbo': fields.char('Insurance number', size=9),
        'phone':fields.related('address','phone',type='char', string='Phone',readonly=True),
        'sport_activities': fields.char(size=256, string='Sport activities'),
        'medication': fields.char(size=256, string='Medication'),
        
        'medical_diagnosis': fields.text(string='Medical diagnosis'),
        'functional_diagnosis': fields.text(string='Functional diagnosis'),
        'anamnesis': fields.text(string='Anamnesis'),
        'activities_participation': fields.text(string='Activity participation'),
        'analysis': fields.text(string='Analysis: structure-function'),
        'therapy_goals': fields.text(string='Therapy goals'),
        'client_goals': fields.text(string='Client goals'),
        'plan': fields.text(string='Plan'),
        'other': fields.text(string='Other'),
        'notes': fields.text(string='Notes'),
        'client_confirmation': fields.boolean(string='Confirmation of the clients information'),
        'bowen_line': fields.one2many('oemedical.bowen.line',
                                             'bowen_therapy_id',
                                             string='Bowen Therapy Sessions',),
    }
    
    _defaults={
         #'ref': lambda obj, cr, uid, context: 
                #obj.pool.get('ir.sequence').get(cr, uid, 'oemedical.patient'),
         'identification_code':lambda self, cr, uid, context: 
                self.pool.get('ir.sequence').get(cr, uid, 'oemedical.patient'),
         'is_patient': True,
         'date_registered': lambda *a: time.strftime('%Y-%m-%d'),
        
                 }
    

    
    def onchange_dob(self, cr, uid, ids, dob):
        now = datetime.now()
        result = {'value': {}}
        if dob:
            (years_num) = self._compute_age(dob)
            result['value']['age'] = int(math.fabs(years_num))
        else:
            result['value']['age'] = 0
        return result
OeMedicalPatient()

class BowenTherapy(osv.osv):
    _name = 'oemedical.bowen.line'

    _columns = {
        'session_name': fields.char(size=64, string='Name',),
        'session_date': fields.date('Date'),
        'subjective': fields.text(string='Subjective'),
        'objective': fields.text(string='Objective'),
        'treatment': fields.text(string='Treatment'),
        'water': fields.char(size=64, string='Water',),
        'walk': fields.char(size=64, string='Walk',),
        'week': fields.char(size=64, string='Week',),
        'bowen_therapy_id': fields.many2one(
            'oemedical.patient',
            string='Bowen Therapy ID', ),
        
    }

BowenTherapy()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

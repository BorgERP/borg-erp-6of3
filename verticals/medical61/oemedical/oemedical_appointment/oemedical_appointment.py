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
from base_calendar import base_calendar

class OeMedicalAppointment(osv.osv):
    _name = 'oemedical.appointment'
    _inherit = "calendar.event"
    _columns = {
        'consultations': fields.many2one('product.product',
                                         string='Consultation Services',
                                          help='Consultation Services'),

        'patient_id': fields.many2one('oemedical.patient', string='Patient',
                                   required=True, select=True,
                                   help='Patient Name'),
        'name': fields.char(size=256, string='Appointment ID', readonly=True),
        'appointment_date': fields.datetime(string='Date and Time'),
        'doctor': fields.many2one('oemedical.physician',
                                  string='Physician',select=True, 
                                  help='Physician\'s Name'),
        'comments': fields.text(string='Comments'),
        'appointment_type': fields.selection([
            ('ambulatory', 'Ambulatory'),
            ('outpatient', 'Outpatient'),
            ('inpatient', 'Inpatient'),
        ], string='Type'),
        'institution': fields.many2one('res.partner',
                                       string='Health Center',
                                       help='Medical Center'),
        'urgency': fields.selection([
            ('a', 'Normal'),
            ('b', 'Urgent'),
            ('c', 'Medical Emergency'), ],
            string='Urgency Level'),
        'speciality': fields.many2one('oemedical.specialty',
                                      string='Specialty', 
                                      help='Medical Specialty / Sector'),
        'user_id': fields.many2one('res.users', 'User',domain="[('is_doctor','=',True)]"),
        'product_id':fields.many2one( 'product.product','Product'),
        'operational_area': fields.many2one('oemedical.operational_area', string='Operational area'),
        'attendee_ids': fields.many2many('calendar.attendee', 'appointment_attendee_rel', \
                                         'event_id', 'attendee_id', 'Attendees'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirmed', 'Confirmed'),
                                   ('cancelled', 'Cancelled')], 'State', readonly=True),     
    }
    
    _defaults = {
         'state': 'draft',
         'name': lambda obj, cr, uid, context: 
            obj.pool.get('ir.sequence').get(cr, uid, 'oemedical.appointment'),
                 }

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        return super(osv.osv, self).read_group(cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False)

OeMedicalAppointment()

class base_calendar_invite_attendee(osv.osv_memory):
    """
    Invite attendee.
    """
    _name = "base_calendar.invite.attendee"
    _inherit = "base_calendar.invite.attendee"
    _description = "Invite Attendees"
    _columns = {
        'user_ids': fields.many2many('res.users', 'invite_user_rel',
                                  'invite_id', 'user_id', 'Users',domain="[('is_doctor','=',True)]"),
    }
    _defaults = {
        'send_mail': False
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

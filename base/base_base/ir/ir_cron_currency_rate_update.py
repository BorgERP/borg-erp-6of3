# -*- encoding: utf-8 -*-
##############################################################################
#
#    Slobodni programi d.o.o.
#    Copyright (C) 2012- Slobodni programi (<http://www.slobodni-programi.hr>).
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#    End users who are looking for a ready-to-use solution with commercial
#    garantees and support are strongly adviced to contract a Free Software
#    Service Company
#
#    This program is Free Software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import calendar
import openerp
from openerp.cron import WAKE_UP_NOW
from openerp.osv import osv, fields
from datetime import datetime
from tools import DEFAULT_SERVER_DATETIME_FORMAT
from tools.safe_eval import safe_eval as eval
from tools.translate import _
from dateutil.relativedelta import relativedelta

_intervalTypes = {
    'work_days': lambda interval: relativedelta(days=interval),
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}

class ir_cron(osv.Model):
    _inherit = "ir.cron"
    _columns = {
        'update_nextcall' : fields.boolean('Update next call', help="If Repeat Missed is checked, checking this option updates nextcall date in each cron call. By default, this option is unchecked. "),
    }
    _defaults = {
        'update_nextcall': False,
    }

    def _run_job(self, cr, job, now):
        """ Run a given job taking care of the repetition.

        The cursor has a lock on the job (aquired by _run_jobs_multithread()) and this
        method is run in a worker thread (spawned by _run_jobs_multithread())).

        :param job: job to be run (as a dictionary).
        :param now: timestamp (result of datetime.now(), no need to call it multiple time).

        """
        try:
            nextcall = datetime.strptime(job['nextcall'], DEFAULT_SERVER_DATETIME_FORMAT)
            numbercall = job['numbercall']

            ok = False
            while nextcall < now and numbercall:
                if numbercall > 0:
                    numbercall -= 1
                if not ok or job['doall']:
                    self._callback(cr, job['user_id'], job['model'], job['function'], job['args'], job['id'])
                if numbercall:
                    nextcall += _intervalTypes[job['interval_type']](job['interval_number'])
                # CFO_START: This change is made to ensure that in every job execution we can access date of the execution
                if 'update_nextcall' in job and job['update_nextcall']:
                    addsql = ''
                    if not numbercall:
                        addsql = ', active=False'
                    cr.execute("UPDATE ir_cron SET nextcall=%s, numbercall=%s" + addsql + " WHERE id=%s",
                               (nextcall.strftime(DEFAULT_SERVER_DATETIME_FORMAT), numbercall, job['id']))
                ok = True

            if not ('update_nextcall' in job and job['update_nextcall']):
                addsql = ''
                if not numbercall:
                    addsql = ', active=False'
                cr.execute("UPDATE ir_cron SET nextcall=%s, numbercall=%s" + addsql + " WHERE id=%s",
                           (nextcall.strftime(DEFAULT_SERVER_DATETIME_FORMAT), numbercall, job['id']))
            # CFO_END
            if numbercall:
                # Reschedule our own main cron thread if necessary.
                # This is really needed if this job runs longer than its rescheduling period.
                nextcall = calendar.timegm(nextcall.timetuple())
                openerp.cron.schedule_wakeup(nextcall, cr.dbname)
        finally:
            cr.commit()
            cr.close()
            openerp.cron.release_thread_slot()

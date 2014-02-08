# -*- encoding: utf-8 -*-
##############################################################################
#
#    Slobodni programi d.o.o.
#    Copyright (C) 2012- Slobodni programi (<http://www.slobodni-programi.hr>).
#
#    This module was originally developed by OpenERP.
#    We thank them for their contribution.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from osv import osv, fields
from tools.translate import _
from datetime import datetime


class res_currency_rate_wizard(osv.TransientModel):
    _name = 'res.currency.rate.wizard'
    _description = 'Refresh currencies by update services and date range'

    _columns = {
        'date_start': fields.date(string='Starts', required=True),
        'date_end': fields.date(string='Ends', required=True),
        'service_ids': fields.many2many('res.currency.rate.update.service', 'res_currency_service_wizard_rel', 'wizard_id', 'service_id', string='Services', required=True),
        # 'company_id': fields.many2one('res.company', string='Company', required=True),
    }

    def _get_all_services(self, cr, uid, context=None):
        # company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'res.currency.rate.update.wizard',context=context)
        # return self.pool.get('res.currency.rate.update.service').search(cr, uid , [('company_id','=',company_id)])
        return self.pool.get('res.currency.rate.update.service').search(cr, uid, [])

    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),
        # 'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'res.currency.rate.update.wizard',context=c),
        'service_ids': _get_all_services,
    }

    # def onchange_company_id(self, cr, uid, ids, company_id, context=None):
    #    if context is None:
    #        context = {}
    #    service_ids = self.pool.get('res.currency.rate.update.service').search(cr, uid ,[('company_id','=',company_id)])
    #    return {'value': {'service_ids': service_ids}}

    def update_currencies(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        service_ids = [service.id for service in data.service_ids]
        date_start = datetime.strptime(data.date_start, '%Y-%m-%d')
        date_end = datetime.strptime(data.date_end, '%Y-%m-%d')

        currency_updater_obj = self.pool.get('res.currency.rate.update')
        currency_updater_obj.run_currency_update(cr, uid, service_ids, date_start, date_end,
                                                 called_from='update wizard', context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

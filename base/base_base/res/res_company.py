# -*- encoding: utf-8 -*-
##############################################################################
#
#    Slobodni programi d.o.o.
#    Copyright (C) 2012- Slobodni programi (<http://www.slobodni-programi.hr>).
#
#    This module was originally developed by Camptocamp.
#    We thank them for their contribution.
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

from osv import fields, osv
from tools.translate import _
from lxml import etree


class res_company(osv.Model):
    """override company to add currency update"""

    def button_refresh_currency(self, cr, uid, ids, context=None):
        """Refresh the currency ! For all the company now"""
        service_id = None
        if 'service_id' not in context:
            raise osv.except_osv(_('Warning!'),
                                 _('You must choose bank for currency rate update. Also, that bank must have defined update service.'))
        else:
            service_id = context['service_id']
        currency_updater_obj = self.pool.get('res.currency.rate.update')
        try:
            currency_updater_obj.run_currency_update(cr, uid, service_id, None, None,
                                                              called_from='company', context=context)
        except Exception, e:
            return False
        return True

    _inherit = "res.company"
    _columns = {
        # activate the currency update
        'update_service_id': fields.many2one(obj='res.currency.rate.update.service', string='Currency update service'),
        'service_currency_to_update': fields.related('update_service_id', 'currency_to_update',
                                                     type="many2many", relation='res.currency',
                                                     string='currency to update with this service', readonly=True),
    }

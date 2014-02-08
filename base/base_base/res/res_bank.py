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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
from lxml import etree


class Bank(osv.Model):
    _inherit = 'res.bank'
    _columns = {
        'update_service_id': fields.many2one('res.currency.rate.update.service', string="Currency update service",
                                             help="Service to get currency rates for this bank"),
        'fetch_bid_rate': fields.related('update_service_id', 'fetch_bid_rate', type='boolean', string="Fetch bid rate", readonly=True,
                                         help="Middle rate is fetched by default. If there is a need you can also fetch bid rate."),
        'fetch_ask_rate': fields.related('update_service_id', 'fetch_ask_rate', type='boolean', string="Fetch ask rate", readonly=True,
                                         help="Middle rate is fetched by default. If there is a need you can also fetch ask rate."),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(Bank, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)

        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'res.bank', context=context)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='update_service_id']")
        for node in nodes:
            node.set('domain', "[('company_id','=',%(c_id)d)]" % {'c_id': company_id})
        res['arch'] = etree.tostring(doc)
        return res

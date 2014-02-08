# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
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

from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import fields
from osv import osv
from tools.translate import _
import ir
import netsvc
import time

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    
    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        procurement_obj = self.pool.get('procurement.order')
        produce_ids = []
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            loc_id = procurement.location_id.id
            newdate = datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.product_id.product_tmpl_id.produce_delay or 0.0)
            newdate = newdate - relativedelta(days=company.manufacturing_lead)
            if procurement.product_id.virtual_available < 0:
                produce_id = production_obj.create(cr, uid, {
                    'origin': procurement.origin,
                    'product_id': procurement.product_id.id,
                    'product_qty': - procurement.product_id.virtual_available,
                    'product_uom': procurement.product_uom.id,
                    'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                    'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                    'location_src_id': procurement.location_id.id,
                    'location_dest_id': procurement.location_id.id,
                    'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                    'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                    'move_prod_id': res_id,
                    'company_id': procurement.company_id.id,
                })
                res[procurement.id] = produce_id
                produce_ids.append(produce_id)
                bom_result = production_obj.action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
                self.write(cr, uid, [procurement.id], {'state': 'running'})
            else:
                self.write(cr, uid, [procurement.id], {'state': 'ready','message':'from stock: products assigned.','procure_method':'make_to_stock'})
                move_obj.write(cr, uid, [res_id],
                    {'state': 'assigned'})
            move_obj.write(cr, uid, [res_id],
                    {'location_id': procurement.location_id.id})
            for produce_id in produce_ids:
                wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
        return res
    
procurement_order()
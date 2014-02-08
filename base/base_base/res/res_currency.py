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

import time
from osv import fields, osv
import decimal_precision as dp
from lxml import etree
from tools.translate import _
from tools import float_round, float_is_zero, float_compare
import addons
from openerp import SUPERUSER_ID


class one2many_mod(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if context is None:
            context = {}
        if self._context:
            context = context.copy()
        context.update(self._context)
        if values is None:
            values = {}
        res = {}
        for id in ids:
            res[id] = []
        service_id = context.get('service_id', False)
        if not service_id:
            tmp_user = obj.pool.get('res.users').browse(cr, user, user, context=context)
            service_id = tmp_user and tmp_user.company_id and \
                         tmp_user.company_id.update_service_id and \
                         tmp_user.company_id.update_service_id.id or None
        rate_type_code = context.get('rate_type_code', False) or 'middle_rate'
        id = obj.pool.get('res.currency.rate.type').search(cr, user,
                                [('code', '=', rate_type_code)], context=context)
        rate_type_id = id and id[0] or None

        condition = [('update_service_id', '=', service_id),
                     ('currency_rate_type_id', '=', rate_type_id),
                    ]

        ids2 = obj.pool.get(self._obj).search(cr, user, condition + self._domain + [(self._fields_id, 'in', ids)], limit=self._limit, context=context)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            if r[self._fields_id] in res:
                res[r[self._fields_id]].append(r['id'])
        return res


class res_currency(osv.Model):
    """ Override res.currency object to change compute method so it would take currency rate types into consideration """

    def _current_rate(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        date = context.get('date', False) or time.strftime('%Y-%m-%d')
        rate_type_code = context.get('rate_type_code', False) or 'middle_rate'
        id = self.pool.get('res.currency.rate.type').search(cr, uid,
                                [('code', '=', rate_type_code)], context=context)
        rate_type_id = id and id[0] or None
        service_id = context.get('service_id', False)
        if not service_id:
            company = context.get('company_id', False) and \
                        self.pool.get('res.users').browse(cr, SUPERUSER_ID, [context['company_id']])[0].company_id or \
                        self.pool.get('res.users').browse(cr, uid, uid).company_id
            service_id = company.update_service_id.id
        service_id = service_id or None

        for id in ids:
            cr.execute("""SELECT currency_id, rate, ratio
                               ,case when abs(rate)>0.0 then 1.000000/rate else 0.0000
                                end as rate_inv
                          FROM res_currency_rate
                         WHERE currency_id = %(currency_id)s
                           AND name <= '%(name)s'
                           AND update_service_id = %(service_id)s
                           AND currency_rate_type_id = %(currency_type)s
                           ORDER BY name desc, update_service_id LIMIT 1""" % {
                'currency_id': id, 'name': date, 'currency_type': rate_type_id or 'null', 'service_id': service_id or 'null'})
            if cr.rowcount:
                id, rate, ratio, rate_inv = cr.fetchall()[0]
                res[id] = {'rate': rate, 'ratio': ratio, 'rate_inv': rate_inv}
            else:
                res[id] = {'rate': 0., 'ratio': 0, 'rate_inv': 0.}
        return res

    _inherit = 'res.currency'
    _columns = {
        'rate': fields.function(_current_rate, type='float', string='Current Rate', digits=(16, 8),
            help='The rate of the currency to the currency of rate 1.', multi='currency'),
        'ratio': fields.function(_current_rate, type='integer', string='Ratio',
            help='The rate of the currency to the currency of rate 1.', multi='currency'),
        'rate_ids': one2many_mod('res.currency.rate', 'currency_id', 'Rates'),
        'rate_inv': fields.function(_current_rate, type='float', string='Inverse Rate',
                                    digits=(16, 8), digits_compute=dp.get_precision('Currency rate'),
                                    help='Inverse ratio. ', multi='currency'),
    }

    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        res = super(res_currency, self).read(cr, user, ids, fields, context, load)
        currency_rate_obj = self.pool.get('res.currency.rate')
        for r in res:
            if r.__contains__('rate_ids'):
                rates = r['rate_ids']
                if rates:
                    # difference # - taking latest rate - highest id
                    r['date'] = max([x['name'] for x in currency_rate_obj.read(cr, user, rates, ['name'])])
        return res

    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount,
                round=True, currency_type_from_code=False, currency_type_to_code=False, context=None):
        if not context:
            context = {}
        if not from_currency_id:
            from_currency_id = to_currency_id
        if not to_currency_id:
            to_currency_id = from_currency_id
        # Added to check context for currency rate types 'ask_rate', 'middle_rate' or 'bid_rate'
        if not currency_type_from_code:
            currency_type_from_code = context.get('currency_type_from_code')
        if not currency_type_to_code:
            currency_type_to_code = context.get('currency_type_to_code')
        # Check ends
        xc = self.browse(cr, uid, [from_currency_id, to_currency_id], context=context)
        from_currency = (xc[0].id == from_currency_id and xc[0]) or xc[1]
        to_currency = (xc[0].id == to_currency_id and xc[0]) or xc[1]

        force_currency_rate = 0.0
        if context.get('force_currency_rate'):
            if not float_is_zero(context.get('force_currency_rate'), precision_digits=8):  # if self.is_zero(self.cr, self.uid, currency, res['credit'])
                force_currency_rate = 1. / context.get('force_currency_rate')
        if context.get('force_currency_inv_rate'):
            force_currency_rate = context.get('force_currency_inv_rate')
        if not float_is_zero(force_currency_rate, precision_digits=8):
            if round:
                return self.round(cr, uid, to_currency, from_amount * force_currency_rate)
            else:
                return (from_amount * force_currency_rate)

        if (to_currency_id == from_currency_id) and (currency_type_from_code == currency_type_to_code):
            if round:
                return self.round(cr, uid, to_currency, from_amount)
            else:
                return from_amount
        else:
            context.update({'currency_type_from_code': currency_type_from_code, 'currency_type_to_code': currency_type_to_code})
            rate = self._get_conversion_rate(cr, uid, from_currency, to_currency, context=context)
            if round:
                return self.round(cr, uid, to_currency, from_amount * rate)
            else:
                return (from_amount * rate)

    def _get_conversion_rate(self, cr, uid, from_currency, to_currency, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'currency_rate_type_code': ctx.get('currency_type_from_code')})
        from_currency = self.browse(cr, uid, from_currency.id, context=ctx)

        ctx.update({'currency_rate_type_code': ctx.get('currency_type_to_code')})
        to_currency = self.browse(cr, uid, to_currency.id, context=ctx)

        if from_currency.rate == 0 or to_currency.rate == 0:
            date = context.get('date', time.strftime('%Y-%m-%d'))
            if from_currency.rate == 0:
                currency_symbol = from_currency.symbol
            else:
                currency_symbol = to_currency.symbol
            raise osv.except_osv(_('Error'), _('No rate found \n' \
                    'for the currency: %s \n' \
                    'at the date: %s') % (currency_symbol, date))
        return to_currency.rate / from_currency.rate


class res_currency_rate(osv.Model):
    """ Override res.currency.rate object to add fields bank_id """

    def _rate_inv(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for rate in self.browse(cr, uid, ids, context=context):
            res[rate.id] = {'rate_inv': abs(rate.rate) > 0.0 and
                                        1.0 / rate.rate or 0.0
                            }
            # res[rate.id] = {}
            # inverse = 0.0
            # if abs(rate.rate) > 0.0:
            #    inverse = 1.0 / rate.rate
            # res[rate.id]['rate_inv'] = inverse
        return res

    def _check_curency_rate_type(self, cr, uid, c):
        id = self.pool.get('res.currency.rate.type').search(cr, uid, [('code', '=', 'middle_rate')], context=c)
        return id and id[0] or id

    _inherit = "res.currency.rate"
    _columns = {
        # This field will hold real value of currency, because e.g. users in Croatia are accustomed to view
        # 1 EUR = XXX HRK, instead of real ratio 1 HRK = YYY EUR, field 'rate' is used for users to see
        'update_service_id': fields.many2one('res.currency.rate.update.service', 'Service',
                                             select=True,
                                             help='This field shows the bank/service from which the currency list was obtained'),
        'ratio': fields.integer('Ratio', help='Ratio', required=True),
        'rate_inv': fields.function(_rate_inv, type='float', string='Inverse Rate', digits_compute=dp.get_precision('Currency rate'),
            help='Inverse ratio. ', multi='currency'),
        'from_currency_id': fields.many2one('res.currency', 'From Currency',)  # required=True, readonly=True), states={'draft':[('readonly',False)]}),
    }
    _defaults = {
        'currency_rate_type_id': _check_curency_rate_type,
        'ratio': 1,
    }

    def _auto_init(self, cr, context=None):
        res = super(res_currency_rate, self)._auto_init(cr, context=context)
        f = addons.get_module_resource('base_base', 'sql', 'oe_currency_compute.sql')
        sql = open(f).read()
        cr.execute(sql)
        return res


class res_currency_rate_type(osv.Model):
    _inherit = "res.currency.rate.type"
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),  # original
        'code': fields.char('Code', size=16, required=True),  # added
    }
    _sql_constraints = [
        ('unique_rate_type', 'unique (code)', 'The currency rate type must be unique!'),
    ]

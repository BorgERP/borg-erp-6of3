# -*- encoding: utf-8 -*-
##############################################################################
#
#    Slobodni programi d.o.o.
#    Copyright (C) 2012- Slobodni programi (<http://www.slobodni-programi.hr>).
#
#    This module was originally developed by Camptocamp.
#    We thank them for their contribution.
#
#    - ported XML-based webservices (Admin.ch, ECB, PL NBP) to new XML lib
#    - rates given by ECB webservice is now correct even when main_cur <> EUR
#    - rates given by PL_NBP webservice is now correct even when main_cur <> PLN
#    - if company_currency <> CHF, you can now update CHF via Admin.ch webservice
#    (same for EUR with ECB webservice and PLN with NBP webservice)
#    For more details, see Launchpad bug #645263
#    - mecanism to check if rates given by the webservice are "fresh" enough to be
#    written in OpenERP ('max_delta_days' parameter for each currency update service)
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

# TODO "nice to have" : restain the list of currencies that can be added for
# a webservice to the list of currencies supported by the Webservice
# TODO : implement max_delta_days for Yahoo webservice

import string
import logging
import time
from mx import DateTime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tools.translate import _
from osv import osv, fields
from lxml import etree


class res_currency_rate_update_service(osv.Model):
    """Class that tells for which services which currencies have to be updated"""

    def _get_curr_services(self, cr, uid, context=None):
        return [('manual', _('Manual')),
                ('Yahoo_getter', _('Yahoo Finance')),
                ('ECB_getter', _('European Central Bank')),
               ]

    _name = "res.currency.rate.update.service"
    _description = "Currency rate update service"
    _columns = {
        'name': fields.char(string='Name', size=64, required=True),
        'service': fields.selection(_get_curr_services, string='Webservice to use', required=True),
        'currency_to_update': fields.many2many('res.currency', 'res_currency_auto_update_rel', 'service_id', 'currency_id', help='currency to update with this service'),
        'company_id': fields.many2one('res.company', string='Linked company'),
        'note': fields.text(string='Update notice'),
        'max_delta_days': fields.integer('Max delta days', required=True, help="If the time delta between the rate date given by the webservice and the current date exeeds this value, then the currency rate is not updated in OpenERP."),
        'fetch_bid_rate': fields.boolean(string="Fetch bid rate", help="Defines if service offers bid rate data."),
        'fetch_ask_rate': fields.boolean(string="Fetch ask rate", help="Defines if service offers ask rate data."),
        'bank_ids': fields.one2many('res.bank', 'update_service_id', string="Banks", help="Banks using this service."),
        'auto_currency_up': fields.boolean('Automatic update'),
        'cron_id': fields.many2one('ir.cron', string='Automatic update object'),
        'from_currency_id': fields.many2one('res.currency', 'From Currency', required=True,)
    }
    _defaults = {
        'max_delta_days': lambda *a: 1,
        'fetch_bid_rate': False,
        'fetch_ask_rate': False,
        'company_id': False,  #
    }
    _sql_constraints = [
        ('curr_service_unique', 'unique (service, from_currency_id)', _('You can use a service one time per From Currency !'))
    ]

    def _check_max_delta_days(self, cr, uid, ids):
        for i in ids:
            value_to_check = self.read(cr, uid, i, ['max_delta_days'])['max_delta_days']
            if value_to_check >= 0:
                return True
            else:
                return False

    _constraints = [
        (_check_max_delta_days, "'Max delta days' must be >= 0", ['max_delta_days']),
    ]

    def button_refresh_currency(self, cr, uid, ids, context=None):
        """Refresh the currency ! For all the company now"""
        if 'active_id' in context:
            service_id = context['active_id']
        else:
            return False
        currency_updater_obj = self.pool.get('res.currency.rate.update')
        currency_updater_obj.run_currency_update(cr, uid, service_id, None, None,
                                                 called_from='update service', context=context)
        return True

    def button_fetch_currencies(self, cr, uid, ids, context=None):
        """Refresh the currency ! For all the company now"""
        context = {} if not context else context

        if 'active_id' in context:
            service_id = context['active_id']
        else:
            raise osv.except_osv(_('Currency update error'), _("Couldn't find update service id. Please contact your administrator. "))

        currency_obj = self.pool.get('res.currency')
        currency_updater_obj = self.pool.get('res.currency.rate.update')
        update_service_obj = self.pool.get('res.currency.rate.update.service')
        service = update_service_obj.browse(cr, uid, service_id, context=context)

        # get available currencies fom the service
        factory = Currency_getter_factory()
        if service.service in ['Yahoo_getter']:
            # we get ALL currencies
            currency_ids = currency_obj.search(cr, uid, [], context=context)
        elif service.service in ['manual']:
            currency_ids = currency_obj.search(cr, uid, [('name', 'in', ('EUR', 'USD',))], context=context)
        else:
            getter = factory.register(service.service)()
            currencies = getter.get_available_currencies()
            if not currencies:
                raise osv.except_osv(_('Currency update error'), _("Couldn't fetch update service currency data. Please contact your administrator. "))
            # Get currencies ids
            currency_ids = currency_obj.search(cr, uid, [('name', 'in', currencies)], context=context)
        update_service_obj.write(cr, uid, service.id, {'currency_to_update': [(6, 0, currency_ids)]}, context=context)

        return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(res_currency_rate_update_service, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)

        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_ids = ','.join([str(x.id) for x in current_user.company_ids])

        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='company_id']")
        for node in nodes:
            node.set('domain', "[('id','in',[%s])]" % (company_ids))
        res['arch'] = etree.tostring(doc)
        return res

    def create(self, cr, uid, values, context=None):
        if values.get('service', False) == 'manual':
            values['auto_currency_up'] = False
        service_id = super(res_currency_rate_update_service, self).create(cr, uid, values, context=context)
        if 'auto_currency_up' in values and values['auto_currency_up']:
            try:
                currency_updater_obj = self.pool.get('res.currency.rate.update')
                context.update({'update_service_name': values['name'], 'update_service_id': service_id})
                cron_id = currency_updater_obj.get_cron_id(cr, uid, context=context)
                self.pool.get('res.currency.rate.update.service').write(cr, uid, [service_id], {'cron_id': cron_id})
            except Exception, e:
                return False
        return service_id

    def write(self, cr, uid, ids, values, context=None):
        if context is None:
            context = {}
        if values.get('service', False) == 'manual':
            values['auto_currency_up'] = False
        if 'auto_currency_up' in values or 'name' in values:
            cron_dict = {}
            try:
                for id in ids:
                    tmp_context = context.copy()
                    cron_obj = self.pool.get('ir.cron')
                    service_obj = self.pool.get('res.currency.rate.update.service')
                    currency_updater_obj = self.pool.get('res.currency.rate.update')

                    service_data = service_obj.read(cr, uid, id, ['name', 'cron_id'], context=tmp_context)
                    cron_id = None
                    if 'cron_id' in service_data and service_data['cron_id']:
                        cron_id = service_data['cron_id'][0]

                    name = service_data['name']
                    if 'name' in values:
                        name = values['name']
                        cron_dict.update({'name': name})

                    if 'auto_currency_up' in values:
                        cron_dict.update({'active': values['auto_currency_up']})

                    # We enabled cron
                    if 'auto_currency_up' in values and values['auto_currency_up'] and not cron_id:
                        tmp_context.update({'update_service_name': name, 'update_service_id': id})
                        cron_id = currency_updater_obj.get_cron_id(cr, uid, context=tmp_context)
                        values['cron_id'] = cron_id
                    else:
                        cron_obj.write(cr, uid, [cron_id], cron_dict, context=tmp_context)
            except Exception, e:
                raise osv.except_osv(_('Unknown Error !'), str(e))
        return super(res_currency_rate_update_service, self).write(cr, uid, ids, values, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        try:
            for id in ids:
                cron_obj = self.pool.get('ir.cron')
                service_obj = self.pool.get('res.currency.rate.update.service')

                service_data = service_obj.read(cr, uid, id, ['cron_id'], context=context)
                cron_id = None
                if 'cron_id' in service_data and service_data['cron_id']:
                    cron_id = service_data['cron_id'][0]
                if cron_id:
                    cron_obj.unlink(cr, uid, [cron_id], context=context)
        except Exception, e:
            raise osv.except_osv(_('Unknown Error !'), str(e))
        return super(res_currency_rate_update_service, self).unlink(cr, uid, ids, context=context)


class res_currency_rate_update(osv.Model):
    """Class that handle an ir cron call who will update currencies based on a web url"""

    _name = "res.currency.rate.update"
    _description = "Currency rate update"
    _auto = False

    # Dict that represent a cron object
    cron = {
        'active'         : True,
        'priority'       : 1,
        'interval_number': 1,
        'interval_type'  : 'days',
        'nextcall'       : time.strftime("%Y-%m-%d %H:%M:%S", (datetime.today() + timedelta(days=1)).timetuple()),  # tomorrow same time
        'numbercall'     :-1,
        'doall'          : True,
        'model'          : 'res.currency.rate.update',
        'function'       : 'run_currency_update',
        'args'           : '()',
        'update_nextcall': True,
    }

    logger = logging.getLogger(__name__)

    LOG_NAME = 'cron-rates'
    MOD_NAME = 'currency_rate_update: '

    def get_cron_id(self, cr, uid, context):
        """return the updater cron's id. Create one if the cron does not exists """
        cron_obj = self.pool.get('ir.cron')

        cron_id = None
        cron_name = None
        if 'update_service_name' in context:
            cron_name = context['update_service_name']

        try:
            # Find the cron that send messages
            cron_id = cron_obj.search(cr, uid, [('function', 'ilike', self.cron['function']),
                                                ('model', 'ilike', self.cron['model']),
                                                ('name', '=', cron_name)])
            cron_id = int(cron_id[0])
        except Exception, e:
            self.logger.info('Warning - cron not, found one will be created...')
            pass  # Ignore if the cron is missing cause we are going to create it in db

        # The cron does not exists
        if not cron_id:
            self.cron['name'] = cron_name
            if 'update_service_id' in context:
                self.cron['args'] = "(%(service_id)s,None,None,'cron')" % {'service_id': context['update_service_id']}
            cron_id = cron_obj.create(cr, uid, self.cron, context)
        return cron_id

    def save_cron(self, cr, uid, datas, context=None):
        """save the cron config data should be a dict"""
        # Modify the cron
        if context is None:
            context = {}
        cron_id = self.get_cron_id(cr, uid, context=context)
        result = self.pool.get('ir.cron').write(cr, uid, [cron_id], datas)
        return result

    # called_from = ['company', 'update service', 'cron', 'update wizard']
    def run_currency_update(self, cr, uid, service_ids=None,
                            date_start=None, date_end=None, called_from='cron', context=None):
        "update currency at the given frequency"

        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        rate_obj = self.pool.get('res.currency.rate')
        rate_type_obj = self.pool.get('res.currency.rate.type')
        update_service_obj = self.pool.get('res.currency.rate.update.service')

        # company_id = None
        if service_ids:
            if type(service_ids) is not list:
                service_ids = [service_ids]
            # company_id = update_service_obj.read(cr, uid, service_ids, ['company_id'], context=context)[0]['company_id'][0]
        else:
            service_ids = []

        # If there is no context and there is no date_start I must guess
        if service_ids:
            service = update_service_obj.browse(cr, uid, service_ids, context=context)[0]
            if service and service.cron_id and called_from == 'cron':
                # Needed to override ir_cron method so nextcall can be saved
                date_end = date_start = datetime.strptime(service.cron_id.nextcall, '%Y-%m-%d %H:%M:%S')
        if service_ids and called_from and called_from == 'update service':
            date_end = datetime.today() - timedelta(days=1)
            date_start = datetime.today() - timedelta(days=7)

        factory = Currency_getter_factory()
        middle_rate_type_id = rate_type_obj.search(cr, uid, [('code', '=', 'middle_rate')], limit=1)[0]
        ask_rate_type_id = rate_type_obj.search(cr, uid, [('code', '=', 'ask_rate')], limit=1)[0]
        bid_rate_type_id = rate_type_obj.search(cr, uid, [('code', '=', 'bid_rate')], limit=1)[0]
        if not middle_rate_type_id or not ask_rate_type_id or not bid_rate_type_id:
            error_msg = _("%s ERROR : \n%s") % (datetime.strftime(datetime.today(),
                                                                 '%Y-%m-%d %H:%M:%S'),
                                               _("There is no currency rate type with code middle_rate or ask_rate or bid_rate !!! No update is possible until this data is defined !!! "))
            raise osv.except_osv(_('Currency update error'), error_msg)
            self.logger.error(error_msg)
            return False

        serv_ids = update_service_obj.search(cr, uid, [('id', 'in', service_ids), ])
        for service in self.pool.get('res.currency.rate.update.service').browse(cr, uid, serv_ids):
            if service.service in ['manual']:
                continue
            main_curr = service.from_currency_id and service.from_currency_id.name.upper() or False
            from_currency_id = service.from_currency_id and \
                               service.from_currency_id.id  or False
            note = service.note or ''
            try:
                # We initalize the class that will handle the request and return a dict of rate
                getter = factory.register(service.service)()
                curr_to_fetch = map(lambda x: x.name.upper(), service.currency_to_update)
                # main currency should be updated to 1., if there is no main currency, we should add it, but not save it in service update currency list
                if not curr_to_fetch:
                    raise osv.except_osv(_('Currency update error'), _("You didn't select any currencies to be refreshed."))
                curr_types_to_fetch = ['middle_rate']
                if service.fetch_bid_rate:
                    curr_types_to_fetch.append('bid_rate')
                if service.fetch_ask_rate:
                    curr_types_to_fetch.append('ask_rate')

                new_values = getter.get_currency_for_period(curr_to_fetch,
                                        main_curr, service.max_delta_days, date_start, date_end,
                                        currency_type_array=curr_types_to_fetch)
                if 'exception' in new_values and new_values['exception']:
                    title = new_values['exception']['title']
                    message = new_values['exception']['message']
                    service.write({'note': message})
                    self.logger.error(message)
                    raise osv.except_osv(title, message)

                for rate_name, rate_data in new_values['data'].items():
                    added_curr = list(set(rate_data.keys()).difference(set(curr_to_fetch)))
                    for curr_name in added_curr:
                        currency_id = currency_obj.search(cr, uid, [('name', '=', curr_name)])[0]
                        # MIDDLE RATE for main currency and/or service currency
                        rate_id = rate_obj.search(cr, uid, [('currency_id.name', '=', curr_name),
                                                            ('name', '=', rate_name),
                                                            ('currency_rate_type_id.code', '=', 'middle_rate'),
                                                            ('update_service_id', '=', service.id),
                                                            ('from_currency_id', '=', from_currency_id),
                                                           ], limit=1)

                        if not rate_id:
                            vals = {
                                        'from_currency_id': from_currency_id,
                                        'currency_id': currency_id,
                                        'currency_rate_type_id': middle_rate_type_id,
                                        'rate': rate_data[curr_name]['middle_rate'],
                                        'name': rate_name,
                                        'update_service_id': service.id,
                                    }
                            rate_obj.create(cr, uid, vals)
                        else:
                            rate_obj.write(cr, uid, rate_id, {'rate': rate_data[curr_name]['middle_rate']})
                        # BID RATE for main currency and/or service currency
                        if service.fetch_bid_rate:
                            rate_id = rate_obj.search(cr, uid, [('currency_id.name', '=', curr_name),
                                                                ('name', '=', rate_name),
                                                                ('currency_rate_type_id.code', '=', 'bid_rate'),
                                                                ('update_service_id', '=', service.id),
                                                                ('from_currency_id', '=', from_currency_id),
                                                               ], limit=1)
                            if not rate_id:
                                vals = {
                                            'from_currency_id': from_currency_id,
                                            'currency_id': currency_id,
                                            'currency_rate_type_id': bid_rate_type_id,
                                            'rate': rate_data[curr_name]['bid_rate'],
                                            'name': rate_name,
                                            'update_service_id': service.id,
                                        }
                                rate_obj.create(cr, uid, vals)
                            else:
                                rate_obj.write(cr, uid, rate_id, {'rate': rate_data[curr_name]['bid_rate']})
                        # ASK RATE for main currency and/or service currency
                        if service.fetch_ask_rate:
                            rate_id = rate_obj.search(cr, uid, [('currency_id.name', '=', curr_name),
                                                                ('name', '=', rate_name),
                                                                ('currency_rate_type_id.code', '=', 'ask_rate'),
                                                                ('update_service_id', '=', service.id),
                                                                ('from_currency_id', '=', from_currency_id),
                                                               ], limit=1)
                            if not rate_id:
                                vals = {
                                            'from_currency_id': from_currency_id,
                                            'currency_id': currency_id,
                                            'currency_rate_type_id': ask_rate_type_id,
                                            'rate': rate_data[curr_name]['ask_rate'],
                                            'name': rate_name,
                                            'update_service_id': service.id,
                                        }
                                rate_obj.create(cr, uid, vals)
                            else:
                                rate_obj.write(cr, uid, rate_id, {'rate': rate_data[curr_name]['ask_rate']})

                    for curr in service.currency_to_update:
                        if curr.name not in rate_data or curr.name in added_curr:
                            continue
                        rate_id = rate_obj.search(cr, uid,
                                      [('currency_id', '=', curr.id),
                                       ('name', '=', rate_name),
                                       ('currency_rate_type_id.code', '=', 'middle_rate'),
                                       ('update_service_id', '=', service.id),
                                       ('from_currency_id', '=', from_currency_id),
                                      ])
                        if rate_id:
                            rate_obj.write(cr, uid, rate_id, {'rate': rate_data[curr.name]['middle_rate'],
                                                              'ratio': rate_data[curr.name]['ratio'],
                                                             })
                        else:
                            vals = {
                                        'from_currency_id': from_currency_id,
                                        'currency_id': curr.id,
                                        'currency_rate_type_id': middle_rate_type_id,
                                        'rate': rate_data[curr.name]['middle_rate'],
                                        'name': rate_name,
                                        'update_service_id': service.id,
                                        'ratio': rate_data[curr.name]['ratio'],
                                    }
                            rate_obj.create(cr, uid, vals)

                        if service.fetch_bid_rate:
                            rate_id = rate_obj.search(cr, uid,
                                          [('currency_id', '=', curr.id),
                                           ('name', '=', rate_name),
                                           ('currency_rate_type_id.code', '=', 'bid_rate'),
                                           ('update_service_id', '=', service.id),
                                           ('from_currency_id', '=', from_currency_id),
                                           ])
                            if rate_id:
                                rate_obj.write(cr, uid, rate_id, {'rate': rate_data[curr.name]['bid_rate'],
                                                                  'ratio': rate_data[curr.name]['ratio']})
                            else:
                                vals = {
                                            'from_currency_id': from_currency_id,
                                            'currency_id': curr.id,
                                            'currency_rate_type_id': bid_rate_type_id,
                                            'rate': rate_data[curr.name]['bid_rate'],
                                            'name': rate_name,
                                            'update_service_id': service.id,
                                            'ratio': rate_data[curr.name]['ratio'],
                                        }
                                rate_obj.create(cr, uid, vals)

                        if service.fetch_ask_rate:
                            rate_id = rate_obj.search(cr, uid,
                                              [('currency_id', '=', curr.id),
                                               ('name', '=', rate_name),
                                               ('currency_rate_type_id.code', '=', 'ask_rate'),
                                               ('update_service_id', '=', service.id),
                                               ('from_currency_id', '=', from_currency_id),
                                              ])
                            if rate_id:
                                rate_obj.write(cr, uid, rate_id,
                                               {'rate': rate_data[curr.name]['ask_rate'],
                                                'ratio': rate_data[curr.name]['ratio']})
                            else:
                                vals = {
                                            'from_currency_id': from_currency_id,
                                            'currency_id': curr.id,
                                            'currency_rate_type_id': ask_rate_type_id,
                                            'rate': rate_data[curr.name]['ask_rate'],
                                            'name': rate_name,
                                            'update_service_id': service.id,
                                            'ratio': rate_data[curr.name]['ratio'],
                                        }
                                rate_obj.create(cr, uid, vals)
                if 'log_message' in new_values and new_values['log_message']:
                    note = note + "%s" % (new_values['log_message'])
                else:
                    note = note + "%s currency updated. \n" % (datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
                service.write({'note': note})
            except Exception, e:
                error_msg = note + "%s ERROR for date %s : %s\n" % (datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'),
                                                                    datetime.strftime(date_start or datetime.today(), '%Y-%m-%d'),
                                                                    e.value)
                service.write({'note': error_msg})
                if hasattr(e, 'name') and hasattr(e, 'value'):
                    raise osv.except_osv(e.name, e.value)
                else:
                    msg = e.args[0]
                    raise osv.except_osv(_('Currency update error'), msg)
        return True


# Error Definition as specified in python 2.6 PEP
class AbstractClassError(Exception):
    def __str__(self):
        return 'Abstract Class'
    def __repr__(self):
        return 'Abstract Class'


class AbstractMethodError(Exception):
    def __str__(self):
        return 'Abstract Method'
    def __repr__(self):
        return 'Abstract Method'


class UnknownClassError(Exception):
    def __str__(self):
        return 'Unknown Class'
    def __repr__(self):
        return 'Unknown Class'


class UnsuportedCurrencyError(Exception):
    def __init__(self, value):
        self.curr = value
    def __str__(self):
        return 'Unsupported currency ' + self.curr
    def __repr__(self):
        return 'Unsupported currency ' + self.curr


class Currency_getter_interface(object):
    "Abstract class of currency getter"
    # remove in order to have a dryer code
    # def __init__(self):
    #    raise AbstractClassError

    log_info = " "
    logger = logging.getLogger(__name__)

    supported_currency_array = [
        'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM',
        'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTN',
        'BWP', 'BYR', 'BZD', 'CAD', 'CDF', 'CHF', 'CLP', 'CNY', 'COP', 'CRC', 'CUP',
        'CVE', 'CYP', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EEK', 'EGP', 'ERN', 'ETB',
        'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ',
        'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD',
        'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW',
        'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LTL', 'LVL',
        'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRO', 'MTL', 'MUR',
        'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD',
        'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD',
        'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLL', 'SOS',
        'SPL', 'SRD', 'STD', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMM', 'TND', 'TOP',
        'TRY', 'TTD', 'TVD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VEB',
        'VEF', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD', 'XDR', 'XOF', 'XPD',
        'XPF', 'XPT', 'YER', 'ZAR', 'ZMK', 'ZWD'
    ]

    # This array will contain the final result
    updated_currency = {}

    def get_currency_for_period(self, currency_array, main_currency, max_delta_days,
                                date_start, date_end, currency_type_array=None):
        """Interface method that will retrieve the currency for period from date_start to date_end,
           default from start of the year. If there is only date_start then only that specific date
           is retrieved.
           This function has to be reinplemented in child"""
        raise AbstractMethodError

    def get_available_currencies(self):
        """Used to fetch available currencies from service"""
        raise AbstractMethodError

    def validate_cur(self, currency):
        """Validate if the currency to update is supported"""
        if currency not in self.supported_currency_array:
            raise UnsuportedCurrencyError(currency)

    def get_url(self, url):
        """Return a string of a get url query"""
        try:
            import urllib
            objfile = urllib.urlopen(url)
            rawfile = objfile.read()
            objfile.close()
            return rawfile
        except ImportError:
            raise osv.except_osv('Error !', self.MOD_NAME + 'Unable to import urllib !')
        except IOError:
            raise osv.except_osv('Error !', self.MOD_NAME + 'Web Service does not exist !')

    def check_rate_date(self, rate_date, max_delta_days):
        """Check date constrains. WARN : rate_date must be of datetime type"""
        days_delta = (datetime.today() - rate_date).days
        if days_delta > max_delta_days:
            return {'exception': {'title': _('Currency update error'),
                                  'message': _('The rate date from the source (%s) is %d days away from today, which is over the update service limit (%d days). Rate not updated in OpenERP.'
                                               ) % (rate_date, days_delta, max_delta_days)}}
        # We always have a warning when rate_date <> today
        rate_date_str = datetime.strftime(rate_date, '%Y-%m-%d')
        if rate_date_str != datetime.strftime(datetime.today(), '%Y-%m-%d'):
            self.logger.warning(_("the rate date from the source (%s) is not today's date") % rate_date_str)
        return None


## Yahoo ###################################################################################
class Yahoo_getter(Currency_getter_interface):
    """Implementation of Currency_getter_factory interface for Yahoo finance service"""

    def get_currency_for_period(self, currency_array, main_currency, max_delta_days,
                                date_start, date_end, currency_type_array=None):
        """implementation of abstract method of Currency_getter_interface"""
        if currency_type_array is None:
            currency_type_array = []
        self.updated_currency = {'data': {}, 'log_message': '', 'exception': {}}

        rate_name = datetime.now().strftime("%Y-%m-%d")
        url = "http://download.finance.yahoo.com/d/quotes.txt?s=%s&f=sl1c1abg" % (','.join(['%(from)s%(to)s=X' % {'from': main_currency, 'to': curr} for curr in currency_array if curr != main_currency]))
        data = {}

        self.logger.debug(_("YAHOO currency rate service : connecting..."))
        rawfile = self.get_url(url)
        rawfile = rawfile.strip()
        lines = rawfile.split("\r\n")

        self.logger.debug(_("YAHOO sent a valid text file"))
        self.logger.debug(_("Supported currencies = ") + str(self.supported_currency_array))

        for line in lines:
            vals = line.replace('N/A', '0.0').strip().split(",")
            if vals[0][4:7].upper() in currency_array:
                tmp_dict = {
                    'ratio': 1.,
                    'middle_rate': float(vals[1]),
                }
                if 'bid_rate' in currency_type_array:
                    tmp_dict['bid_rate'] = float(vals[4])
                if 'ask_rate' in currency_type_array:
                    tmp_dict['ask_rate'] = float(vals[3])
                data[vals[0][4:7].upper()] = tmp_dict

        self.validate_cur(main_currency)
        # Check if supports all of expected currencies
        curr_error_list = [curr for curr in currency_array if curr not in data and curr not in [main_currency]]
        if curr_error_list:
            warning = _('Your tried to update %s %s which are not available from the current service !!!' \
            '\nPlease remove those currencies from the service update list and refresh currencies again.') % \
            ('currency' if len(curr_error_list) == 1 else 'currencies', ','.join(curr_error_list))
            self.updated_currency['log_message'] += warning + '\n'
            self.logger.error(warning)
            # return {'exception': {'title': _('Currency update error'), 'message': warning,} }
        if curr_error_list:
            currency_array = [x for x in currency_array if x not in curr_error_list]
        to_remove = set(data) - set(currency_array)
        for key in to_remove:
            del data[key]

        data[main_currency] = {
            'ratio': 1,
            'middle_rate': 1.,
        }
        if 'bid_rate' in currency_type_array:
            data[main_currency]['bid_rate'] = 1.
        if 'ask_rate' in currency_type_array:
            data[main_currency]['ask_rate'] = 1.

        self.updated_currency['data'][rate_name] = data
        return self.updated_currency

'''
## Admin CH ############################################################################
class Admin_ch_getter(Currency_getter_interface) :
    """Implementation of Currency_getter_factory interface for Admin.ch service"""

    def rate_retrieve(self, dom, ns, curr) :
        """ Parse a dom node to retrieve currencies data"""
        res = {}
        xpath_rate_currency = "/def:wechselkurse/def:devise[@code='%s']/def:kurs/text()"%(curr.lower())
        xpath_rate_ref = "/def:wechselkurse/def:devise[@code='%s']/def:waehrung/text()"%(curr.lower())
        res['rate_currency'] = float(dom.xpath(xpath_rate_currency, namespaces=ns)[0])
        res['rate_ref'] = float((dom.xpath(xpath_rate_ref, namespaces=ns)[0]).split(' ')[0])
        return res

    def get_currency_for_period(self, currency_array, main_currency, max_delta_days, date_start, date_end, currency_type_array=None):
        """implementation of abstract method of Currency_getter_interface"""
        if currency_type_array is None:
            currency_type_array = []

        url='http://www.afd.admin.ch/publicdb/newdb/mwst_kurse/wechselkurse.php'
        #we do not want to update the main currency
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        # Move to new XML lib cf Launchpad bug #645263
        from lxml import etree
        self.logger.debug(_("Admin.ch currency rate service : connecting..."))
        rawfile = self.get_url(url)
        dom = etree.fromstring(rawfile)
        self.logger.debug(_("Admin.ch sent a valid XML file"))
        adminch_ns = {'def': 'http://www.afd.admin.ch/publicdb/newdb/mwst_kurse'}
        rate_date = dom.xpath('/def:wechselkurse/def:datum/text()', namespaces=adminch_ns)[0]
        rate_date_datetime = datetime.strptime(rate_date, '%Y-%m-%d')
        #self.check_rate_date(rate_date_datetime, max_delta_days)
        #we dynamically update supported currencies
        self.supported_currency_array = dom.xpath("/def:wechselkurse/def:devise/@code", namespaces=adminch_ns)
        self.supported_currency_array = [x.upper() for x in self.supported_currency_array]
        self.supported_currency_array.append('CHF')

        self.logger.debug(_("Supported currencies = ") + str(self.supported_currency_array))
        self.validate_cur(main_currency)
        if main_currency != 'CHF':
            main_curr_data = self.rate_retrieve(dom, adminch_ns, main_currency)
            # 1 MAIN_CURRENCY = main_rate CHF
            main_rate = main_curr_data['rate_currency'] / main_curr_data['rate_ref']
        for curr in currency_array :
            self.validate_cur(curr)
            if curr == 'CHF':
                rate = main_rate
            else:
                curr_data = self.rate_retrieve(dom, adminch_ns, curr)
                # 1 MAIN_CURRENCY = rate CURR
                if main_currency == 'CHF' :
                    rate = curr_data['rate_ref'] / curr_data['rate_currency']
                else :
                    rate = main_rate * curr_data['rate_ref'] / curr_data['rate_currency']
            self.updated_currency[curr] = rate
            self.logger.debug(_("Rate retrieved : 1 ") + main_currency + ' = ' + str(rate) + ' ' + curr)
        return self.updated_currency

## ECB getter ############################################################################
class ECB_getter(Currency_getter_interface) :
    """Implementation of Currency_getter_factory interface for ECB service"""

    def rate_retrieve(self, dom, ns, curr) :
        """ Parse a dom node to retrieve currencies data"""
        res = {}
        xpath_curr_rate = "/gesmes:Envelope/def:Cube/def:Cube/def:Cube[@currency='%s']/@rate"%(curr.upper())
        res['rate_currency'] = float(dom.xpath(xpath_curr_rate, namespaces=ns)[0])
        return res

    def get_currency_for_period(self, currency_array, main_currency, max_delta_days, date_start, date_end, currency_type_array=None):
        """implementation of abstract method of Currency_getter_interface"""
        if currency_type_array is None:
            currency_type_array = []

        url='http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        # Important : as explained on the ECB web site, the currencies are
        # at the beginning of the afternoon ; so, until 3 p.m. Paris time
        # the currency rates are the ones of trading day N-1
        # see http://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html

        #we do not want to update the main currency
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        # Move to new XML lib cf Launchpad bug #645263
        from lxml import etree
        self.logger.debug(_("ECB currency rate service : connecting..."))
        rawfile = self.get_url(url)
        dom = etree.fromstring(rawfile)
        self.logger.debug(_("ECB sent a valid XML file"))
        ecb_ns = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01', 'def': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        rate_date = dom.xpath('/gesmes:Envelope/def:Cube/def:Cube/@time', namespaces=ecb_ns)[0]
        rate_date_datetime = datetime.strptime(rate_date, '%Y-%m-%d')
        #self.check_rate_date(rate_date_datetime, max_delta_days)
        #we dynamically update supported currencies
        self.supported_currency_array = dom.xpath("/gesmes:Envelope/def:Cube/def:Cube/def:Cube/@currency", namespaces=ecb_ns)
        self.supported_currency_array.append('EUR')
        self.logger.debug(_("Supported currencies = ") + str(self.supported_currency_array))
        self.validate_cur(main_currency)
        if main_currency != 'EUR':
            main_curr_data = self.rate_retrieve(dom, ecb_ns, main_currency)
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'EUR':
                rate = 1 / main_curr_data['rate_currency']
            else:
                curr_data = self.rate_retrieve(dom, ecb_ns, curr)
                if main_currency == 'EUR':
                    rate = curr_data['rate_currency']
                else:
                    rate = curr_data['rate_currency'] / main_curr_data['rate_currency']
            self.updated_currency[curr] = rate
            self.logger.debug(_("Rate retrieved : 1 ") + main_currency + ' = ' + str(rate) + ' ' + curr)
        return self.updated_currency

## PL NBP ############################################################################
class PL_NBP_getter(Currency_getter_interface) :   # class added according to polish needs = based on class Admin_ch_getter
    """Implementation of Currency_getter_factory interface for PL NBP service"""

    def rate_retrieve(self, dom, ns, curr) :
        """ Parse a dom node to retrieve currencies data"""
        res = {}
        xpath_rate_currency = "/tabela_kursow/pozycja[kod_waluty='%s']/kurs_sredni/text()"%(curr.upper())
        xpath_rate_ref = "/tabela_kursow/pozycja[kod_waluty='%s']/przelicznik/text()"%(curr.upper())
        res['rate_currency'] = float(dom.xpath(xpath_rate_currency, namespaces=ns)[0].replace(',','.'))
        res['rate_ref'] = float(dom.xpath(xpath_rate_ref, namespaces=ns)[0])
        return res

    def get_currency_for_period(self, currency_array, main_currency, max_delta_days, date_start, date_end, currency_type_array=None):
        """implementation of abstract method of Currency_getter_interface"""
        if currency_type_array is None:
            currency_type_array = []
            
        url='http://www.nbp.pl/kursy/xml/LastA.xml'    # LastA.xml is always the most recent one
        #we do not want to update the main currency
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        # Move to new XML lib cf Launchpad bug #645263
        from lxml import etree
        self.logger.debug(_("NBP.pl currency rate service : connecting..."))
        rawfile = self.get_url(url)
        dom = etree.fromstring(rawfile) # If rawfile is not XML, it crashes here
        ns = {} # Cool, there are no namespaces !
        self.logger.debug(_("NBP.pl sent a valid XML file"))

        rate_date = dom.xpath('/tabela_kursow/data_publikacji/text()', namespaces=ns)[0]
        rate_date_datetime = datetime.strptime(rate_date, '%Y-%m-%d')
        #self.check_rate_date(rate_date_datetime, max_delta_days)
        #we dynamically update supported currencies
        self.supported_currency_array = dom.xpath('/tabela_kursow/pozycja/kod_waluty/text()', namespaces=ns)
        self.supported_currency_array.append('PLN')
        self.logger.debug(_("Supported currencies = ") + str(self.supported_currency_array))
        self.validate_cur(main_currency)
        if main_currency != 'PLN':
            main_curr_data = self.rate_retrieve(dom, ns, main_currency)
            # 1 MAIN_CURRENCY = main_rate PLN
            main_rate = main_curr_data['rate_currency'] / main_curr_data['rate_ref']
        for curr in currency_array :
            self.validate_cur(curr)
            if curr == 'PLN':
                rate = main_rate
            else:
                curr_data = self.rate_retrieve(dom, ns, curr)
                # 1 MAIN_CURRENCY = rate CURR
                if main_currency == 'PLN':
                    rate = curr_data['rate_ref'] / curr_data['rate_currency']
                else:
                    rate = main_rate * curr_data['rate_ref'] / curr_data['rate_currency']
            self.updated_currency[curr] = rate
            self.logger.debug(_("Rate retrieved : 1 ") + main_currency + ' = ' + str(rate) + ' ' + curr)
        return self.updated_currency
'''



# End of error definition
class Currency_getter_factory():
    """Factory pattern class that will return
    a currency getter class base on the name passed
    to the register method"""

    _services = {
          # 'NYFB_getter': eval(NYFB_getter),
          # 'Google_getter': eval(Google_getter),
          'Yahoo_getter': eval('Yahoo_getter'),
        }

    def register(self, class_name):
        return Currency_getter_factory._services[class_name]
        # module = Currency_getter_factory._services[class_name].__module__
        # name = Currency_getter_factory._services[class_name].__name__
        # full_class_name = '.'.join((module, name))
        # return eval(Currency_getter_factory._services[full_class_name])

        allowed = [
          'HNB_getter',
          'RBA_getter',
          'SB_getter',
          'Admin_ch_getter',
          'PL_NBP_getter',
          'ECB_getter',
          'NYFB_getter',
          'Google_getter',
          'Yahoo_getter',
        ]
        if class_name in self._get_allowed():
            class_def = eval(class_name)
            return class_def()
        else:
            raise UnknownClassError

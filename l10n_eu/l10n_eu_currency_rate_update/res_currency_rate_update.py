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
from lxml import etree
from osv import osv, fields
from tools.translate import _
from base_base.res.res_currency_rate_update import Currency_getter_factory, Currency_getter_interface, UnknownClassError


class res_currency_rate_update_service(osv.Model):
    """Class that tells for which services which currencies have to be updated"""
    _inherit = "res.currency.rate.update.service"

    def _get_curr_services(self, cr, uid, context=None):
        res = super(res_currency_rate_update_service, self)._get_curr_services(cr, uid, context=context)
        return res + [('ECB_getter', _('European Central Bank'))]

    _columns = {
        'service': fields.selection(_get_curr_services, string='Webservice to use', required=True),
    }

## ECB getter ############################################################################
class ECB_getter(Currency_getter_interface) :
    """Implementation of Currency_getter_factory interface for ECB service"""

    def rate_retrieve(self, dom, ns, curr) :
        """ Parse a dom node to retrieve currencies data"""
        res = {}
        xpath_curr_rate = "/gesmes:Envelope/def:Cube/def:Cube/def:Cube[@currency='%s']/@rate" % (curr.upper())
        res['rate_currency'] = float(dom.xpath(xpath_curr_rate, namespaces=ns)[0])
        return res

    def get_currency_for_period(self, currency_array, main_currency, max_delta_days, date_start, date_end, currency_type_array=None):
        """implementation of abstract method of Currency_getter_interface"""
        if currency_type_array is None:
            currency_type_array = []

        url = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        # Important : as explained on the ECB web site, the currencies are
        # at the beginning of the afternoon ; so, until 3 p.m. Paris time
        # the currency rates are the ones of trading day N-1
        # see http://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html

        # we do not want to update the main currency
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
        # self.check_rate_date(rate_date_datetime, max_delta_days)
        # we dynamically update supported currencies
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

Currency_getter_factory._services['ECB_getter'] = eval('ECB_getter')


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

{
    "name" : "Currency Rate Update",
    "version" : "0.7",
    "author" : "Slobodni programi d.o.o.",
    "website" : "http://www.slobodni-programi.hr",
    "category" : "Financial Management/Configuration",
    "description": """
Import exchange rates from three different sources on the internet :

1. Hrvatska Narodna Banka (HNB)
    Parsed from downloaded text file.
    Takes official rates from http://www.hnb.hr. You can get previous exchange rates by specifying
    different URL's for download based on desired date of exchange rate.
    E.g. http://www.hnb.hr/tecajn/f040412.dat is exchange rate on day 04-04-2012 (in format %d%m%Y)

2. Raiffeisen Bank Austria (RBA) in Croatia
    Parsed from downloaded text file.
    Takes official rates from http://www.rba.hr. You can get previous exchange rates by specifying
    different URL's for download based on desired date of exchange rate.
    E.g. http://www.rba.hr/my/bank/redir.jsp?src=/my/bank/rates/rates_exchange.jsp&language=HR&datum=04.04.2012s&formatTL=ASCII&subref=8
    is exchange rate on day 04-04-2012 (in format %d.%m.%Y)

3. Splitska Banka (SB) - part of Societe Generale
    Parsed from HTML page
    Takes official rates from http://www.splitskabanka.hr. You can get previous exchange rates by specifying
    different URL's for download based on desired date of exchange rate.
    E.g. http://www.splitskabanka.hr/tecajna-lista/arhiva?lista=20120404 is exchange rate on day 04-04-2012 (in format %Y%m%d)

************************************** NEED TO ADAPT FUNCTIONALITY *******************************************************************
4. Admin.ch
   Updated daily, source in CHF.

5. European Central Bank (ported by Grzegorz Grzelak)
   The reference rates are based on the regular daily concertation procedure between
   central banks within and outside the European System of Central Banks,
   which normally takes place at 2.15 p.m. (14:15) ECB time. Source in EUR.
   http://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html

    REMARK: ECB shows date as of day before (e.g. on 22.08.2015 it will show date 21.08.2015),
    which means that max delta days has to be minimum 1... 

6. Yahoo Finance
   Updated daily

7. Polish National Bank (Narodowy Bank Polski) (contribution by Grzegorz Grzelak)
   Takes official rates from www.nbp.pl. Adds rate table symbol in log.
   You should check when rates should apply to bookkeeping. If next day you should 
   change the update hour in schedule settings because in OpenERP they apply from 
   date of update (date - no hours).

************************************** NEED TO ADAPT FUNCTIONALITY *******************************************************************

The update can be set under the company form. You should choose/create default update service for your company.
When creating service you have to choose which currencies you want to update. 
In Accounting under Configuration -> Miscellaneous there is Currency update services view where you can setup your currency update service.
Under the Currency update services is wizard Update currency rate used to update currencies in date range (This operation takes a while
because currency rates for every date have to bre downloaded and parsed individually).
Also, while creating service you can create cron scheduled actions 
Every company has it's set of update services, and there can be only one unique service per company.

Special thanks to main contributor: Grzegorz Grzelak


""",
    "depends" : [
        "base_base",
        # "account",
        # "sale",
    ],
    "init_xml" : [],
    "update_xml" : [
        # "security/ir.model.access.csv",
        # "security/base_security.xml",
        # "data/res_currency_rate_type.xml",
        # "res_currency_rate_update.xml",
        # "res_company_view.xml",
        # "res_bank_view.xml",
        # "res_currency_view.xml",
        # "wizard/res_currency_rate_update_wizard.xml",
    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

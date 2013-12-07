# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_base
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#               http://www.slobodni-programi.hr
#    Contributions: 
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
##############################################################################

from openerp.osv import fields, osv, orm
import tools


class res_company(osv.Model):
    _inherit = 'res.company'
    _columns = {
        'l10n_hr_base_nkd_id': fields.many2one('l10n_hr_base.nkd', 'NKD',
                                               help='Nacionalna klasifikacija djelatnosti'),
        'porezna_uprava': fields.char('Porezna uprava', size=64),
        'porezna_ispostava': fields.char('Porezna ispostava', size=64),
        'br_obveze_mirovinsko': fields.char('Br. obveze mirovinsko', size=32,
                                            help='Broj obveze mirovinskog osiguranja'),
        'br_obveze_zdravstveno': fields.char('Br. obveze zdravstveno', size=32,
                                             help='Broj obveze zdravstvenog osiguranja'),
        'maticni_broj': fields.char('Maticni broj', size=16),
        'podnozje_ispisa': fields.text('Podnozje ispisa'),
        'zaglavlje_ispisa': fields.char('Zaglavlje ispisa', size=512),
        'racun_obrazac': fields.char('Vrsta računa', size=32, help='Upišite "R-1" ili "R-2" '),
        'temeljni_kapital': fields.float('Temeljni kapital', digits=(16, 2)),
        'clanovi_uprave': fields.char('Članovi uprave', size=512),
        'trg_sud': fields.char('Trgovački sud u', size=32),
    }

    _defaults = {
        'racun_obrazac': "Obrazac R-1",
        'podnozje_ispisa': ""
              }

    def on_change_podnozje(self, cr, uid, ids, name, l10n_hr_base_nkd_id, trg_sud, company_registry, maticni_broj, vat, temeljni_kapital, clanovi_uprave, reg=False, context=None):
        val = []
        if name:
            val.append(name + ' za računalne i srodne djelatnosti, trgovinu i usluge')
        if trg_sud:
            val.append(' upisano je u registarski uložak Trgovačkog suda u ' + trg_sud)
        if company_registry:
            val.append(' pod brojem\nMBS: ' + company_registry)
        if maticni_broj:
            val.append(' | MB: ' + maticni_broj)
        if vat:
            val.append(' | VAT: ' + vat)
        if temeljni_kapital:
            val.append('\nTemeljni kapital društva ' + '{:,.2f}'.format(temeljni_kapital) + ' HRK uplaćen je u cijelosti u novcu')
        if clanovi_uprave:
            val.append(' Članovi uprave: ' + clanovi_uprave)
        return {'value': {'podnozje_ispisa': ''.join(val)}}

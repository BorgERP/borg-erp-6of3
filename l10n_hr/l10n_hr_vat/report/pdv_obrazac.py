# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: 
#    mail:   
#    Copyright: 
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

import time
from report import report_sxw
from datetime import datetime

class pdv_obrazac(report_sxw.rml_parse):

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        res = {}
        self.period_ids = []
        period_obj = self.pool.get('account.period')
        res['periods'] = ''
        res['fiscalyear'] = data['form'].get('fiscalyear_id', False)

        if data['form'].get('period_from', False) and data['form'].get('period_to', False):
            self.period_ids = period_obj.build_ctx_periods(self.cr, self.uid, data['form']['period_from'][0], data['form']['period_to'][0])
                    
        if not self.period_ids:
            company_id = self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id'][0]).company_id.id or False                   
            self.period_ids = self.pool.get('account.period').search(self.cr, self.uid, \
                              [('fiscalyear_id', '=', res['fiscalyear'][0]), ('company_id', '=', company_id), ('special', '=', False)])

        periods_l = period_obj.read(self.cr, self.uid, self.period_ids, ['name'])
        for period in periods_l:
            if res['periods'] == '':
                res['periods'] = period['name']
            else:
                res['periods'] += ", "+ period['name']
                                                    
        return super(pdv_obrazac, self).set_context(objects, data, new_ids, report_type=report_type)
          
    def __init__(self, cr, uid, name, context=None):
        super(pdv_obrazac, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_company_name': self._get_company_name,
            'get_company_oib': self._get_company_oib,
            'get_company_nkd': self._get_company_nkd,
            'get_company_ispostava': self._get_company_ispostava,                                    
            'get_value': self._get_value,    
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,           
        })

    def _get_start_date(self):
        start_date = None
        if self.period_ids:
            for period in self.period_ids:
                period_date_start = self.pool.get('account.period').browse(self.cr, self.uid, period).date_start
                if start_date is None:
                    start_date = period_date_start
                if datetime.strptime(period_date_start, '%Y-%m-%d') < datetime.strptime(start_date, '%Y-%m-%d'):
                    start_date = period_date_start
            return start_date
        else:
            return False

    def _get_end_date(self):
        end_date = None
        if self.period_ids:
            for period in self.period_ids:
                period_date_stop = self.pool.get('account.period').browse(self.cr, self.uid, period).date_stop
                if end_date is None:
                    end_date = period_date_stop
                if datetime.strptime(period_date_stop, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
                    end_date = period_date_stop
            return end_date
        else:
            return False        
        
    def _get_company_name(self, data):
        name = self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id']).company_id.name or False
        return name
    
    def _get_company_oib(self, data):
        name = self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id']).company_id.partner_id.vat and \
            self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id']).company_id.partner_id.vat[2:] or False
        return name 
    
    def _get_company_nkd(self, data):
        name = self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id']).company_id.l10n_hr_base_nkd_id and \
            self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id']).company_id.l10n_hr_base_nkd_id.code or False
        return name       
    
    def _get_company_ispostava(self, data):
        name = self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id']).company_id.porezna_ispostava or False
        return name    

    def _get_value(self, data, poz, rbr):
        value = 0.0
        company_id = self.pool.get('account.tax.code').browse(self.cr, self.uid, data['form']['chart_tax_id'][0]).company_id.id or False                   
        periods_ids = tuple(self.period_ids)     
        
        if poz:
            poz_id = self.pool.get('l10n_hr_pdv.report.obrazac').search(self.cr, self.uid, [('position','=',poz),('company_id','=',company_id)])
            if poz_id:
                obrazac = self.pool.get('l10n_hr_pdv.report.obrazac').browse(self.cr, self.uid, poz_id[0])
                base_code_id = obrazac.base_code_id.id
                tax_code_id = obrazac.tax_code_id.id       
                koeficijent = obrazac.base_code_tax_koef   
                if rbr == 2 and not tax_code_id:
                    return value 
            else:
                return value
        else:
            return value
        
        if rbr == 1:
            parent_tax_ids = tuple(self.pool.get('account.tax.code').search(self.cr, self.uid, [('parent_id', 'child_of', [base_code_id])]))
        else:
            parent_tax_ids = tuple(self.pool.get('account.tax.code').search(self.cr, self.uid, [('parent_id', 'child_of', [tax_code_id])]))
        
        self.cr.execute('SELECT COALESCE(SUM(line.tax_amount),0) AS tax_amount \
                    FROM account_move_line AS line, \
                        account_account AS account \
                    WHERE line.state <> %s \
                        AND line.tax_code_id IN %s  \
                        AND line.account_id = account.id \
                        AND account.company_id = %s \
                        AND line.period_id IN %s\
                        AND account.active ', ('draft', parent_tax_ids,
                        company_id, periods_ids,))  
        value_tax = self.cr.fetchone()
        if value_tax:
            value = value_tax[0]
        if rbr == 1:
            if koeficijent == 0:
                value = 0.0
            else:
                value = value / koeficijent                                    
        return value or 0.0
    
report_sxw.report_sxw('report.pdv.obrazac', 'account.tax.code',
    'l10n_hr_vat/report/pdv_obrazac.rml', parser=pdv_obrazac, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
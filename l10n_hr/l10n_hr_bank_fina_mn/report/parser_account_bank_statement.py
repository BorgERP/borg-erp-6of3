# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from tools.translate import _
from report import report_sxw
from account.report.common_report_header import common_report_header

class Parser(report_sxw.rml_parse, common_report_header):
    _statement_total_debt = 0.0
    _statement_total_credit = 0.0
    _statement_total = 0.0

    def __init__(self, cr, uid, name, context):
        self._statement_total_debt = 0.0
        self._statement_total_credit = 0.0
        self._statement_total = 0.0
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'get_total_debt': self._get_total_debt,
            'get_total_credit': self._get_total_credit,
            'get_total': self._get_total,
            'get_bank_name': self._get_bank_name,
            'get_bank_acc_number': self._get_bank_acc_number,
        })

    def _get_lines(self, bank_statement):
        self._statement_total_debt = 0.0
        self._statement_total_credit = 0.0
        self._statement_total = 0.0
        res = []
        for i, line in enumerate(bank_statement.line_ids):
            tmp_row = {
                'code': line.account_id.code or 'NO DATA',
                'name': line.name or 'NO DATA',
                'amount': line.amount or 0.0,
            }
            res.append(tmp_row)
            if line.amount <= 0:
                self._statement_total_debt += line.amount
            else:
                self._statement_total_credit += line.amount
        self._statement_total = self._statement_total_debt + self._statement_total_credit  
        res.sort(key=lambda x: x['code'])

        for i in range(len(res)):
            res[i]['rownum'] = '%d.'%(i + 1)

        return res

    def _get_total_debt(self):
        return self._statement_total_debt or 0.0

    def _get_total_credit(self):
        return self._statement_total_credit or 0.0

    def _get_total(self):
        return self._statement_total or 0.0

    def _get_bank_name(self, statement):
        partner_bank = statement.journal_id.partner_bank_id
        return partner_bank and partner_bank.bank and partner_bank.bank.name or 'NO DATA'

    def _get_bank_acc_number(self, statement):
        partner_bank = statement.journal_id.partner_bank_id
        return partner_bank and partner_bank.acc_number or 'NO DATA'
  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

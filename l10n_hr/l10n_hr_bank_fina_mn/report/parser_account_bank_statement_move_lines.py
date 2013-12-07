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

    def __init__(self, cr, uid, name, context):
        self._statement_total_debt = 0.0
        self._statement_total_credit = 0.0
        self._statement_total = 0.0
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'get_total_debt': self._get_total_debt,
            'get_total_credit': self._get_total_credit,
            'get_bank_name': self._get_bank_name,
            'get_bank_acc_number': self._get_bank_acc_number,
        })

    def _get_lines(self, bank_statement):
        self._statement_total_debt = 0.0
        self._statement_total_credit = 0.0
        res = []
        
        credit_account = bank_statement.journal_id.default_credit_account_id
        credit_row = {
            'code': credit_account.code or 'NO DATA',
            'name': credit_account.name or 'NO DATA',
            'ref': '',
            'debit': 0.0,
            'credit': 0.0,
        }
        debit_account = bank_statement.journal_id.default_debit_account_id
        debit_row = {
            'code': debit_account.code or 'NO DATA',
            'name': debit_account.name or 'NO DATA',
            'ref': '',
            'debit': 0.0,
            'credit': 0.0,
        }

        for move_line in bank_statement.move_line_ids:
            self._statement_total_debt += move_line.credit
            self._statement_total_credit += move_line.debit 
            if move_line.account_id.id == credit_account.id and move_line.credit != 0.0:
                credit_row['debit'] += move_line.debit
                credit_row['credit'] += move_line.credit
            elif move_line.account_id.id == debit_account.id and move_line.debit != 0.0:
                debit_row['debit'] += move_line.debit
                debit_row['credit'] += move_line.credit
            else:
                tmp_row = {
                    'code': move_line.account_id.code or 'NO DATA',
                    'name': move_line.name or 'NO DATA',
                    'ref': move_line.ref or '',
                    'debit': move_line.debit,
                    'credit': move_line.credit,
                }
                res.append(tmp_row)

        ###res.sort(key=lambda x: x['code'])
        res.insert(0, credit_row)
        res.insert(0, debit_row)

        for i in range(len(res)):
            res[i]['rownum'] = '%d.'%(i + 1)

        return res

    def _get_total_debt(self):
        return self._statement_total_debt or 0.0

    def _get_total_credit(self):
        return self._statement_total_credit or 0.0

    def _get_bank_name(self, statement):
        partner_bank = statement.journal_id.partner_bank_id
        return partner_bank and partner_bank.bank and partner_bank.bank.name or 'NO DATA'

    def _get_bank_acc_number(self, statement):
        partner_bank = statement.journal_id.partner_bank_id
        return partner_bank and partner_bank.acc_number or 'NO DATA'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

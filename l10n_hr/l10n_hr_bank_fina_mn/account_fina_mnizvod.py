# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import osv,fields
from tools.translate import _

class account_izvod(osv.osv):
    _name = "account.izvod"
    _description = "Fina MN izvod"
    _columns = {
        'name': fields.binary('Coda file', readonly=True, help="Store the detail of bank statements"),
        'statement_ids': fields.one2many('account.bank.statement', 'izvod_id', 'Generated Bank Statements', readonly=True),
        'note': fields.text('Import log', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True, select=True, help="Bank Journal"),
        'date': fields.date('Date', readonly=True, select=True, help="Import Date"),
        'user_id': fields.many2one('res.users', 'User', readonly=True, select=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True)
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr,uid,context: uid,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.coda', context=c),
    }

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None: 
            context = {}
        res = super(account_coda, self).search(cr, user, args=args, offset=offset, limit=limit, order=order,
                context=context, count=count)
        if context.get('bank_statement', False) and not res:
            raise osv.except_osv('Error', _('Coda file not found for bank statement !!'))
        return res

account_izvod()

class account_bank_statement(osv.osv):
    _inherit = "account.bank.statement"
    _columns = {
        'izvod_id':fields.many2one('account.izvod', 'Izvod'),
    }
    
    def find_partner_and_voucher(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        self.find_partner( cr, uid, ids, context=context)
        self.create_voucher( cr, uid, ids, context=context)
        return False

    def find_partner(self, cr, uid, ids, context=None):
        if context == None:
            context = {}

        journal_obj=self.pool.get('account.journal')
        account_period_obj = self.pool.get('account.period')
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_statement_obj = self.pool.get('account.bank.statement')
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        account_izvod_obj = self.pool.get('account.izvod')
        mod_obj = self.pool.get('ir.model.data')
        partner_obj = self.pool.get('res.partner')

        move_line_obj = self.pool.get('account.move.line')
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')

        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:    
                partner_id   = None   # partner_id search by bank account number
                move_line_id = None   # tražimo točnu stavku po opisu i iznosu
                if line.type == 'supplier': # na teret
                    move_line_id = move_line_obj.search(cr, uid, [('ref'            , '=', line.ref), # isti opis
                                                                  ('reconcile_id'   , '=', False),    # otvorena
                                                                  ('account_id.reconcile', '=', True), # konto se zatvara
                                                                  ('credit'              , '=', line.amount),
                                                                ])
                if line.type == 'customer':
                    move_line_id = move_line_obj.search(cr, uid,[('ref'            , '=', line.ref), 
                                                                 ('reconcile_id'   , '=', False), 
                                                                 ('account_id.reconcile', '=', True),
                                                                 ('debit'               , '=', line.amount),
                                                                ])
                if not move_line_id: #  po opisu i iznosu
                    move_line_id =[]
                    cr.execute("    SELECT m.id FROM account_move_line m " \
                               "  WHERE m.ref = %s      " \
                               "    AND m.reconcile_id IS NULL  " \
                               "    AND m.account_id in (select a.id from account_account a where a.reconcile ='t') " \
                               "   AND abs(m.credit + m.debit) = %s   " ,
                               (line.ref, line.amount)
                               ) 
                    for ml_id in cr.fetchall():
                        move_line_id.append[ml_id]
        
        
                if not move_line_id: # samo po opisu 
                    move_line_id = move_line_obj.search(cr, uid, [('ref'            , '=', line.ref), 
                                                                  ('reconcile_id'   , '=', False), 
                                                                  ('account_id.reconcile', '=', True),
                                                                 ])
                
                if move_line_id and (len(move_line_id) == 1): # only one found 
                    partner_id = move_line_obj.browse(cr, uid, move_line_id[0], context=context).partner_id.id   
        
                #bank account search
                bank_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=', line.imported_bank_acc_no )])
        
                bank = None
                if bank_ids and (len(bank_ids)==1):
                   bank = partner_bank_obj.browse(cr, uid, bank_ids, context=context)
                   if (not partner_id) and bank[0] and bank[0].partner_id:
                       partner_id = bank[0].partner_id.id
                   if partner_id and bank[0] and bank[0].partner_id and  bank[0].partner_id != partner_id:
                       partner_id = None # ambiguous - better 
                   
                account_id = None
                if partner_id and (not move_line_id):
                    partner = partner_obj.browse(cr, uid, partner_id, context=context)
                    if uplata:
                        account_id = partner.property_account_receivable.id
                    else:
                        account_id = partner.property_account_payable.id
                if move_line_id and (len(move_line_id) == 1):
                    account_id = move_line_obj.browse(cr, uid, move_line_id[0], context=context).account_id
                
                partner_id = partner_id or line.partner_id
                account_id = account_id or line.account_id
                            
                #write line
                bank_statement_line_obj.write(cr, uid, line.id, {'partner_id': partner_id, 'account_id': account_id  } , context=context)
                   
        
        return False
    
    def create_voucher(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        return False
        
    def add_bank_accounts_from_lines(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        partner_bank_obj = self.pool.get('res.partner.bank')
        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:
                if not (line.imported_bank_acc_no and line.partner_id):
                    continue
                partner_bank_ids = partner_bank_obj.search(cr, uid, [('acc_number'            , '=', line.imported_bank_acc_no),])
                if partner_bank_ids:
                    continue 
                
                partner_bank = { 
                    'name'       : 'Prema izvodu:' + statement.name,
                    'acc_number' : line.imported_bank_acc_no,
                    'owner_name' : line.partner_id.name,
                    'partner_id' : line.partner_id,
                    'state'      : 'bank',  #?
                    'sequence'   : 10,
                    }
                partner_bank_id = partner_bank_obj.create(cr, uid, partner_bank, context=context)

        return False

account_bank_statement()

class account_bank_statement_line(osv.osv):
    _inherit = "account.bank.statement"
    _columns = {
        'imported_bank_acc_no': fields.char('Imported bank account', size=32),
    }

account_bank_statement_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
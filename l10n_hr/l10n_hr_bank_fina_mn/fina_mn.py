# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Slobodni programi d.o.o 
#    Author: Goran Kliska
#    Inspired by account_coda module
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

class account_bank_statement_line(osv.osv):
    _inherit = "account.bank.statement.line"
    _columns = {
        'bank_acc_no': fields.char('Bank account', size=32),
    }
account_bank_statement_line()

class account_journal(osv.osv):
    _inherit = "account.journal"
    _columns = {
        'partner_id': fields.related('company_id', 'partner_id', type='many2one', relation='res.partner',string='Partner', store=False),
        'partner_bank_id':fields.many2one('res.partner.bank', 'Bank Account', help="Employee bank salary account"),
    }
account_journal()

class l10n_hr_fina_mn(osv.osv):
    _name = "l10n_hr_fina.mn"
    _description = "Object to store Fina mn bank statement file"
    _columns = {
        'name': fields.char('FINA MN Filename',size=128, readonly=True),
        'fina_data': fields.binary('FINA MN File', readonly=True),
        'statement_ids': fields.one2many('account.bank.statement','fina_mn_id','Generated FINA MN Bank Statements', readonly=True),
        'note': fields.text('Import Log', readonly=True),
        'file_creation_date': fields.date('FINA MN Creation Date', readonly=True, select=True),
        'date': fields.date('Import Date', readonly=True, select=True),
        'user_id': fields.many2one('res.users','User', readonly=True, select=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        #'journal_id': fields.many2one('account.journal', 'Journal', readonly=True, select=True, help="Bank Journal"),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr,uid,context: uid,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'l10n_hr_pdv.fina.mn', context=c),
    }

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None: 
            context = {}
        res = super(l10n_hr_fina_mn, self).search(cr, user, args=args, offset=offset, limit=limit, order=order,
                context=context, count=count)
        if context.get('bank_statement', False) and not res:
            raise osv.except_osv('Error', _('FINA MN file not found for bank statement !!'))
        return res
l10n_hr_fina_mn()


class account_bank_statement(osv.osv):
    _inherit = "account.bank.statement"
    _columns = {
        'fina_mn_id':fields.many2one('l10n_hr_fina.mn', 'FINA Izvod'),
    }

    def _get_open_move_line_ids_by_ref(self, cr, uid, line, context=None):
        move_line_obj = self.pool.get('account.move.line')
        
        move_line_ids = None  
        if line.ref:  
            if line.type == 'customer':
                move_line_ids = move_line_obj.search(cr, uid,[('ref'            , '=', line.ref), 
                                                             ('reconcile_id'   , '=', False), 
                                                             ('account_id.reconcile', '=', True),
                                                             ('debit'               , '=', line.amount),
                                                            ])
            if line.type == 'supplier':
                move_line_ids = move_line_obj.search(cr, uid, [('ref'            , '=', line.ref),
                                                              ('reconcile_id'   , '=', False),    
                                                              ('account_id.reconcile', '=', True),
                                                              ('credit'              , '=', line.amount),
                                                            ])
    
            if not move_line_ids: 
                move_line_ids = move_line_obj.search(cr, uid, [('ref'            , '=', line.ref), 
                                                              ('reconcile_id'   , '=', False), 
                                                              ('account_id.reconcile', '=', True),
                                                             ])
        return move_line_ids


    
    def partner_and_voucher(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        self.find_partner_and_account( cr, uid, ids, context=context)
        self.propose_vouchers( cr, uid, ids, context=context)
        return False

    def find_partner_and_account(self, cr, uid, ids, context=None):
        if context == None:
            context = {}

        journal_obj=self.pool.get('account.journal')
        account_period_obj = self.pool.get('account.period')
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_statement_obj = self.pool.get('account.bank.statement')
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        mod_obj = self.pool.get('ir.model.data')
        partner_obj = self.pool.get('res.partner')

        move_line_obj = self.pool.get('account.move.line')
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')

        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:    
                partner_id   = None   
                
                move_line_ids = self._get_open_move_line_ids_by_ref(cr, uid, line, context=context) 
                if move_line_ids and (len(move_line_ids) == 1): 
                    partner_id = move_line_obj.browse(cr, uid, move_line_ids[0], context=context).partner_id.id   
        
                bank_ids = None
                if line.bank_acc_no:
                    bank_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=', line.bank_acc_no )])
        
                bank = None
                if bank_ids and (len(bank_ids)==1):
                   bank = partner_bank_obj.browse(cr, uid, bank_ids, context=context)
                   if (not partner_id) and bank[0] and bank[0].partner_id:
                       partner_id = bank[0].partner_id.id
                   if partner_id and bank[0] and bank[0].partner_id and bank[0].partner_id.id != partner_id:
                       partner_id = None 
                   
                account_id = None
                if partner_id and (not move_line_ids): 
                    partner = partner_obj.browse(cr, uid, partner_id, context=context)
                    if line.type == 'customer':
                        account_id = partner.property_account_receivable.id
                    else:
                        account_id = partner.property_account_payable.id
                if move_line_ids and (len(move_line_ids) == 1): 
                    account_id = move_line_obj.browse(cr, uid, move_line_ids[0], context=context).account_id.id
                
                partner_id = partner_id or (line.partner_id and line.partner_id.id) 
                account_id = account_id or (line.account_id and line.account_id.id)  
                            
                if (not line.partner_id) or partner_id != (line.partner_id and line.partner_id.id):
                    bank_statement_line_obj.write(cr, uid, line.id, {'partner_id': partner_id,
                                                                     'account_id': account_id  } , context=context)
        return True

    
    def propose_vouchers(self, cr, uid, ids, context=None):
        if context == None:
            context = {}

        move_line_obj = self.pool.get('account.move.line')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
            
        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:    
                if (line.voucher_id) or (not line.partner_id):  
                    continue
                move_line_ids = self._get_open_move_line_ids_by_ref(cr, uid, line, context=context)
                voucher_id = None
                if move_line_ids and (len(move_line_ids) == 1) and line.partner_id.id:
                    context.update({'move_line_ids': move_line_ids})

                    voucher_partner = voucher_obj.onchange_partner_id(cr, uid, [],
                                                     partner_id  = line.partner_id.id,
                                                     journal_id  = statement.journal_id.id,
                                                     price       = abs(line.amount),
                                                     currency_id = statement.journal_id.company_id.currency_id.id,
                                                     ttype       = line.type == 'supplier' and 'payment' or 'receipt',
                                                     date        = line.date,
                                                     context=context
                                                            )

                    voucher_res = { 
                                'type'       : (line.type == 'supplier' and 'payment' or 'receipt'),
                                'name'       : line.name,
                                'partner_id' : line.partner_id.id,
                                'journal_id' : statement.journal_id.id, 
                                'account_id' : voucher_partner.get('account_id', statement.journal_id.default_credit_account_id.id),
                                'company_id' : statement.journal_id.company_id.id,
                                'currency_id': statement.journal_id.company_id.currency_id.id,
                                'date'       : line.date,
                                'amount'     : abs(line.amount),
                                'period_id'  : statement.period_id.id,
                                }

                    voucher_line_dict =  False
                    if voucher_partner['value']['line_ids']:
                        for line_dict in voucher_partner['value']['line_ids']:
                            move_line = move_line_obj.browse(cr, uid, line_dict['move_line_id'], context)
                            if move_line_ids[0] == move_line.id: 
                                voucher_line_dict = line_dict
                                account_id = move_line.account_id.id

                            if voucher_line_dict:
                                voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)
                                voucher_line_dict.update({'voucher_id':voucher_id})
                                voucher_line_dict.update({'amount':abs(line.amount)})
                                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                                bank_statement_line_obj.write(cr, uid, line.id, {'voucher_id': voucher_id  } , context=context)
                                break
           
        return False


    def bank_accounts_from_lines(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_obj         = self.pool.get('res.bank')
        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:
                if not (line.bank_acc_no and line.partner_id):
                    continue
                partner_bank_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=', line.bank_acc_no),])
                if partner_bank_ids:
                    continue 
                bank_id = bank_obj.search(cr, uid, [('code' , '=', line.bank_acc_no[:7]),])
                if bank_id: 
                    partner_bank = { 
                        'name'       : 'Izvor: izvod ' + statement.name,
                        'acc_number' : line.bank_acc_no,
                        'owner_name' : line.partner_id.name,
                        'partner_id' : line.partner_id.id,
                        'state'      : 'bank',  
                        'sequence'   : 100,
                        'bank'       : bank_id[0],
                        }
                    partner_bank_id = partner_bank_obj.create(cr, uid, partner_bank, context=context)
        return False

account_bank_statement()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
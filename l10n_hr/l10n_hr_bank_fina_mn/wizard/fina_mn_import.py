# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import base64

from osv import fields, osv
from tools.translate import _

class l10n_hr_fina_mn_import(osv.osv_memory):

    row_defs={ 
     '0':{
        'Broj podruznice_FINA-e':      [  1,   5], 
        'Tip kodne stranice':          [  6,   6], 
        'Vrsta digitalnog potpisa':    [  7,   7],
        'Datum obrade (DDMMYY)':       [  8,  13],
        'Id broj primatelja izvatka':  [ 14,  20], 
        'Vrsta izvatka = 250':         [ 21,  23], 
        'Rezerva':                     [ 23, 191], 
        'Prosireni datum':             [192, 199], 
        'Rezerva':                     [200, 249], 
        'Tip sloga':                   [250, 250], 
         },
    '3': { 
        'Racun korisnika izvatka':    [  1,  18],
        'Naziv korisnika izvatka':    [ 19,  53],
        'Redni broj izvatka':         [ 54,  56],
        'Datum izvatka':              [ 57,  62],
        'Broj pretinca':              [ 63,  67],
        'R.br. grupe mag. nositelju': [ 68,  71],
        'Naziv FINA-e':               [ 72, 106],
        'Broj dnevnog presjeka':      [107, 109],
        'Tip kodne stranice':         [110, 110],
        'Vrsta digitalnog potpisa':   [111, 111],
        'Vrsta izvatka = 250':        [112, 114],
        'Vodeci broj banke':          [115, 121],
        'Oznaka konstrukcije racuna': [122, 122],
        'IBAN – oznaka ziro racuna':  [123, 126],
        'BIC- Id banke':              [127, 134], 
        'Rezerva':                    [135, 191], 
        'Prosireni datum':            [192, 199],
        'Rezerva':                    [200, 249],
        'Tip sloga':                  [250, 250],
        },
    '5':{ 
        'Oznaka transakcije':    [  1,   2],
        'Racun vjer/duz':        [  3,  20],
        'Naziv vjer/duz':        [ 21,  55],
        'Mjesto vjer/duz':       [ 56,  65],
        'Iznos':                 [ 66,  78],
        'Pnbr zaduzenja':        [ 79, 102],
        'Pnbr odobrenja':        [103, 126],
        'Vezna oznaka':          [127, 128],
        'Opis svrhe doznake':    [129, 164],
        'Oznaka konstuk racuna': [165, 165],
        'Broj za reklamaciju':   [166, 197],
        'VBDI vjer/duz' :        [198, 204],
        'Vrsta prihvata':        [205, 207],
        'Izvor dokumenta':       [208, 210],
        'Datum valute':          [211, 218],
        'Rezerva':               [219, 249],
        'Tip sloga':             [250, 250],
        }, 
    '7':{ 
        'Racun korisnika izvatka':      [  1,  18],
        'Naziv korisnika izvatka':      [ 19,  53],
        'Redni broj izvatka':           [ 54,  56],
        'Datum izvatka':                [ 57,  62],
        'Prethodni saldo':              [ 63,  77],
        'Ukupni dnevni dug. promet':    [ 78,  92],
        'Ukupni dnevni pot. promet':    [ 93, 107],
        'Novi saldo':                   [108, 122],
        'R.br. grupe mag.nositelju':    [123, 126],
        'Broj stavaka u grupi':         [127, 132],
        'Naziv FINA-e':                 [133, 167],
        'Broj dnevnog presjeka':        [168, 170],
        'Predznak pocetnog stanja':     [171, 171],
        'Predznak novog stanja':        [172, 172],
        'Razlika na dugovnoj stavci':   [173, 173],
        'Razlika na potraznoj stavci':  [174, 174],
        'Rezerva':                      [175, 191],
        'Prosireni datum':              [192, 199],
        'Vodeci broj banke':            [200, 206],
        'Oznaka konstrukcije racuna':   [207, 207],
        'Rezerva':                      [208, 249],
        'Tip sloga':                    [250, 250],
        },
    '9': { 
        'Broj podruznice_FINA-e':       [  1,   5],
        'Rezerva':                      [  6,   7],
        'Datum obrade':                 [  8,  13],
        'Id. broj primatelja izvatka':  [ 14,  20],
        'Ukupan broj grupa/paket':      [ 21,  25],
        'Ukupan broj slog/paket':       [ 26,  31],
        'Rezerva':                      [ 32, 191],
        'Prosireni datum':              [192, 199],
        'Rezerva':                      [200, 249],
        'Tip sloga':                    [250, 250],
        },
    }        

    _name = 'l10n_hr_fina.mn.import'
    _description = 'FINA MN datoteke izvoda'
    _rec_name = 'file_name'
    _columns = {
            'journal_id': fields.many2one('account.journal', 'Bank Journal', required=True),
            'def_payable': fields.many2one('account.account', 'Default Payable Account', domain=[('type', '=', 'payable')], required=True, help= 'Set here the payable account that will be used, by default, if the partner is not found'),
            'def_receivable': fields.many2one('account.account', 'Default Receivable Account', domain=[('type', '=', 'receivable')], required=True, help= 'Set here the receivable account that will be used, by default, if the partner is not found',),
            'awaiting_account': fields.many2one('account.account', 'Default Account for Unrecognized Movement', domain=[('type', '=', 'liquidity')], required=True, help= 'Set here the default account that will be used, if the partner is found but does not have the bank account, or if he is domiciled'),
            'fina_data': fields.binary('FINA MN File', required=True),
            'file_name': fields.char('CODA Filename', size=128,),
            'note':fields.text('Log'),
            'state': fields.selection((('choose','choose'),('finish','finish'))),
    }
    _defaults = {
        'state': lambda *a: 'choose',
    }

    def create(self, cr, uid, vals, context={}):
        if context is None:
            context = {}
        context.update(bin_raw=True)
        return super(l10n_hr_fina_mn_import, self).create(cr, uid, vals, context)


    
    def parse_mn_file(self, cr, uid, ids, context=None):

        journal_obj=self.pool.get('account.journal')
        account_period_obj = self.pool.get('account.period')
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_statement_obj = self.pool.get('account.bank.statement')
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.record')
        mod_obj = self.pool.get('ir.model.data')
        move_line_obj = self.pool.get('account.move.record')
        partner_obj = self.pool.get('res.partner')

        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0] 

        codafile = base64.decodestring( data['fina_data'] ) 
        journal = journal_obj.browse(cr, uid, data['journal_id'], context=context)

        def_pay_acc = data['def_payable']
        def_rec_acc = data['def_receivable']

        err_log = u"Greske:\n------\n"
        nb_err=0
        std_log='\n'
        str_log1 = u"Datoteka izvoda ucitana:  "

        recordlist = unicode(codafile.decode('windows-1250')).split('\n')
        #recordlist.pop() #remove last row?
                
        file_start, file_end, statements = [], [], []

        def parse_mn_row(row_type, row):
            row_def = self.row_defs[row_type]
            res = {}.fromkeys(row_def,None)
            for key in row_def.keys():
                #res[key] = row[ row_def[key][0]-1 : row_def[key][1] ].decode('windows-1250') 
                res[key] = row[ row_def[key][0]-1 : row_def[key][1] ] 
            return res       
        
        for record in recordlist:
            if len(record) == 0:
                continue
            if len(record) not in (250,251):
                raise osv.except_osv(_('Greska kod ucitavanja izvoda!'),_('Redak nije prepoznat (250) %s') % (record,))
            row_type = record[249]
            row = parse_mn_row ( row_type, record )
            if row_type == '0':
                file_start.append( row.copy() )
            elif row_type == '3':
                statements.append(
                               {'stmt_start' : row.copy(),
                                'stmt_lines' : [],
                                'stmt_end'  : None,
                                })
            elif row_type == '5':
                statements[-1]['stmt_lines'].append(row.copy() )
            elif row_type == '7':
                statements[-1]['stmt_end'] = row.copy()
            elif row_type == '9':
                file_end.append( row.copy() )
            else:    
                raise osv.except_osv(_('Greska kod ucitavanja izvoda!'),_('Redak nije prepoznat (%s) %s') % (row_type, row,))

        #TODO Check for errors in file    

        def strToDate(date_str):
            return time.strftime("%Y/%m/%d", time.strptime(date_str, "%d%m%Y"))

        def str2float(str):
            try:
                return float(str)
            except:
                return 0.0
        
        statement_ids = []
        for stmt in statements:
            statement_date = strToDate( stmt['stmt_start']['Prosireni datum'] )
            period_id = account_period_obj.search(cr, uid, [('date_start', '<=', statement_date ), ('date_stop', '>=', statement_date)])[0]

            balance_before    = str2float( stmt['stmt_end']['Prethodni saldo'] ) /100
            if stmt['stmt_end']['Predznak pocetnog stanja']=='-':
                balance_before *= -1
            balance_end_real = str2float( stmt['stmt_end']['Novi saldo']      ) /100
            if stmt['stmt_end']['Predznak novog stanja']=='-':
                balance_end_real *= -1
            
            name =  stmt['stmt_start']['Redni broj izvatka'] \
                  + ' - '+ stmt['stmt_start']['Broj dnevnog presjeka']  

            bank_st_id = bank_statement_obj.search(cr, uid, [('name', '=', name )])
            if bank_st_id:
                raise osv.except_osv(_('Greska!'),_('Izvod %s vec postoji! ') % (name,))

            bank_st_id =bank_statement_obj.create(cr, uid, {
                'journal_id': data['journal_id'][0],
                'date'      : statement_date,
                'period_id' : period_id,
                'balance_before'   : balance_before, #todo -addfield
                'balance_end_real': balance_end_real,
                'state': 'draft',
                'name' : name,
                 })
            statement_ids.append(bank_st_id)

            for record in stmt['stmt_lines']:
                name = record['Naziv vjer/duz'].strip() + ' :' + record['Opis svrhe doznake'].strip()
                amount= str2float( record['Iznos'] ) /100
                if record['Oznaka transakcije'] in ['10',]:
                    note = 'NA TERET'
                    type = 'supplier'
                    amount *= -1
                elif record['Oznaka transakcije'] in ['20',]:
                    note = 'U KORIST'
                    type = 'customer'
                elif record['Oznaka transakcije'] in ['30',]: 
                    stdlog += 'Nije izvršeno zbog nedostatka sredstava na računu platitelja: \n ' \
                             + line_name
                    continue 
                elif record['Oznaka transakcije'] in ['40',]: 
                    stdlog += 'Nije izvršeno zbog nedostatka novca na zahtjev sudionika: \n ' \
                             + line_name
                    continue 
                else:
                    raise osv.except_osv(__('Greska kod ucitavanja izvoda!'),_('Transakcija nije prepoznata %s') % (record['Oznaka transakcije'],))

                #?record['Vezna oznaka']?
                bank_acc_no = record['VBDI vjer/duz'].strip()+'-'+record['Racun vjer/duz'].strip() 
                
                note +=  u'\nRačun vjer./duž.:'        + bank_acc_no \
                        +u'\nPoziv na br. odobrenja: ' + record['Pnbr odobrenja'].strip() \
                        +u'\nPartner: '                + record['Naziv vjer/duz'] \
                        +u'\nPoziv na br. zaduženja: ' + record['Pnbr zaduzenja'] \
                        +u'\nBroj za reklamaciju: '    + record['Broj za reklamaciju'] \
                        +u'\nVrsta prihvata: '         + record['Vrsta prihvata']
                 

                bank_statement_line_obj.create(cr, uid, {
                               'name'        : name,
                               'date'        : strToDate( record['Datum valute'] ),
                               'amount'      : amount,
                               'type'        : type,
                               'account_id'  :   (type == 'supplier' and data['def_payable'][0]) 
                                              or (type == 'customer' and data['def_receivable'][0])
                                              or  data['awaiting_account'],
                               'statement_id': bank_st_id,
                               'note'        : note,
                               'ref'         : record['Pnbr odobrenja'].strip(),
                               'bank_acc_no' : bank_acc_no 
                               })

                
        self.pool.get('l10n_hr_fina.mn').create(
            cr,
            uid, {
                'name': codafile,
                'statement_ids': [(6, 0, statement_ids,)],
                'note': std_log,
                'journal_id': data['journal_id'][0],
                'date': time.strftime("%Y-%m-%d"),
                'user_id': uid,
                })
        
        # try to find partner and reconcile
        
        #bank_statement_obj.guess_partner_and_voucher(cr, uid, [bank_st_id], context=context)
        bank_statement_obj.partner_and_voucher(cr, uid, [bank_st_id], context=context)
        
        
        test = ''
        test = str_log1 + std_log + err_log
        context.update({ 'statment_ids': statement_ids})
        model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'account.bank.statement.form.fina_mn')], context=context)
        #TODOresource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return self.write(cr, uid, [data['id']], {'note': test, 'state':'finish'}, context=context)

        """
        return {
            'name': _('Result'),
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.mnizvod.import',
            'view_id': False,
            'target': 'new',
            'views': [(resource_id, 'form')],
            'context': context,
            'type': 'ir.actions.act_window',
        }"""
                

    def action_open_window(self, cr, uid, data, context=None):
        if context is None:
            context = {}

        return {
            'domain':"[('id','in',%s)]"%(context.get('statment_ids', False)),
            'name': 'Statement',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.bank.statement',
            'view_id': False,
            'type': 'ir.actions.act_window',
    }

l10n_hr_fina_mn_import()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
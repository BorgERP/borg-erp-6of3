# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Marko Tribuson @Infokom.hr
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

from osv import fields, osv

class l10n_hr_pdv_report_obrazac(osv.osv):
    _name = 'l10n_hr_pdv.report.obrazac'
    _description = 'Postavke ispisa PDV obrasca'
        
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),

        'position': fields.selection([
            ('A','Redak 1'),
            ('I','Redak 2'),
            ('I1','Redak 3'),            
            ('I2','Redak 4'),
            ('I21','Redak 5'),
            ('I22','Redak 6'),
            ('I23','Redak 7'),
            ('I24','Redak 8'),
            ('I3','Redak 9'),
            ('II','Redak 10'),
            ('II1','Redak 11'),         
            ('II2','Redak 12'),
            ('II3','Redak 13'),               
            ('II4','Redak 14'),
            ('III','Redak 15'),               
            ('III1','Redak 16'),
            ('III2','Redak 17'),               
            ('III3','Redak 18'),            
            ('III4','Redak 19'),               
            ('III5','Redak 20'),            
            ('III6','Redak 21'),               
            ('III7','Redak 22'),            
            ('III8','Redak 23'), 
            ('IV','Redak 24'), 
            ('V','Redak 25'), 
            ('VI','Redak 26')                                
            ],'Pozicija', select=True, required=True),
        'base_code_id': fields.many2one('account.tax.code', 'Osnovica', required=True),
        'base_code_tax_koef': fields.float('Stopa',  help="Stopa za izračun. Upisati stopu po kojoj se izračunava osnovica iz upisane šifre poreza."), 
        'tax_code_id': fields.many2one('account.tax.code', 'Porez', required=False),               
    }
    
    _sql_constraints = [
        ('l10n_hr_pdv_report_obrazac_uniq', 'unique (company_id,position)', 'Isti redak se smije korisiti samo jednom za jednu tvrtku!')
    ]
    
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]

    _defaults = {
        'company_id': _default_company,
        'base_code_tax_koef': 1.0,
    }
    
    
l10n_hr_pdv_report_obrazac()

class l10n_hr_pdv_report_knjiga(osv.osv):
    _name = 'l10n_hr_pdv.report.knjiga'
    _description = 'Postavke ispisa URA-IRA'
    _rec_name = 'id'
        
    _columns = {
#        'report_type': fields.selection([
#            ('ira','Knjiga IRA'),      
#            ('ura','Knjiga URA'),                                 
#            ],'Ispis', select=True, required=True),
        'id': fields.integer('Id', readonly=True),
        'knjiga_id': fields.many2one('l10n_hr_pdv.knjiga','Porezna knjiga', select=True, required=True),
        'position': fields.selection([
            ('6','Stupac 6'),
            ('7','Stupac 7'),
            ('8','Stupac 8'),
            ('9','Stupac 9'),
            ('10','Stupac 10'),
            ('11','Stupac 11'),         
            ('12','Stupac 12'),
            ('13','Stupac 13'),               
            ('14','Stupac 14'),
            ('15','Stupac 15'),               
            ('16','Stupac 16'),
            ('17','Stupac 17'),               
            ('18','Stupac 18'),                                         
            ],'Pozicija', select=True, required=True),               
        'line_ids': fields.one2many('l10n_hr_pdv.report.knjiga.stavka', 'report_knjiga_id', 'Stavke poreza'),                
    }

    _sql_constraints = [
        ('l10n_hr_pdv_report_knjiga_uniq', 'unique (knjiga_id, position)', 'Isti redak se smije koristi samo jednom po ispisu !')
    ]
    
l10n_hr_pdv_report_knjiga()

class l10n_hr_pdv_report_knjiga_stavka(osv.osv):
    _name = 'l10n_hr_pdv.report.knjiga.stavka'
    _description = 'Postavke ispisa URA-IRA po porezima'
    _rec_name='tax_code_id'
        
    _columns = {   
        'report_knjiga_id': fields.many2one('l10n_hr_pdv.report.knjiga', 'Ispis knjige', required=True),                           
        'tax_code_id': fields.many2one('account.tax.code', 'Porez', required=True),        
        'tax_code_koef': fields.float('Stopa',  required=True, help="Stopa za izračun. Upisati stopu po kojoj se izračunava osnovica iz upisane šifre poreza."),       
    }
    
    _defaults = {
        'tax_code_koef': 1.0,
    }    
l10n_hr_pdv_report_knjiga_stavka()
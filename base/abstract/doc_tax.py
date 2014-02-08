
TODO

class document_tax(osv.Abstract):
    _name = "document.tax"
    _description = "Document Tax"

    def _count_factor(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice_tax in self.browse(cr, uid, ids, context=context):
            res[invoice_tax.id] = {
                'factor_base': 1.0,
                'factor_tax': 1.0,
            }
            if invoice_tax.amount <> 0.0:
                factor_tax = invoice_tax.tax_amount / invoice_tax.amount
                res[invoice_tax.id]['factor_tax'] = factor_tax

            if invoice_tax.base <> 0.0:
                factor_base = invoice_tax.base_amount / invoice_tax.base
                res[invoice_tax.id]['factor_base'] = factor_base

        return res

    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice Line', ondelete='cascade', select=True),
        'name': fields.char('Tax Description', size=64, required=True),
        'account_id': fields.many2one('account.account', 'Tax Account', required=True, domain=[('type', '<>', 'view'), ('type', '<>', 'income'), ('type', '<>', 'closed')]),
        'base': fields.float('Base', digits_compute=dp.get_precision('Account')),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'manual': fields.boolean('Manual'),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of invoice tax."),
        'base_code_id': fields.many2one('account.tax.code', 'Base Code', help="The account basis of the tax declaration."),
        'base_amount': fields.float('Base Code Amount', digits_compute=dp.get_precision('Account')),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration."),
        'tax_amount': fields.float('Tax Code Amount', digits_compute=dp.get_precision('Account')),
        'company_id': fields.related('account_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'factor_base': fields.function(_count_factor, string='Multipication factor for Base code', type='float', multi="all"),
        'factor_tax': fields.function(_count_factor, string='Multipication factor Tax code', type='float', multi="all")
    }

    def base_change(self, cr, uid, ids, base, currency_id=False, company_id=False, date_invoice=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency = False
        factor = 1
        if ids:
            factor = self.read(cr, uid, ids[0], ['factor_base'])['factor_base']
        if company_id:
            company_currency = company_obj.read(cr, uid, [company_id], ['currency_id'])[0]['currency_id'][0]
        # KGB TODO force ratio maybe?
        if currency_id and company_currency:
            base = cur_obj.compute(cr, uid, currency_id, company_currency, base * factor,
                                   context={'date': date_invoice or time.strftime('%Y-%m-%d'),
                                            # 'force_currency_inv_rate': inv.ccurrency_rate,
                                            }, round=False)
        return {'value': {'base_amount':base}}

    def amount_change(self, cr, uid, ids, amount, currency_id=False, company_id=False, date_invoice=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency = False
        factor = 1
        if ids:
            factor = self.read(cr, uid, ids[0], ['factor_tax'])['factor_tax']
        if company_id:
            company_currency = company_obj.read(cr, uid, [company_id], ['currency_id'])[0]['currency_id'][0]
        # KGB TODO force ratio maybe?
        if currency_id and company_currency:
            amount = cur_obj.compute(cr, uid, currency_id, company_currency, amount * factor,
                                      context={'date': date_invoice or time.strftime('%Y-%m-%d'),
                                              # 'force_currency_inv_rate': inv.ccurrency_rate,
                                               },
                                      round=False)
        return {'value': {'tax_amount': amount}}

    _order = 'sequence'
    _defaults = {
        'manual': 1,
        'base_amount': 0.0,
        'tax_amount': 0.0,
    }
    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit * (1 - (line.discount or 0.0) / 100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id)['taxes']:
                tax['price_unit'] = cur_obj.round(cr, uid, cur, tax['price_unit'])
                val = {}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = tax['price_unit'] * line['quantity']
                # KGB force currency rate
                if inv.type in ('out_invoice', 'in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'],
                                                          context={'date': inv.date_invoice or time.strftime('%Y-%m-%d'),
                                                                   'force_currency_inv_rate': inv.ccurrency_rate,
                                                                    }, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'],
                                                         context={'date': inv.date_invoice or time.strftime('%Y-%m-%d'),
                                                                  'force_currency_inv_rate': inv.ccurrency_rate,
                                                                  },
                                                         round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'],
                                                           context={'date': inv.date_invoice or time.strftime('%Y-%m-%d'),
                                                                    'force_currency_inv_rate': inv.ccurrency_rate,
                                                                    },
                                                           round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'],
                                                         context={'date': inv.date_invoice or time.strftime('%Y-%m-%d'),
                                                                  'force_currency_inv_rate': inv.ccurrency_rate,
                                                                  },
                                                         round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped

    def move_line_get(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_tax WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            if not t['amount'] \
                    and not t['tax_code_id'] \
                    and not t['tax_amount']:
                continue
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['amount'],
                'quantity': 1,
                'price': t['amount'] or 0.0,
                'account_id': t['account_id'],
                'tax_code_id': t['tax_code_id'],
                'tax_amount': t['tax_amount']
            })
        return res


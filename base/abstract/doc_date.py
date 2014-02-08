# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Goran Kliska
#    mail:   goran.kliska AT slobodni-programi.hr
#    Copyright (C) 2012- Slobodni programi d.o.o., Zagreb, www.slobodni-programi.hr
#    Contributions:
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


    def _get_dates_field_map(self, cr, uid, context=None):
        return {
                'account_invoice': {'date':  ['date_invoice'],
                                    'other': ['date_confirm',
                                              'create_date',  # datetime
                                              'date_delivery',
                                              'date_due',
                                              'date_invoice',
                                              'vrijeme_izdavanja',  # datetime
                                              'write_date',]
                                    },

                'sale_order':      {'date':  ['date_order'],
                                    'other': ['create_date',  # datetime
                                              'date_confirm',]
                                    },


                'purchase_order':  {'date':  ['date_order'],
                                    'other': ['date_approve',
                                              'minimum_planned_date',]
                                    },
                'purchase_order_line': {'date':  ['date_order'],
                                        'other': ['date_planned',]
                                       },


                'stock_move':       {'date':  ['date'],  # datetime
                                     'other': ['create_date',  # datetime
                                               'date_expected',] # datetime
                                     },

                'procurement_order': {'other': ['date_close',  # datetime
                                                'date_planned',] # datetime
                                     },

                'account_move_line': {'date':  ['date'],
                                      'other': ['date_created',
                                                'date_maturity',]
                                     },

                'account_analytic_line': {'date':  ['date'],
                                          },
                }

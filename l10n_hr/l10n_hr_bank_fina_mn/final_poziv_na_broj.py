# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Goran Kliska
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#                http://www.slobodni-programi.hr
#    Contributions:
#    Documentation: http://www.fina.hr/Default.aspx?sec=1266
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

#import logging

def mod11ini(value):
    '''
    Compute mod11ini
    '''
    length = len(value)
    sum = 0
    for i in xrange(0, length):
        sum += int(value[length - i - 1]) * (i + 2)
    res = sum % 11
    if res > 1:
        res = 11 - res
    else:
        res = 0
    return str(res)

def iso7064(value):
    """
    Compute ISO 7064, Mod 11,10
    """
    t = 10
    for i in value:
        c = int(i)
        t = (2 * ((t + c) % 10 or 10)) % 11
    return str((11 - t) % 10)

def mod11p7(value):
     length = len(value)
     ### if 1.st digit differs from three - ERROR
     #if not return_check_digit and int(value[0]) != 3:
     #    return False
     sum = 0
     for i in xrange(0, length):
         sum += int(value[length - i - 1]) * ((i % 6) + 2)
     res = sum % 11
     if res == 0:
         return '5'
     elif res == 1:
         return '0'
     else:
         return str(11 - res)

def mod10zb(value):
    l = len(value)
    res = 0
    for i in xrange(0, l):
        res += int(value[l - i - 1]) * (i % 2 + 1)
    return str(res % 10)

def mod10(value):
    l = len(value)
    res = 0
    for i in xrange(0, l):
        num = int(value[l - i - 1]) * (((i + 1) % 2) + 1)
        res += (num / 10 + num % 10)
    res = res % 10
    if res == 0:
        return '0'
    else:
        return str(10 - res)

def mod11(value):
    l = len(value)
    res = 0
    for i in xrange(0, l):
        res += int(value[l - i - 1]) * (i % 6 + 2)
    res = res % 11
    if res > 1:
        return str(11 - res)
    else:
        return '0'
"""
# Test
mod11p7('3456789012') # res = '2'
mod10zb('223344556') #res='8'
mod7064('234000') #res='9'
mod11ini('33444555666') #res=9
mod10('54370395') #res=7
mod11('54370395') #res=8
"""

def reference_number_get(model='', P1='', P2='', P3='', P4=''):

    if not model:
        model = ''  # or '99'?
    if model == "01":
        res = '-'.join((P1, P2, P3 + mod11ini(P1 + P2 + P3)))
    elif model == "02":
        res = '-'.join((P1, P2 + mod11ini(P2), P3 + mod11ini(P3)))
    elif model == "03":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + mod11ini(P3)))
    elif model == "04":
        res = '-'.join((P1 + mod11ini(P1), P2, P3 + mod11ini(P3)))
    elif model == "05":
        res = '-'.join((P1 + mod11ini(P1), P2, P3))
    elif model == "06":
        res = '-'.join((P1, P2, P3 + mod11ini(P2 + P3)))
    elif model == "07":
        res = '-'.join((P1, P2 + mod11ini(P2), P3))
    elif model == "08":
        res = '-'.join((P1, P2 + mod11ini(P1 + P2), P3 + mod11ini(P3)))
    elif model == "09":
        res = '-'.join((P1, P2 + mod11ini(P1 + P2), P3))
    elif model == "10":
        res = '-'.join((P1 + mod11ini(P1), P2, P3 + mod11ini(P2 + P3)))
    elif model == "11":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3))
    elif model == "13":
        res = '-'.join((P1 + mod11p7(P1), P2, P3))
    elif model == "14":
        res = '-'.join((P1 + mod10zb(P1), P2, P3))
    elif model == "15":
        res = '-'.join((P1 + mod10(P1), P2 + mod10(P2)))
    elif model == "16":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3))
    elif model == "17":
        res = '-'.join((P1 + iso7064(P1), P2, P3))
    elif model == "18":
        res = '-'.join((P1 + mod11p7(P1), P2, P3))
    elif model == "21":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3))
    elif model == "23":
        res = '-'.join((P1 + mod11ini(P1), P2, P3, P4))
    elif model == "24":
        res = '-'.join((P1 + mod11ini(P1), P2, P3, P4))
    elif model == "26":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + mod11ini(P3), P4))
    elif model == "27":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2)))
    elif model == "28":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + mod11ini(P3), P4))
    elif model == "29":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + mod11ini(P3)))
    elif model == "31":
        res = '-'.join((P1 + iso7064(P1), P2, P3, P4))
    elif model == "33":
        res = '-'.join((P1 + iso7064(P1), P2 + iso7064(P2), P3))
    elif model == "34":
        res = '-'.join((P1 + iso7064(P1), P2 + iso7064(P2), P3 + iso7064(P3)))
    elif model == "40":
        res = '-'.join((P1 + mod10(P1), P2, P3))
    elif model == "43":
        res = '-'.join((P1, P2 + mod11ini(P2), P3, P4))
    elif model == "55":
        res = '-'.join((P1 + mod11ini(P1), P2, P3))
    elif model == "62":
        res = '-'.join((P1 + mod11ini(P1), P2 + iso7064(P2), P3 + mod11ini(P3), P4))
    elif model == "63":
        res = '-'.join((P1 + mod11ini(P1), P2 + iso7064(P2), P3 + mod11ini(P3)))
    elif model == "64":
        res = '-'.join((P1 + mod11ini(P1), P2 + iso7064(P2), P3, P4))
    elif model == "65":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + iso7064(P3), P4))
    elif model == "66":
        res = '-'.join((P1, P2[:7] + mod11ini(P2[:7]) + P2[7:], P3))
    elif model == "83":
        res = '-'.join(((P1 + mod11ini(P1), P2, P3)))
    elif model == "84":
        if len(P2) == 4:
            res = '-'.join((P1 + mod11ini(P1), P2, P3))
        else:
            res = '-'.join(((P1 + mod11ini(P1), P2)))
    else: # model in ('','00',"99")
        res = (P1 + '-' + P2 + '-' + P3 + '-' + P4)

    res.strip('-')
    res = res.strip('-').replace('---', '-').replace('--', '-')
    
    return res


# 1.   = V-variable,mandatory
#      = v-variable,optional
#      = F-fixed lenght,mandatory
#      = f-fixed lenght,optional
# 2-3. =max lenght
# 4.   = K - control num
#      = k - control num if right one does not exists ???
#      = n - NO control num
MODELS_LENGHT = {
          "01":('V12k', 'v12k', 'v12K', 'n00n'),
          "02":('V12n', 'v12K', 'v12K', 'n00n'),
          "03":('V12K', 'v12K', 'v12K', 'n00n'),
          "04":('V12K', 'v12n', 'v12K', 'n00n'),
          "05":('V12K', 'v12n', 'v12n', 'n00n'),
          "06":('V12n', 'v12k', 'v12K', 'n00n'),
          "07":('V12n', 'v12K', 'v12n', 'n00n'),
          "08":('V12k', 'v12K', 'v12K', 'n00n'),
          "09":('V12k', 'v12K', 'v12n', 'n00n'),
          "10":('V12K', 'v12k', 'v12K', 'n00n'),
          "11":('V12K', 'v12K', 'v12n', 'n00n'),
          "12":('F13K', 'v12n', 'v12n', 'n00n'),
          "13":('F10K', 'v12n', 'v12n', 'n00n'),
          "14":('F10K', 'v12n', 'v12n', 'n00n'),
          "15":('F08K', 'F11K', 'n00n', 'n00n'),
          "16":('F05K', 'F04K', 'F08n', 'n00n'),
          "17":('V12K', 'v12K', 'v12n', 'n00n'),
          "18":('V12K', 'v12n', 'v12n', 'n00n'),
          "23":('F04K', 'v12n', 'v12n', 'v12n'),
          "24":('F04K', 'v12n', 'v12n', 'v12n'),
          "25":('F03n', 'F07n', 'n00n', 'n00n'),
          "26":('F04K', 'V11K', 'V11K', 'v12n'),
          "27":('F04K', 'V12K', 'n00n', 'n00n'),
          "28":('F04K', 'F03K', 'F06K', 'v06n'),
          "29":('F04K', 'V12K', 'V12K', 'n00n'),
          "30":('F10n', 'F04n', 'V06n', 'n00n'),
          "31":('V06K', 'v12n', 'v12n', 'v12n'),
          "33":('V06K', 'V07K', 'V07n', 'n00n'),
          "34":('V06K', 'F07K', 'V05K', 'n00n'),
          "40":('F11K', 'v12n', 'v12n', 'n00n'),
          "41":('F13K', 'v12K', 'v12n', 'n00n'),
          "42":('V12k', 'v12k', 'v12K', 'n00n'),
          "43":('F03n', 'F08K', 'F05n', 'F03n'),
          "55":('V12n', 'v12K', 'v12n', 'n00n'),
          "62":('F04K', 'V05K', 'V06K', 'v12n'),
          "63":('F04K', 'V05K', 'V12K', 'n00n'),
          "64":('F04K', 'V05K', 'V12n', 'v09n'),
          "65":('F04K', 'V03K', 'V05n', 'v12n'),
          "67":('F11K', 'v10K', 'v08n', 'n00n'),
          "68":('F04K', 'F11K', 'v05n', 'n00n'),
          "69":('F05K', 'F11K', 'n00n', 'n00n'),
          "83":('F04K', 'V16n', 'f06n', 'n00n'),
          "84":('F04K', 'v08n', 'v10n', 'n00n'),
          }
#"84":('F04K', 'v08n', 'v10n', 'n00n'),  #interno FINA    
#"23":('F04K', 'v12n', 'v12n', 'v12n'),  #Podaci P2, P3 i P4 ukupno mogu imati 15 znamenaka, s tim da svaki pojedina�no mo�e imati najvi�e do 12 znamenaka.


def validate_lenghts(model='', P1='', P2='', P3='', P4=''):
    P1_4=(P1,P2,P3,P4)
    i=0
    res=True
    for P in P1_4:
        check_type=MODELS_LENGHT[model][i][0]
        check_len=int(MODELS_LENGHT[model][i][1:3])
        if check_type == "n":
            if len(P) != 0:
                res = False
        if check_type == "F":
            if len(P) <> check_len:
                res = False
        if check_type == "f":
            if len(P) <> check_len:
                res = False
        if check_type == "V":
            if len(P) == 0 or len(P) > check_len:
                res = False
        if check_type == "v":
            if len(P) > check_len:
                res = False
        i+=1
    return res


def reference_number_valid(model='', P1='', P2='', P3='', P4=''):
    P1_4=(P1,P2,P3,P4)
    pnbr_ulazni = "-".join(P1_4)
    pnbr_ulazni.strip('-')
    pnbr_ulazni = pnbr_ulazni.strip('-').replace('---', '-').replace('--', '-')
    i=0
    bez_K=[]
    for P in P1_4:
        if MODELS_LENGHT[model][i][3] == "K":
            bez_K.append(P[:-1])
        elif MODELS_LENGHT[model][i][3] == "k" and len(P1_4[i+1]) == "":
            bez_K.append(P[:-1])
        else:
            bez_K.append(P)
        i+=1
    pnbr=reference_number_get(model, bez_K[0], bez_K[1], bez_K[2], bez_K[3])
    return pnbr==pnbr_ulazni

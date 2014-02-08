# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#    
#    Copyright (C) 2010-2011 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#
##############################################################################
{
    "name": "Complete pricelist overview",
    "version": "1.0",
    "depends": ["product_pricelist_fixed_price"],
    "author": "Marco Dieckhoff, BREMSKERL",
    "category": "Generic Modules/Inventory Control",
    "description": """Complete pricelist overview
    """,
    "init_xml": [],
    'update_xml': ["view/pricelist_view.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': '${certificate}',
}
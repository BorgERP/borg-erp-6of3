# -*- encoding: utf-8 -*-

from osv import fields,osv

class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"

    _columns = {
        "price_version_name": fields.related("price_version_id", "name", readonly=True, type="char", string="Version Name"),
        "price_version_date_start": fields.related("price_version_id", "date_start", readonly=True, type="date", string="Version Start"),
        "price_version_date_end": fields.related("price_version_id", "date_end", readonly=True, type="date", string="Version End"),
        "price_version_active": fields.related("price_version_id", "active", readonly=True, type="boolean", string="Version Active"),
        
        "pricelist_idid": fields.related("price_version_id", "pricelist_id", "name", readonly=True, type="integer", string="List ID"),
        "pricelist_name": fields.related("price_version_id", "pricelist_id", "name", readonly=True, type="char", string="List Name"),
        "pricelist_type": fields.related("price_version_id", "pricelist_id", "type", readonly=True, type="char", string="List Type"),
        "pricelist_cur": fields.related("price_version_id", "pricelist_id", "currency_id", readonly=True, type="many2one", relation="res.currency", string="List Currency"),

        }

product_pricelist_item()

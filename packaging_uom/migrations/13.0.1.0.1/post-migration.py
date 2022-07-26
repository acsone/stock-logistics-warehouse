# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    Migration script used to init uom_categ_domain_id on existing records
    :param cr: database cursor
    :param version: str
    :return:
    """
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        ProductPackaging = env["product.packaging"]
        domain = [("uom_categ_domain_id", "=", False)]
        packings = ProductPackaging.with_context(active_test=False).search(domain)
        for packing in packings:
            uom_categ_id = ProductPackaging.with_context(
                default_product_id=packing.product_id.id
            )._default_uom_categ_domain_id()
            if uom_categ_id:
                packing.write({"uom_categ_domain_id": uom_categ_id})

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID
from odoo.api import Environment


def pre_init_hook(cr):

    if not openupgrade.column_exists(cr, "stock_location", "occupancy"):
        env = Environment(cr, SUPERUSER_ID, {})
        field_spec = [
            (
                "occupied",
                "stock.location",
                False,
                "boolean",
                "boolean",
                "stock_location_occupancy",
                False,
            )
        ]
        openupgrade.add_fields(env, field_spec)
        # Compute the True values
        query = """
            UPDATE stock_location SET occupied = True
                WHERE EXISTS (SELECT 1 FROM stock_quant WHERE location_id = stock_location.id)
        """
        openupgrade.logged_query(env.cr, query)

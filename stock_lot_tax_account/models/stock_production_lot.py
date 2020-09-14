# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        relation="stock_production_lot_account_tax_rel",
        column1="lot_id",
        column2="tax_id",
    )

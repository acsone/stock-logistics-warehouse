# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    occupied = fields.Boolean(
        compute="_compute_occupied",
        store=True,
        index=True,
        help="This will reflect if the stock location is void or not (no product quantities).",
    )
    # This field is used to display the state of the location using
    # the 'state_selection' widget.
    occupied_state = fields.Selection(
        [("done", "Void"), ("blocked", "Occupied")],
        string="Occupancy",
        compute="_compute_occupied_state",
    )

    @api.depends("occupied")
    def _compute_occupied_state(self):
        for occupied, locations in self.partition("occupied").items():
            locations.occupied_state = "blocked" if occupied else "done"

    @api.depends("quant_ids.location_id")
    def _compute_occupied(self):
        """
        Compute the 'occupied' field.
        It is True when location does not contain any quant.
        """
        quants_result = self.env["stock.quant"].read_group(
            [("location_id", "in", self.ids)], ["location_id"], ["location_id"]
        )
        counts = [r["location_id"][0] for r in quants_result]
        location_with_quants = self.filtered(lambda location: location.id in counts)
        location_with_quants.occupied = True
        (self - location_with_quants).occupied = False

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import groupby


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_current_move_lines(self):
        """Return a dictionary of move lines that are currently in progress
        by quant.

        This method returns a dictionary with the key being the quant id and
        the value being a list of move lines that are currently in progress
        for that quant.

        A move line is considered to be in progress if it is not done and
        its quantity done is positive for the same product, location, lot
        and package as the quant.
        """
        quants = self.filtered("reserved_quantity")
        move_lines = self.env["stock.move.line"].search(
            [
                ("state", "not in", ("done", "cancel")),
                ("location_id", "in", quants.mapped("location_id").ids),
                ("qty_done", ">", 0.0),
            ]
        )
        move_lines_by_location_by_product = dict(
            groupby(
                move_lines,
                lambda ml: (ml.location_id, ml.product_id, ml.lot_id, ml.package_id),
            )
        )
        ret = {}
        for quant in quants:
            key = (quant.location_id, quant.product_id, quant.lot_id, quant.package_id)
            move_lines = move_lines_by_location_by_product.get(key, [])
            if move_lines:
                ret[quant.id] = move_lines
        return ret

    def _check_update_quantity_allowed(self, raise_exception=True):
        if not self.env.company.stock_quant_no_inventory_if_being_picked:
            return
        current_move_lines = self._get_current_move_lines()
        if current_move_lines:
            if raise_exception:
                details = []
                for quant in self:
                    move_lines = current_move_lines.get(quant.id, [])
                    if move_lines:
                        details.extend(
                            f"{move_line.qty_done} {move_line.product_id.name} "
                            f"-> {move_line.location_id.name}"
                            for move_line in move_lines
                        )
                raise UserError(
                    _(
                        "You cannot update the quantity of a quant that is "
                        "currently being picked.\n %(details)s",
                        details="\n".join(details),
                    )
                )

    def write(self, vals):
        if "inventory_quantity" in vals:
            self._check_update_quantity_allowed()
        return super().write(vals)

    def _apply_inventory(self):
        self.filtered("inventory_diff_quantity")._check_update_quantity_allowed()
        return super()._apply_inventory()

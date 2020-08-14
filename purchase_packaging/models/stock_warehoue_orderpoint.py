# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        # In this method we need to access the purchase order line quantity
        # to correctly evaluate the forecast.
        # Imagine a product with a minimum rule of 4 units and a purchase
        # multiple of 12. The first run will generate a procurement for 4 Pc
        # but a purchase for 12 units.
        # Let's change the minimum rule to 5 units.
        # The standard subtract_procurements_from_orderpoints will return 4
        # and Odoo will create a procurement for 1 unit which will trigger a
        # purchase of 12 due to the multiple. So the original purchase will
        # be increased to 24 units which is wrong.
        # This override will return 12 and no additionnal procurement will be
        # created
        res = super()._quantity_in_progress()
        purchase_requisition_model = self.env["purchase.requisition"]
        purchase_requisitions = purchase_requisition_model.browse()
        for orderpoint in self:
            purchase_requisitions |= purchase_requisition_model.search(
                [
                    ("origin", "=", orderpoint.name),
                    ("state", "not in", ["cancel", "done"]),
                ]
            )
        req_by_orderpoint = {}
        for req in purchase_requisitions:
            req_by_orderpoint.setdefault(
                req.origin, purchase_requisition_model.browse()
            )
            req_by_orderpoint[req.origin] |= req
        for orderpoint in self:
            reqs = req_by_orderpoint.get(orderpoint.name)
            if reqs:
                purchase_orders = reqs.mapped("purchase_ids").filtered(
                    lambda p: p.state in ["draft", "sent", "to approve"]
                )
                po_lines = purchase_orders.mapped("order_line")
                if po_lines:
                    qty = sum([line.product_qty for line in po_lines])
                    precision = orderpoint.product_uom.rounding
                    if (
                        float_compare(
                            qty, res[orderpoint.id], precision_rounding=precision,
                        )
                        >= 0
                    ):
                        res[orderpoint.id] = qty
        return res
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestLocationIsVoid(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.stock_1 = cls.env["stock.location"].create(
            {
                "name": "Stock 1",
                "location_id": cls.stock.id,
            }
        )

    def test_location_is_void(self):
        # Check the multi call
        (self.stock_1 | self.stock).mapped("occupied")
        self.assertTrue(self.stock.occupied)
        self.assertEqual("blocked", self.stock.occupied_state)
        self.assertFalse(self.stock_1.occupied)
        self.assertEqual("done", self.stock_1.occupied_state)
        # Search with the is_void == True domain
        stock = self.stock.search([("occupied", "=", False)])
        self.assertIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertNotIn(
            self.stock.id,
            stock.ids,
        )
        # Search with the is_void == True domain
        stock = self.stock.search([("occupied", "=", True)])
        self.assertNotIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertIn(
            self.stock.id,
            stock.ids,
        )

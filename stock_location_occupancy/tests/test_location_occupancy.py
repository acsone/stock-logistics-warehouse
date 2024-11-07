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
        (self.stock_1 | self.stock).mapped("is_void")
        self.assertFalse(self.stock.is_void)
        self.assertEqual("red", self.stock.is_void_state)
        self.assertTrue(self.stock_1.is_void)
        self.assertEqual("green", self.stock.is_void_state)
        # Search with the is_void == True domain
        stock = self.stock.search([("is_void", "=", True)])
        self.assertIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertNotIn(
            self.stock.id,
            stock.ids,
        )
        # Search with the is_void == True domain
        stock = self.stock.search([("is_void", "=", False)])
        self.assertNotIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertIn(
            self.stock.id,
            stock.ids,
        )

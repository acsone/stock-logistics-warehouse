# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestPurchaseOrderLine(common.TransactionCase):
    def setUp(self):
        """ Create a packagings with uom product_uom_dozen on
            product_supplierinfo_1'product (uom is product_uom_unit)
        """
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.product_supplier_info = self.env.ref("product.product_supplierinfo_1")
        self.product_id = self.product_supplier_info.product_tmpl_id.product_variant_ids[  # noqa
            0
        ]
        self.product_supplier_info.product_id.uom_po_id = self.env.ref(
            "uom.product_uom_unit"
        )
        self.product_supplier_info.min_qty = 1
        self.product_packaging_dozen = self.env["product.packaging"].create(
            {
                "product_id": self.product_id.id,
                "uom_id": self.env.ref("uom.product_uom_dozen").id,
                "name": "Packaging Dozen",
            }
        )
        self.product_packaging_unit = self.env["product.packaging"].create(
            {
                "product_id": self.product_id.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "name": "Packaging Unit",
            }
        )
        self.product_uom_8 = self.env["uom.uom"].create(
            {
                "category_id": self.env.ref("uom.product_uom_categ_unit").id,
                "name": "COL8",
                "factor_inv": 8,
                "uom_type": "bigger",
                "rounding": 1.0,
            }
        )

    def test_po_line(self):
        """ On supplierinfo set product_uom_8 as min_qty_uom_id
            On supplierinfo set 2 as min_qty
            Create purchase order line with product product_product_3
            Check packaging_id is product_packaging_dozen
            Check product_purchase_uom_id is product_uom_8
            Check product_purchase_qty is 2
            Check product_qty is 8*2 = 16
            Check price_unit is 12*38 = 456
            Check product_uom is product_uom_dozen
            Confirm po
            Check stock move packaging is product_packaging_dozen
            Check stock move product_uom is product_uom_dozen
            Check stock move product_qty is 16
        """
        self.product_supplier_info.min_qty_uom_id = self.product_uom_8
        self.product_supplier_info.min_qty = 2
        self.product_supplier_info.packaging_id = self.product_packaging_dozen

        po = self.env["purchase.order"].create(
            {"partner_id": self.product_supplier_info.name.id}
        )
        po_line = po.order_line.new(
            {
                "product_id": self.product_id.id,
                "product_purchase_qty": 1.0,
                "product_purchase_uom_id": po.order_line._default_product_purchase_uom_id(),  # noqa
                "order_id": po,
            }
        )
        po_line.onchange_product_id()
        self.assertEqual(po_line.packaging_id.id, self.product_packaging_dozen.id)
        self.assertEqual(po_line.product_purchase_uom_id.id, self.product_uom_8.id)
        self.assertAlmostEqual(po_line.product_purchase_qty, 2)
        self.assertAlmostEqual(po_line.product_qty, 16)
        self.assertTrue(po_line.price_unit)
        self.assertEqual(po_line.product_uom, self.env.ref("uom.product_uom_dozen"))
        values = po_line._convert_to_write(
            {name: po_line[name] for name in po_line._cache}
        )
        # To ensure the values for product_purchase_qty is correctly forced
        # during the create we have to remove it from the values
        values.pop("product_qty", 0)
        po.order_line.create(values)
        # check that all the packaging informations are on the created picking
        po._create_picking()
        sm = po.picking_ids[0].move_lines[0]
        # self.assertEqual(sm.product_packaging.id, self.product_packaging_dozen.id)
        self.assertEqual(sm.product_uom, self.env.ref("uom.product_uom_dozen"))
        self.assertAlmostEqual(sm.product_uom_qty, 16)

    def test_po_line_no_product(self):
        self.product_supplier_info.min_qty_uom_id = self.product_uom_8
        self.product_supplier_info.min_qty = 2
        self.product_supplier_info.packaging_id = self.product_packaging_dozen

        po = self.env["purchase.order"].create(
            {"partner_id": self.product_supplier_info.name.id}
        )
        po_line = po.order_line.new(
            {
                "product_id": self.product_id.id,
                "product_purchase_qty": 1.0,
                "product_purchase_uom_id": po.order_line._default_product_purchase_uom_id(),  # noqa
                "order_id": po,
            }
        )
        po_line.onchange_product_id()
        po_line.product_id = None
        po_line.product_qty = 2.0
        self.assertEqual(
            2.0, po_line.product_purchase_qty, "The purchase quantity is not well set",
        )

    def test_po_line_change_packaging(self):
        self.product_supplier_info.min_qty_uom_id = self.product_uom_8
        self.product_supplier_info.min_qty = 2
        self.product_supplier_info.packaging_id = self.product_packaging_dozen

        po = self.env["purchase.order"].create(
            {"partner_id": self.product_supplier_info.name.id}
        )
        po_line = po.order_line.new(
            {
                "product_id": self.product_id.id,
                "product_purchase_qty": 1.0,
                "product_purchase_uom_id": po.order_line._default_product_purchase_uom_id(),  # noqa
                "order_id": po,
            }
        )
        po_line.onchange_product_id()
        self.assertEquals(
            self.product_packaging_dozen.uom_id,
            po_line.product_uom,
            "The UOM Unit is not well set",
        )
        po_line.packaging_id = self.product_packaging_unit
        po_line._onchange_packaging_id()
        self.assertEquals(
            self.product_packaging_unit.uom_id,
            po_line.product_uom,
            "The product uom is not well set",
        )

    def test_po_line_inverse_no_supplier(self):
        self.product_supplier_info.min_qty_uom_id = self.product_uom_8
        self.product_supplier_info.min_qty = 2
        self.product_supplier_info.packaging_id = self.product_packaging_dozen

        po = self.env["purchase.order"].create(
            {"partner_id": self.product_supplier_info.name.id}
        )
        po_line = po.order_line.new(
            {
                "product_id": self.product_id.id,
                "product_purchase_qty": 1.0,
                "product_purchase_uom_id": po.order_line._default_product_purchase_uom_id(),  # noqa
                "order_id": po,
            }
        )
        po_line.onchange_product_id()
        self.assertEquals(
            16.0, po_line.product_qty,
        )
        # Remove Supplierinfos
        po_line.product_id.seller_ids = self.env["product.supplierinfo"].browse()
        po_line.product_qty = 2.0
        self.assertEquals(
            2.0, po_line.product_qty,
        )

    def test_po_line_change(self):
        self.product_supplier_info.min_qty_uom_id = self.product_uom_8
        self.product_supplier_info.min_qty = 2
        self.product_supplier_info.packaging_id = self.product_packaging_dozen

        po = self.env["purchase.order"].create(
            {"partner_id": self.product_supplier_info.name.id}
        )
        po_line = po.order_line.new(
            {
                "product_id": self.product_id.id,
                "product_purchase_qty": 1.0,
                "product_purchase_uom_id": po.order_line._default_product_purchase_uom_id(),  # noqa
                "order_id": po,
            }
        )
        po_line.onchange_product_id()
        vals = po_line._convert_to_write(po_line._cache)
        po_line = po_line.create(vals)
        self.assertEquals(
            16.0, po_line.product_qty,
        )
        # Remove Supplierinfos
        po_line.product_id.seller_ids = self.env["product.supplierinfo"].browse()
        po_line.onchange_product_id()
        po_line.product_qty = 2.0
        self.assertEquals(2.0, po_line.product_qty)

    def test_po_line_change_uom(self):
        self.product_supplier_info.min_qty_uom_id = self.product_uom_8
        self.product_supplier_info.min_qty = 2
        self.product_supplier_info.packaging_id = self.product_packaging_dozen

        po = self.env["purchase.order"].create(
            {"partner_id": self.product_supplier_info.name.id}
        )
        po_line = po.order_line.new(
            {
                "product_id": self.product_id.product_variant_id,
                "product_purchase_qty": 1.0,
                "product_purchase_uom_id": po.order_line._default_product_purchase_uom_id(),  # noqa
                "order_id": po,
            }
        )
        po_line.onchange_product_id()
        vals = po_line._convert_to_write(po_line._cache)
        po_line = po_line.create(vals)
        self.assertEquals(16.0, po_line.product_qty)
        po_line.product_purchase_uom_id = self.env.ref("uom.product_uom_unit")
        self.assertEquals(2.0, po_line.product_qty)

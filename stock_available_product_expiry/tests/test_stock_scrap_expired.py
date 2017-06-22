# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo .exceptions import UserError
from odoo.tests import common
from datetime import timedelta


class TestProductProduct(common.TransactionCase):

    def setUp(self):
        super(TestProductProduct, self).setUp()
        param_obj = self.env['ir.config_parameter']
        param_obj.set_param('stock_qty_available_lot_expired', True)
        lot_obj = self.env['stock.production.lot']
        # ensure that all lots are without removal date
        lot_obj.search([]).write({'removal_date': False})

        vals = {'name': 'Product with lot',
                'type': 'product'
                }
        self.product_1 = self.env['product.product'].create(vals)
        self.product_1.tracking = 'lot'
        self.product_template = self.product_1.product_tmpl_id
        vals = {'name': 'Product variant with lot',
                'type': 'product',
                'product_tmpl_id': self.product_template.id,
                }
        self.product_2 = self.env['product.product'].create(vals)
        self.product_2.tracking = 'lot'
        self.warehouse_1 = self.env.ref('stock.warehouse0')

        # on product 1 add a quantity of 10 with a removal time set to now +
        #  5 days
        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + timedelta(days=5)
        # First create lot
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }

        self.lot_1 = lot_obj.create(vals)
        inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.product_1.id,
                'prod_lot_id': self.lot_1.id,
                'product_uom_id': self.product_1.uom_id.id,
                'product_qty': 10,
                'location_id': self.warehouse_1.lot_stock_id.id
            })]
        })
        inventory.action_done()
        # on product 2 add a quantity of 20 with a removal time set to 5
        # days ago
        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + timedelta(days=-5)
        self.expired_removal_date = removal_date
        vals = {'removal_date': removal_date,
                'product_id': self.product_2.id
                }
        self.lot_2 = lot_obj.create(vals)
        inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.product_2.id,
                'prod_lot_id': self.lot_2.id,
                'product_uom_id': self.product_2.uom_id.id,
                'product_qty': 20,
                'location_id': self.warehouse_1.lot_stock_id.id
            })]
        })
        inventory.action_done()

    def test_stock_scrap_expired(self):
        stock_scrap_expired_obj = self.env['stock.scrap.expired']
        # create a scrap for today and all the default values
        stock_scrap_expired = stock_scrap_expired_obj.create({})
        self.assertFalse(stock_scrap_expired.stock_scrap_expired_line_ids)
        # The list of product to scrap is computed by the onchange
        stock_scrap_expired._onchange_removal_date_location_id()
        line = stock_scrap_expired.stock_scrap_expired_line_ids
        self.assertEqual(1, len(line))
        # The generated line must only reference product_2 since it's the only
        # one expired
        self.assertEqual(line.product_id, self.product_2)
        self.assertEqual(line.lot_id, self.lot_2)
        self.assertEqual(line.expected_scrap_qty, 20)
        self.assertFalse(stock_scrap_expired.move_ids)
        # specify a quantity to scrap
        line.scrap_qty = 5
        # before the confirmation no move exists
        move = stock_scrap_expired.move_ids
        self.assertEqual(0, len(move))
        # launch the scrap
        stock_scrap_expired.action_confirm()
        self.assertEqual(stock_scrap_expired.state, 'done')
        self.assertEqual(line.state, 'done')
        # a stock move is created
        move = stock_scrap_expired.move_ids
        self.assertEqual(1, len(move))
        self.assertTrue(move.location_dest_id.scrap_location)
        self.assertEqual(
            move.location_dest_id, stock_scrap_expired.scrap_location_id)
        self.assertEqual(move.product_id, self.product_2)
        self.assertEqual(move.quant_ids.lot_id, self.lot_2)
        self.assertEqual(move.product_uom_qty, 5)

        # an action allows you to display the moves generated by the scrap
        res = stock_scrap_expired.action_get_stock_moves()
        domain = res['domain']
        self.assertEqual(domain, [('id', 'in', [move.id])])

        # after the scrap 15 products remains as expired
        self.assertEqual(self.product_2.qty_expired, 15)

    def test_stock_scrap_expired_no_scrap(self):
        stock_scrap_expired_obj = self.env['stock.scrap.expired']
        # create a scrap for today and all the default values
        stock_scrap_expired = stock_scrap_expired_obj.create({})
        self.assertFalse(stock_scrap_expired.stock_scrap_expired_line_ids)
        # The list of product to scrap is computed by the onchange
        stock_scrap_expired._onchange_removal_date_location_id()
        line = stock_scrap_expired.stock_scrap_expired_line_ids
        self.assertEqual(1, len(line))
        # before the confirmation no move exists
        move = stock_scrap_expired.move_ids
        self.assertEqual(0, len(move))
        # launch the scrap
        stock_scrap_expired.action_confirm()
        # after the confirmation no move exists since we don't have
        # specified a scrap_qty
        move = stock_scrap_expired.move_ids
        self.assertEqual(0, len(move))

    def test_unlink(self):
        stock_scrap_expired_obj = self.env['stock.scrap.expired']
        # create a scrap for today and all the default values
        stock_scrap_expired = stock_scrap_expired_obj.create({})
        self.assertFalse(stock_scrap_expired.stock_scrap_expired_line_ids)
        # The list of product to scrap is computed by the onchange
        stock_scrap_expired._onchange_removal_date_location_id()
        line = stock_scrap_expired.stock_scrap_expired_line_ids
        self.assertEqual(1, len(line))
        line.scrap_qty = line.expected_scrap_qty
        stock_scrap_expired.action_confirm()
        # once the scrap is done is no more possible to remove the line nor
        # the stock.scrap.expired
        with self.assertRaises(UserError):
            stock_scrap_expired.unlink()
        with self.assertRaises(UserError):
            line.unlink()

    def test_unlink_draft(self):
        stock_scrap_expired_obj = self.env['stock.scrap.expired']
        # create a scrap for today and all the default values
        stock_scrap_expired = stock_scrap_expired_obj.create({})
        self.assertFalse(stock_scrap_expired.stock_scrap_expired_line_ids)
        # The list of product to scrap is computed by the onchange
        stock_scrap_expired._onchange_removal_date_location_id()
        line = stock_scrap_expired.stock_scrap_expired_line_ids
        self.assertEqual(1, len(line))
        stock_scrap_expired.unlink()
        self.assertFalse(stock_scrap_expired.exists())

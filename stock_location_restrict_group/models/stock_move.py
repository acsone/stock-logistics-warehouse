# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = 'stock.move'

    restricted = fields.Boolean(
        string='Restricted',
        compute='_compute_restricted')

    @api.multi
    def _compute_restricted(self):
        for move in self:
            if move.location_dest_id and\
                    move.location_dest_id.usage == 'group' and\
                    move.location_dest_id.restricted_group:
                move.restricted = True
            else:
                move.restricted = False

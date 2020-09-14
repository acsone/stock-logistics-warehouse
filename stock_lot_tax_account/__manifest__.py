# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Lot Tax Account',
    'summary': """
        This module allows to define a tax account linked to a lot""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'depends': [
        'account',
        'stock',
    ],
    'data': [
        'views/stock_production_lot.xml',
    ],
}

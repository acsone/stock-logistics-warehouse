# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Is Void",
    "summary": """This module allows to identify void stock locations""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["base_partition", "stock"],
    "maintainers": ["rousseldenis"],
    "data": [
        "views/stock_location.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}

# Copyright 2026 KOBROS-TECH LTD (https://www.kobros-tech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Picking Prevent Consolidation",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "license": "AGPL-3",
    "author": "KOBROS-TECH LTD",
    "maintainer": "kobros-tech",
    "summary": "Prevent stock move consolidation per operation type",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
    "installable": True,
    "application": False,
}

# Copyright 2026 KOBROS-TECH LTD (https://www.kobros-tech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    prevent_consolidation = fields.Boolean(
        string="Prevent Move Consolidation",
        default=False,
        help=(
            "When enabled, stock moves in pickings of this type will not "
            "be consolidated with other moves. Each move will remain separate."
        ),
    )

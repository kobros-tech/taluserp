# Copyright 2026 KOBROS-TECH LTD (https://www.kobros-tech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _search_picking_for_assignation_domain(self):
        """Override to prevent picking consolidation based on picking type setting.

        When prevent_consolidation is enabled on stock.picking.type, all pickings
        of that type won't consolidate. This method returns an impossible domain
        [('id', '=', False)] to prevent finding existing pickings, forcing creation
        of NEW pickings instead.

        This operates at the PICKING-LEVEL (prevents moves from being added to
        existing pickings).
        """
        domain = super()._search_picking_for_assignation_domain()
        # Check if consolidation should be prevented at picking type level
        if self.picking_type_id.prevent_consolidation:
            # Return an impossible domain so no picking is found
            # This forces a new picking to be created instead of consolidating moves
            domain = [("id", "=", False)]
        return domain

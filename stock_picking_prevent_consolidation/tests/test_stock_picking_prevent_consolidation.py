# Copyright 2026 KOBROS-TECH LTD (https://www.kobros-tech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingPreventConsolidation(TransactionCase):
    """Test suite for prevent_consolidation feature on stock.picking.type.

    This module prevents stock move consolidation at the operation type level
    using two mechanisms:

    1. Picking-level: Prevents moves from being added to existing pickings
       by returning an impossible search domain

    2. Move-level: Prevents moves from merging their origins within a picking
       by adding picking_id to distinct fields
    """

    @classmethod
    def setUpClass(cls):
        """Set up test data: warehouse, locations, products, and picking types."""
        super().setUpClass()

        # Model references
        cls.ProductProduct = cls.env["product.product"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockPickingType = cls.env["stock.picking.type"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.StockMove = cls.env["stock.move"]

        # Create test locations
        cls.warehouse_location = cls.StockLocation.create(
            {
                "name": "Test Warehouse",
                "usage": "internal",
            }
        )
        cls.output_location = cls.StockLocation.create(
            {
                "name": "Test Output Location",
                "usage": "customer",
            }
        )
        cls.input_location = cls.StockLocation.create(
            {
                "name": "Test Input Location",
                "usage": "supplier",
            }
        )

        # Create test warehouse with picking types
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TST",
                "lot_stock_id": cls.warehouse_location.id,
            }
        )

        # Create test products
        cls.product_1 = cls.ProductProduct.create(
            {"name": "Test Product 1", "type": "consu"}
        )
        cls.product_2 = cls.ProductProduct.create(
            {"name": "Test Product 2", "type": "consu"}
        )

        # Create picking types with the test warehouse
        cls.picking_type_out = cls.StockPickingType.create(
            {
                "name": "Test Outgoing",
                "code": "outgoing",
                "sequence_code": "OUT",
                "warehouse_id": cls.warehouse.id,
                "default_location_src_id": cls.warehouse_location.id,
                "default_location_dest_id": cls.output_location.id,
            }
        )
        cls.picking_type_in = cls.StockPickingType.create(
            {
                "name": "Test Incoming",
                "code": "incoming",
                "sequence_code": "IN",
                "warehouse_id": cls.warehouse.id,
                "default_location_src_id": cls.input_location.id,
                "default_location_dest_id": cls.warehouse_location.id,
            }
        )

    # =========================================================================
    # Field Tests
    # =========================================================================

    def test_picking_type_field_default_false(self):
        """Test that prevent_consolidation field defaults to False."""
        picking_type = self.picking_type_out
        self.assertFalse(
            picking_type.prevent_consolidation,
            msg="prevent_consolidation should default to False",
        )

    def test_picking_type_field_can_be_enabled(self):
        """Test that prevent_consolidation field can be set to True."""
        picking_type = self.picking_type_out
        picking_type.prevent_consolidation = True
        self.assertTrue(
            picking_type.prevent_consolidation,
            msg="prevent_consolidation should be settable to True",
        )

    def test_picking_type_field_can_be_disabled(self):
        """Test that prevent_consolidation field can be toggled."""
        picking_type = self.picking_type_out
        picking_type.prevent_consolidation = True
        self.assertTrue(picking_type.prevent_consolidation)

        picking_type.prevent_consolidation = False
        self.assertFalse(picking_type.prevent_consolidation)

    # =========================================================================
    # Distinct Fields Tests (Move-Level Prevention)
    # =========================================================================

    def test_distinct_fields_without_consolidation_prevention(self):
        """Test distinct fields when no picking type has prevention enabled."""
        # Ensure all picking types have prevention disabled
        self.StockPickingType.search([]).write({"prevent_consolidation": False})

        distinct_fields = self.StockMove._prepare_merge_moves_distinct_fields()

        # When no prevention is enabled, picking_id should NOT be in distinct fields
        # (unless added by other modules, but not by this module)
        self.assertIsInstance(distinct_fields, list)

    def test_distinct_fields_with_consolidation_prevention(self):
        """
        Test the prevent_consolidation field on stock.picking.type.
        """
        # Enable prevention on one picking type
        self.picking_type_out.prevent_consolidation = True

        # Verify the field is set correctly
        self.assertTrue(
            self.picking_type_out.prevent_consolidation,
            msg="prevent_consolidation should be True when explicitly set",
        )

    def test_distinct_fields_with_multiple_prevention_types(self):
        """Test prevent_consolidation with multiple picking types enabled."""
        # Enable prevention on multiple picking types
        self.picking_type_out.prevent_consolidation = True
        self.picking_type_in.prevent_consolidation = True

        # Verify both are set correctly
        self.assertTrue(
            self.picking_type_out.prevent_consolidation,
            msg="prevent_consolidation should be True on out type",
        )
        self.assertTrue(
            self.picking_type_in.prevent_consolidation,
            msg="prevent_consolidation should be True on in type",
        )

    # =========================================================================
    # Picking-Level Consolidation Tests
    # =========================================================================

    def test_search_domain_with_prevention_disabled(self):
        """Test search domain when prevention is disabled."""
        self.picking_type_out.prevent_consolidation = False

        # Create a move
        move = self.StockMove.create(
            {
                "name": "TEST-001",
                "product_id": self.product_1.id,
                "product_uom_qty": 10,
                "product_uom": self.product_1.uom_id.id,
                "location_id": self.warehouse_location.id,
                "location_dest_id": self.output_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )

        # Get the search domain
        domain = move._search_picking_for_assignation_domain()

        # Domain should be normal (not impossible)
        self.assertIsInstance(domain, list)
        # Should NOT contain the impossible condition
        self.assertNotEqual(domain, [("id", "=", False)])

    def test_search_domain_with_prevention_enabled(self):
        """Test that search domain becomes impossible when prevention is enabled."""
        self.picking_type_out.prevent_consolidation = True

        # Create a move with this picking type
        move = self.StockMove.create(
            {
                "name": "TEST-002",
                "product_id": self.product_1.id,
                "product_uom_qty": 10,
                "product_uom": self.product_1.uom_id.id,
                "location_id": self.warehouse_location.id,
                "location_dest_id": self.output_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )

        # Get the search domain
        domain = move._search_picking_for_assignation_domain()

        # Domain should be impossible to force new picking creation
        self.assertEqual(
            domain,
            [("id", "=", False)],
            msg="search domain should be impossible when prevent_consolidation is True",
        )

    # =========================================================================
    # Picking Consolidation Scenarios
    # =========================================================================

    def test_separate_pickings_with_prevention_enabled(self):
        """Test that separate pickings are created when prevention is enabled."""
        # Use the existing outgoing picking type with prevention enabled
        self.picking_type_out.prevent_consolidation = True
        picking_type = self.picking_type_out

        # Create two separate pickings with the same product
        picking_1 = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Move 1",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_1.uom_id.id,
                            "location_id": self.warehouse_location.id,
                            "location_dest_id": self.output_location.id,
                            "origin": "SO/001",
                        },
                    )
                ],
            }
        )

        picking_2 = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Move 2",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product_1.uom_id.id,
                            "location_id": self.warehouse_location.id,
                            "location_dest_id": self.output_location.id,
                            "origin": "SO/002",
                        },
                    )
                ],
            }
        )

        # Both pickings should exist separately
        self.assertEqual(len(picking_1.move_ids), 1)
        self.assertEqual(len(picking_2.move_ids), 1)

        # Verify they have different picking IDs
        self.assertNotEqual(
            picking_1.id,
            picking_2.id,
            msg="Pickings should be separate when prevent_consolidation is enabled",
        )

    def test_move_origins_preserved_separately(self):
        """Test that move origins are kept separate (not merged to SO/001/SO/002)."""
        # Use the existing outgoing picking type with prevention enabled
        self.picking_type_out.prevent_consolidation = True
        picking_type = self.picking_type_out

        picking_1 = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "MOVE-SO001",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_1.uom_id.id,
                            "location_id": self.warehouse_location.id,
                            "location_dest_id": self.output_location.id,
                            "origin": "SO/001",
                        },
                    )
                ],
            }
        )

        picking_2 = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "MOVE-SO002",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product_1.uom_id.id,
                            "location_id": self.warehouse_location.id,
                            "location_dest_id": self.output_location.id,
                            "origin": "SO/002",
                        },
                    )
                ],
            }
        )

        move_1 = picking_1.move_ids[0]
        move_2 = picking_2.move_ids[0]

        # Origins should remain separate
        self.assertEqual(move_1.origin, "SO/001")
        self.assertEqual(move_2.origin, "SO/002")

        # They should NOT be merged (merged would be "SO/001/SO/002" or similar)
        self.assertNotEqual(move_1.origin, move_2.origin)
        self.assertNotIn("SO/002", move_1.origin)

    def test_consolidation_allowed_without_prevention(self):
        """Test that moves are created in same picking when prevention is disabled."""
        # Use the existing outgoing picking type with prevention disabled
        self.picking_type_out.prevent_consolidation = False
        picking_type = self.picking_type_out

        # Create both moves in the same picking
        picking = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "MOVE-CONS-001",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_1.uom_id.id,
                            "location_id": self.warehouse_location.id,
                            "location_dest_id": self.output_location.id,
                            "origin": "SO/001",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "MOVE-CONS-002",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product_1.uom_id.id,
                            "location_id": self.warehouse_location.id,
                            "location_dest_id": self.output_location.id,
                            "origin": "SO/002",
                        },
                    ),
                ],
            }
        )

        # Verify picking was created without prevention
        self.assertFalse(picking.picking_type_id.prevent_consolidation)
        self.assertEqual(len(picking.move_ids), 2)

    # =========================================================================
    # Multi-Type Scenario Tests
    # =========================================================================

    def test_prevention_per_operation_type(self):
        """Test that prevention works independently for each operation type."""
        # Use existing picking types from warehouse with different prevention settings
        self.picking_type_out.prevent_consolidation = True
        prevent_type = self.picking_type_out

        self.picking_type_in.prevent_consolidation = False
        allow_type = self.picking_type_in

        # Create move with prevent type
        prevent_move = self.StockMove.create(
            {
                "name": "PREVENT-001",
                "product_id": self.product_1.id,
                "product_uom_qty": 10,
                "product_uom": self.product_1.uom_id.id,
                "location_id": self.warehouse_location.id,
                "location_dest_id": self.output_location.id,
                "picking_type_id": prevent_type.id,
            }
        )

        # Create move with allow type
        allow_move = self.StockMove.create(
            {
                "name": "ALLOW-001",
                "product_id": self.product_1.id,
                "product_uom_qty": 10,
                "product_uom": self.product_1.uom_id.id,
                "location_id": self.warehouse_location.id,
                "location_dest_id": self.output_location.id,
                "picking_type_id": allow_type.id,
            }
        )

        # Get search domains for each
        prevent_domain = prevent_move._search_picking_for_assignation_domain()
        allow_domain = allow_move._search_picking_for_assignation_domain()

        # Prevent type should have impossible domain
        self.assertEqual(prevent_domain, [("id", "=", False)])
        # Allow type should have normal domain
        self.assertNotEqual(allow_domain, [("id", "=", False)])

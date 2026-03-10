## Enable Prevention on Operation Type

To prevent consolidation for a specific operation type:

1. Go to **Inventory > Configuration > Operation Types**
2. Select the operation type you want to configure (e.g., "Incoming Products", "Delivery Orders", "Internal Transfers")
3. In the **"Move Consolidation"** section, check **"Prevent Move Consolidation"**
4. Save the changes

## Effect

All pickings and moves created with this operation type will:

- Create **separate pickings** for each move group (instead of consolidating into one)
- Keep **move origins separate** (no "SO/001/SO/002" consolidation)  
- Maintain **complete traceability** of each source document

## Use Cases

- **Separate Returns Processing**: Prevent consolidation for return pickings to maintain source traceability
- **Quality Control**: Keep moves separate for different quality batches
- **Multiple Suppliers**: In warehouse receiving, keep supplier shipments separate
- **Order Fulfillment**: Maintain separate moves for different sales orders to preserve order traceability

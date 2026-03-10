This module allows you to prevent stock move consolidation at the operation type level.

This module adds a **"Prevent Move Consolidation"** boolean field to stock operation types. When enabled, stock moves created with that operation type will:

- **Not be added to existing pickings** - each move group creates its own picking
- **Keep their origins separate** - no consolidation of origins

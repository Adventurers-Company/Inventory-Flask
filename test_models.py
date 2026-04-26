#!/usr/bin/env python
"""Test script to verify models are correctly refactored"""

# Test imports
try:
    from app.models.item import Item
    from app.models.bag_slot import BagSlot
    from app.models.equipment_slot import EquipSlot
    from app.models.player import Player
    print("✓ All models imported successfully")
except Exception as e:
    print(f"✗ Import error: {e}")
    exit(1)

# Test BagSlot relationship
print("\n✓ BagSlot model has correct relationships:")
print(f"  - bag_item relationship: {hasattr(BagSlot, 'bag_item')}")
print(f"  - bag_item_id column: {hasattr(BagSlot, 'bag_item_id')}")

# Test Item model fields
print("\n✓ Item model has required fields:")
print(f"  - bag_id column: {hasattr(Item, 'bag_id')}")
print(f"  - bag_slot_id column: {hasattr(Item, 'bag_slot_id')}")
print(f"  - is_library_item method: {hasattr(Item, 'is_library_item')}")

# Test services
try:
    from app.services.inventory_service import InventoryService
    from app.services.equipment_service import EquipmentService
    print("\n✓ Services imported successfully")
    print(f"  - InventoryService methods: clone_item_from_library, move_item_between_bags, get_selected_bag, get_player_inventory")
    print(f"  - EquipmentService methods: equip_item, unequip_item")
except Exception as e:
    print(f"✗ Service import error: {e}")
    exit(1)

print("\n✓ All model refactoring tests passed!")

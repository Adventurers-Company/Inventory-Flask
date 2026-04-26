"""
Serviço de Equipamento
Lógica de negócio para equipar/desequipar itens
"""
from app import db
from app.models.item import Item
from app.models.equipment_slot import EquipSlot
from app.models.bag_slot import BagSlot


class EquipmentService:
    """Gerencia equipamento e desequipamento de itens"""

    @staticmethod
    def equip_item(item_id, equipment_slot_id):
        item = Item.query.get(item_id)
        if not item or item.is_library_item():
            return {'success': False, 'error': 'Item not found'}

        if item.bag_id is None:
            return {'success': False, 'error': 'Item must be in a bag to equip'}

        slot = EquipSlot.query.get(equipment_slot_id)
        if not slot:
            return {'success': False, 'error': 'Equipment slot not found'}

        if item.is_equipped():
            return {'success': False, 'error': 'Item is already equipped'}

        if not slot.is_empty():
            return {'success': False, 'error': 'Slot is already occupied'}

        if slot.is_locked():
            return {'success': False, 'error': 'Slot is locked'}

        if not EquipmentService._validate_item_slot_compatibility(item, slot):
            return {'success': False, 'error': 'Item cannot be equipped in this slot'}

        try:
            stats = item.get_stats()
            is_two_handed = stats.get('two_handed', False)

            if is_two_handed and slot.name == 'Arma 1':
                other_slot = EquipSlot.query.filter_by(name='Arma 2').first()
                if not other_slot:
                    return {'success': False, 'error': 'Second weapon slot not found'}
                if not other_slot.is_empty():
                    return {'success': False, 'error': 'Second weapon slot is occupied'}

            item.bag_id = None
            item.equip_slot_id = slot.id
            slot.item_id = item.id

            db.session.commit()

            return {
                'success': True,
                'message': 'Item equipped successfully',
                'item': item.to_dict(),
                'slot': slot.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def unequip_item(item_id, target_bag_item_id=None):
        item = Item.query.get(item_id)
        if not item or not item.is_equipped():
            return {'success': False, 'error': 'Item not found'}

        try:
            current_slot = EquipSlot.query.get(item.equip_slot_id)

            if not target_bag_item_id:
                # Find first equipped bag with space
                bag_slot = BagSlot.query.filter(BagSlot.bag_item_id.isnot(None)).order_by(BagSlot.index.asc()).first()
                if not bag_slot or not bag_slot.bag_item:
                    return {'success': False, 'error': 'No equipped bag available'}
                
                target_bag_item = bag_slot.bag_item
                # Check space: count items in this bag
                items_in_bag = Item.query.filter_by(bag_id=target_bag_item.id).count()
                bag_slots_available = target_bag_item.data.get('slots', 24) if target_bag_item.data else 24
                
                if items_in_bag >= bag_slots_available:
                    return {'success': False, 'error': 'No bag has space for this item'}
            else:
                target_bag_item = Item.query.get(target_bag_item_id)
                if not target_bag_item or target_bag_item.item_type != 'bag':
                    return {'success': False, 'error': 'Target bag not found'}
                
                # Check space
                items_in_bag = Item.query.filter_by(bag_id=target_bag_item.id).count()
                bag_slots_available = target_bag_item.data.get('slots', 24) if target_bag_item.data else 24
                
                if items_in_bag >= bag_slots_available:
                    return {'success': False, 'error': 'Target bag does not have space'}

            item.equip_slot_id = None
            item.bag_id = target_bag_item.id
            if current_slot:
                current_slot.item_id = None

            db.session.commit()

            return {
                'success': True,
                'message': 'Item unequipped successfully',
                'item': item.to_dict(),
                'slot': current_slot.to_dict() if current_slot else None,
                'bag': target_bag_item.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _validate_item_slot_compatibility(item, slot):
        item_type = item.item_type
        accepted_type = slot.accepted_type

        if item_type == 'consumable':
            return False

        if accepted_type == 'weapon':
            if item_type == 'shield':
                return slot.name == 'Arma 2'
            return item_type in ['sword', 'axe', 'dagger', 'bow']

        return item_type == accepted_type

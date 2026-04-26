"""
Serviço de Inventário
Lógica de negócio para operações de bolsas e itens
"""
from app import db
from app.models.item import Item
from app.models.bag_slot import BagSlot
from app.models.equipment_slot import EquipSlot
from app.models.player import Player


class InventoryService:
    """Gerencia operações de inventário e biblioteca"""

    @staticmethod
    def clone_item_from_library(item_id, bag_item_id):
        """
        Clona um item da biblioteca para uma bolsa.
        bag_item_id: ID do item de tipo "bag" no qual adicionar o item
        """
        base_item = Item.query.get(item_id)
        if not base_item or not base_item.is_library_item():
            return {'success': False, 'error': 'Item base not found'}

        bag_item = Item.query.get(bag_item_id)
        if not bag_item or bag_item.item_type != 'bag':
            return {'success': False, 'error': 'Bag not found'}

        # Verificar espaço: contar itens já no bag
        items_in_bag = Item.query.filter_by(bag_id=bag_item.id).count()
        bag_slots = bag_item.data.get('slots', 24) if bag_item.data else 24
        if items_in_bag >= bag_slots:
            return {'success': False, 'error': 'Bag is full. Not enough space.'}

        try:
            item = Item(
                name=base_item.name,
                item_type=base_item.item_type,
                weight=base_item.weight,
                rarity=base_item.rarity,
                data=base_item.get_stats(),
                bag_id=bag_item.id,
            )
            db.session.add(item)
            db.session.commit()
            return {
                'success': True,
                'item': item.to_dict(),
                'bag': bag_item.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def move_item_between_bags(item_id, source_bag_item_id, target_bag_item_id):
        """
        Move um item entre duas bolsas.
        source_bag_item_id, target_bag_item_id: IDs dos items de tipo "bag"
        """
        item = Item.query.get(item_id)
        if not item or item.is_library_item() or item.is_equipped():
            return {'success': False, 'error': 'Item not found or cannot be moved'}

        source_bag = Item.query.get(source_bag_item_id)
        target_bag = Item.query.get(target_bag_item_id)

        if not source_bag or source_bag.item_type != 'bag' or not target_bag or target_bag.item_type != 'bag':
            return {'success': False, 'error': 'Bag not found'}

        if item.bag_id != source_bag.id:
            return {'success': False, 'error': 'Item is not in source bag'}

        # Verificar espaço na bolsa destino
        items_in_target = Item.query.filter_by(bag_id=target_bag.id).count()
        target_bag_slots = target_bag.data.get('slots', 24) if target_bag.data else 24
        if items_in_target >= target_bag_slots:
            return {'success': False, 'error': 'Target bag does not have enough space'}

        try:
            item.bag_id = target_bag.id
            db.session.commit()
            return {
                'success': True,
                'item': item.to_dict(),
                'source_bag': source_bag.to_dict(),
                'target_bag': target_bag.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def move_bag_between_slots(source_slot_index, target_slot_index):
        """Move or swap equipped bags between fixed bag slots."""
        if source_slot_index == target_slot_index:
            return {'success': False, 'error': 'Same slot selected'}

        source_slot = BagSlot.query.filter_by(index=source_slot_index).first()
        target_slot = BagSlot.query.filter_by(index=target_slot_index).first()

        if not source_slot or not target_slot:
            return {'success': False, 'error': 'Bag slot not found'}
        if not source_slot.bag_item_id:
            return {'success': False, 'error': 'Source slot is empty'}

        try:
            source_item = source_slot.bag_item
            target_item = target_slot.bag_item

            if target_item:
                source_slot.bag_item_id = target_item.id
                target_slot.bag_item_id = source_item.id
                source_item.bag_slot_id = target_slot.id
                target_item.bag_slot_id = source_slot.id
            else:
                source_slot.bag_item_id = None
                target_slot.bag_item_id = source_item.id
                source_item.bag_slot_id = target_slot.id

            db.session.commit()
            return {
                'success': True,
                'source_slot': source_slot.to_dict(),
                'target_slot': target_slot.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_inventory_item(item_id):
        item = Item.query.get(item_id)
        if not item or item.is_library_item():
            return None
        return item.to_dict()

    @staticmethod
    def update_inventory_item(item_id, payload):
        item = Item.query.get(item_id)
        if not item or item.is_library_item():
            return {'success': False, 'error': 'Item not found'}
        if item.item_type == 'bag':
            return {'success': False, 'error': 'Bag items cannot be edited here'}

        try:
            item.name = payload.get('name', item.name).strip()
            item.item_type = payload.get('item_type', item.item_type).strip()
            if 'weight' in payload:
                item.weight = float(payload.get('weight'))
            if 'rarity' in payload:
                item.rarity = payload.get('rarity')
            if 'data' in payload:
                item.data = payload.get('data') or {}

            db.session.commit()
            return {'success': True, 'item': item.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_inventory_item(item_id):
        item = Item.query.get(item_id)
        if not item or item.is_library_item():
            return {'success': False, 'error': 'Item not found'}
        
        # Se é uma bolsa, verifica se está vazia
        if item.item_type == 'bag':
            items_in_bag = Item.query.filter_by(bag_id=item.id).count()
            if items_in_bag > 0:
                return {'success': False, 'error': f'Bag has {items_in_bag} items. Empty it first.'}


        try:
            if item.equip_slot_id:
                slot = EquipSlot.query.get(item.equip_slot_id)
                if slot:
                    slot.item_id = None
            db.session.delete(item)
            db.session.commit()
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def duplicate_inventory_item(item_id):
        item = Item.query.get(item_id)
        if not item or item.is_library_item():
            return {'success': False, 'error': 'Item not found'}
        if item.item_type == 'bag':
            return {'success': False, 'error': 'Bag items cannot be duplicated here'}
        if not item.bag_id:
            return {'success': False, 'error': 'Item must be in a bag to duplicate'}

        bag_item = Item.query.get(item.bag_id)
        if not bag_item or bag_item.item_type != 'bag':
            return {'success': False, 'error': 'Bag not found'}

        items_in_bag = Item.query.filter_by(bag_id=bag_item.id).count()
        bag_slots = bag_item.data.get('slots', 24) if bag_item.data else 24
        if items_in_bag >= bag_slots:
            return {'success': False, 'error': 'Bag is full. Not enough space.'}

        try:
            new_item = Item(
                name=item.name,
                item_type=item.item_type,
                weight=item.weight,
                rarity=item.rarity,
                data=item.get_stats(),
                bag_id=bag_item.id,
            )
            db.session.add(new_item)
            db.session.commit()
            return {'success': True, 'item': new_item.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def move_inventory_item(item_id, target_bag_item_id):
        item = Item.query.get(item_id)
        if not item or item.is_library_item():
            return {'success': False, 'error': 'Item not found'}
        if item.item_type == 'bag':
            return {'success': False, 'error': 'Bag items cannot be moved here'}

        target_bag = Item.query.get(target_bag_item_id)
        if not target_bag or target_bag.item_type != 'bag':
            return {'success': False, 'error': 'Target bag not found'}

        items_in_bag = Item.query.filter_by(bag_id=target_bag.id).count()
        bag_slots = target_bag.data.get('slots', 24) if target_bag.data else 24
        if items_in_bag >= bag_slots:
            return {'success': False, 'error': 'Target bag does not have enough space'}

        try:
            item.bag_id = target_bag.id
            db.session.commit()
            return {'success': True, 'item': item.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def equip_bag_in_slot(item_id, slot_index):
        """Equipe uma bolsa (item_type='bag') em um slot fixo pelo index."""
        base_item = Item.query.get(item_id)
        if not base_item or base_item.item_type != 'bag':
            return {'success': False, 'error': 'Invalid bag item'}

        slot = BagSlot.query.filter_by(index=slot_index).first()
        if not slot:
            return {'success': False, 'error': 'Bag slot not found'}
        if slot.bag_item_id is not None:
            return {'success': False, 'error': 'Bag slot already occupied'}

        try:
            if base_item.is_library_item():
                bag_item = Item(
                    name=base_item.name,
                    item_type=base_item.item_type,
                    weight=base_item.weight,
                    rarity=base_item.rarity,
                    data=base_item.get_stats(),
                    bag_slot_id=slot.id,
                )
                db.session.add(bag_item)
                db.session.flush()
            else:
                if base_item.bag_id or base_item.equip_slot_id or base_item.bag_slot_id:
                    return {'success': False, 'error': 'Bag item is already in use'}
                bag_item = base_item
                bag_item.bag_slot_id = slot.id

            slot.bag_item_id = bag_item.id
            db.session.commit()
            return {
                'success': True,
                'slot': slot.to_dict(),
                'bag_item': bag_item.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def unequip_bag_from_slot(slot_index):
        """Remove uma bolsa de um slot fixo e adiciona ao inventário de outra bolsa."""
        slot = BagSlot.query.filter_by(index=slot_index).first()
        if not slot or not slot.bag_item_id:
            return {'success': False, 'error': 'Bag slot is empty'}

        try:
            bag_item = Item.query.get(slot.bag_item_id)
            if not bag_item:
                return {'success': False, 'error': 'Bag not found'}

            # Procura uma bolsa equipada com espaço disponível
            equipped_slots = BagSlot.query.filter(BagSlot.bag_item_id.isnot(None)).all()
            target_bag = None

            for equipped_slot in equipped_slots:
                if equipped_slot.index == slot_index:  # Pula o slot sendo desequipado
                    continue
                
                equipped_bag = equipped_slot.bag_item
                items_count = Item.query.filter_by(bag_id=equipped_bag.id).count()
                max_slots = equipped_bag.data.get('slots', 24) if equipped_bag.data else 24
                
                if items_count < max_slots:
                    target_bag = equipped_bag
                    break

            if not target_bag:
                return {'success': False, 'error': 'No equipped bag with available space found'}

            # Adiciona a bolsa ao inventário da bolsa-alvo
            bag_item.bag_slot_id = None
            bag_item.bag_id = target_bag.id
            slot.bag_item_id = None

            db.session.commit()
            return {
                'success': True,
                'slot': slot.to_dict(),
                'bag_item': bag_item.to_dict(),
                'target_bag': target_bag.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_bag(bag_item_id):
        """Deleta uma bolsa (equipada ou na biblioteca)."""
        bag_item = Item.query.get(bag_item_id)
        if not bag_item or bag_item.item_type != 'bag':
            return {'success': False, 'error': 'Bag not found'}

        # Verifica se há itens na bolsa
        items_in_bag = Item.query.filter_by(bag_id=bag_item.id).count()
        if items_in_bag > 0:
            return {'success': False, 'error': f'Bag has {items_in_bag} items. Empty it first.'}

        try:
            # Se a bolsa está equipada, desacopla do slot
            bag_slot = BagSlot.query.filter_by(bag_item_id=bag_item.id).first()
            if bag_slot:
                bag_slot.bag_item_id = None

            db.session.delete(bag_item)
            db.session.commit()
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_bag_slots():
        slots = BagSlot.query.order_by(BagSlot.index.asc()).all()
        return [slot.to_dict() for slot in slots]

    @staticmethod
    def get_selected_bag(selected_bag_item_id=None):
        """
        Retorna o item de bolsa selecionado ou o primeiro equipado.
        """
        if selected_bag_item_id:
            bag_item = Item.query.get(selected_bag_item_id)
            if bag_item and bag_item.item_type == 'bag':
                return bag_item

        # Retorna o primeiro bag slot equipado
        slot = BagSlot.query.filter(BagSlot.bag_item_id.isnot(None)).order_by(BagSlot.index.asc()).first()
        return slot.bag_item if slot else None

    @staticmethod
    def get_player_inventory(player_id, selected_bag_item_id=None):
        player = Player.query.get(player_id)
        if not player:
            return None

        selected_bag = InventoryService.get_selected_bag(selected_bag_item_id)
        
        # Get all equipped bag items from bag slots
        equipped_bag_slots = BagSlot.query.filter(BagSlot.bag_item_id.isnot(None)).all()
        
        equipment_slots = EquipSlot.query.all()

        # Calculate total weight and items across all equipped bags
        total_weight = 0
        total_items = 0
        for slot in equipped_bag_slots:
            if slot.bag_item:
                items_in_bag = Item.query.filter_by(bag_id=slot.bag_item.id).all()
                total_items += len(items_in_bag)
                total_weight += sum(item.weight for item in items_in_bag)
                total_weight += slot.bag_item.weight

        # Enhance selected_bag with calculated fields
        selected_bag_data = selected_bag.to_dict() if selected_bag else None
        if selected_bag_data:
            items_in_selected = Item.query.filter_by(bag_id=selected_bag.id).all()
            selected_bag_data['used_slots'] = len(items_in_selected)
            selected_bag_data['max_slots'] = selected_bag_data.get('stats', {}).get('slots', 24)
            selected_bag_data['max_weight'] = selected_bag_data.get('stats', {}).get('max_weight', 500)
            selected_bag_data['current_weight'] = sum(item.weight for item in items_in_selected) + selected_bag.weight
            selected_bag_data['items'] = [item.to_dict() for item in items_in_selected]

        return {
            'player': player.to_dict(),
            'bag_slots': InventoryService.get_bag_slots(),
            'selected_bag': selected_bag_data,
            'equipment_slots': [slot.to_dict() for slot in equipment_slots],
            'total_weight': total_weight,
            'total_items': total_items,
        }

    @staticmethod
    def get_bag_details(bag_item_id):
        bag = Item.query.get(bag_item_id)
        if not bag or bag.item_type != 'bag':
            return None
        return bag.to_dict()

    @staticmethod
    def get_item_library(search=None, item_type=None):
        query = Item.query.filter(
            Item.bag_id.is_(None), 
            Item.equip_slot_id.is_(None),
            Item.bag_slot_id.is_(None)
        )

        if search:
            query = query.filter(Item.name.ilike(f'%{search}%'))

        if item_type:
            query = query.filter(Item.item_type == item_type)

        items = query.order_by(Item.rarity.desc(), Item.name.asc()).all()
        return [item.to_dict() for item in items]

    @staticmethod
    def create_library_item(payload):
        try:
            name = payload.get('name', '').strip()
            item_type = payload.get('item_type', '').strip()
            if not name or not item_type:
                return {'success': False, 'error': 'Name and type are required'}

            item = Item(
                name=name,
                item_type=item_type,
                weight=float(payload.get('weight', 0)),
                rarity=payload.get('rarity', 'common'),
                data=payload.get('data') or {},
            )
            db.session.add(item)
            db.session.commit()
            return {'success': True, 'item': item.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def update_library_item(item_id, payload):
        item = Item.query.get(item_id)
        if not item or not item.is_library_item():
            return {'success': False, 'error': 'Item not found'}

        try:
            item.name = payload.get('name', item.name).strip()
            item.item_type = payload.get('item_type', item.item_type).strip()
            if 'weight' in payload:
                item.weight = float(payload.get('weight'))
            if 'rarity' in payload:
                item.rarity = payload.get('rarity')
            if 'data' in payload:
                item.data = payload.get('data') or {}

            db.session.commit()
            return {'success': True, 'item': item.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_library_item(item_id):
        item = Item.query.get(item_id)
        if not item or not item.is_library_item():
            return {'success': False, 'error': 'Item not found'}

        try:
            db.session.delete(item)
            db.session.commit()
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

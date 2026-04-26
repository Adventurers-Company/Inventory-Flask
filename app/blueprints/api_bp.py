"""
Blueprint de API - Rotas REST para operações de inventário
"""
from flask import Blueprint, request, jsonify
from app.models.player import Player
from app.services.inventory_service import InventoryService
from app.services.calculation_service import CalculationService
import json

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/inventory/create-item', methods=['POST'])
def create_item_from_library():
    """Cria instância de item da biblioteca"""
    data = request.get_json()
    result = InventoryService.clone_item_from_library(
        item_id=data.get('item_id'),
        bag_item_id=data.get('bag_item_id')
    )
    
    return jsonify(result)

@bp.route('/inventory/move-item', methods=['POST'])
def move_item():
    """Move item entre bolsas"""
    data = request.get_json()
    result = InventoryService.move_item_between_bags(
        item_id=data.get('item_id'),
        source_bag_item_id=data.get('source_bag_item_id'),
        target_bag_item_id=data.get('target_bag_item_id')
    )
    
    return jsonify(result)

@bp.route('/inventory/move-bag-slot', methods=['POST'])
def move_bag_slot():
    """Move ou troca bolsas entre slots fixos"""
    data = request.get_json()
    result = InventoryService.move_bag_between_slots(
        source_slot_index=data.get('source_slot_index'),
        target_slot_index=data.get('target_slot_index')
    )
    return jsonify(result)

@bp.route('/inventory/items/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    item = InventoryService.get_inventory_item(item_id)
    if not item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404
    return jsonify({'success': True, 'item': item})

@bp.route('/inventory/items/<int:item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    payload = request.get_json() or {}
    data_raw = payload.get('data')
    if isinstance(data_raw, str):
        try:
            payload['data'] = json.loads(data_raw) if data_raw.strip() else {}
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid JSON in data'}), 400
    result = InventoryService.update_inventory_item(item_id, payload)
    return jsonify(result)

@bp.route('/inventory/items/<int:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    result = InventoryService.delete_inventory_item(item_id)
    return jsonify(result)

@bp.route('/inventory/items/<int:item_id>/duplicate', methods=['POST'])
def duplicate_inventory_item(item_id):
    result = InventoryService.duplicate_inventory_item(item_id)
    return jsonify(result)

@bp.route('/inventory/items/<int:item_id>/move', methods=['POST'])
def move_inventory_item(item_id):
    data = request.get_json() or {}
    result = InventoryService.move_inventory_item(
        item_id=item_id,
        target_bag_item_id=data.get('target_bag_item_id')
    )
    return jsonify(result)

@bp.route('/inventory/equip-bag', methods=['POST'])
def equip_bag():
    """Equipa uma bolsa em um slot fixo"""
    data = request.get_json()
    result = InventoryService.equip_bag_in_slot(
        item_id=data.get('item_id'),
        slot_index=data.get('slot_index')
    )
    return jsonify(result)

@bp.route('/inventory/unequip-bag', methods=['POST'])
def unequip_bag():
    """Remove uma bolsa de um slot fixo"""
    data = request.get_json()
    result = InventoryService.unequip_bag_from_slot(
        slot_index=data.get('slot_index')
    )
    return jsonify(result)

@bp.route('/inventory/bags/<int:bag_item_id>', methods=['DELETE'])
def delete_bag(bag_item_id):
    """Deleta uma bolsa"""
    result = InventoryService.delete_bag(bag_item_id)
    return jsonify(result)

@bp.route('/inventory/organize', methods=['POST'])
def organize_bag():
    """Organiza automaticamente uma bolsa"""
    data = request.get_json()
    return jsonify({'success': True, 'message': 'Organizar ainda nao implementado'})

@bp.route('/library/search', methods=['GET'])
def search_library():
    """Busca na biblioteca de itens"""
    search = request.args.get('search', '')
    item_type = request.args.get('type', '')
    
    items = InventoryService.get_item_library(search=search or None, item_type=item_type or None)
    
    return jsonify({
        'success': True,
        'items': items,
        'count': len(items)
    })

@bp.route('/bags/<int:bag_item_id>', methods=['GET'])
def get_bag_details(bag_item_id):
    bag = InventoryService.get_bag_details(bag_item_id)
    if not bag:
        return jsonify({'success': False, 'error': 'Bag not found'}), 404
    return jsonify({'success': True, 'bag': bag})

@bp.route('/items', methods=['POST'])
def create_item():
    payload = request.get_json() or {}
    data_raw = payload.get('data')
    if isinstance(data_raw, str):
        try:
            payload['data'] = json.loads(data_raw) if data_raw.strip() else {}
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid JSON in data'}), 400
    result = InventoryService.create_library_item(payload)
    return jsonify(result)

@bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    payload = request.get_json() or {}
    data_raw = payload.get('data')
    if isinstance(data_raw, str):
        try:
            payload['data'] = json.loads(data_raw) if data_raw.strip() else {}
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid JSON in data'}), 400
    result = InventoryService.update_library_item(item_id, payload)
    return jsonify(result)

@bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    result = InventoryService.delete_library_item(item_id)
    return jsonify(result)

@bp.route('/stats/calculate', methods=['GET'])
def calculate_stats():
    """Calcula stats do jogador"""
    player = Player.query.first()
    
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    stats = CalculationService.calculate_player_stats(player)
    formatted_stats = CalculationService.format_stat_display(stats)
    summary = CalculationService.get_equipment_summary(player)
    
    return jsonify({
        'success': True,
        'stats': stats,
        'formatted_stats': formatted_stats,
        'summary': summary
    })

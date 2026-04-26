"""
Blueprint de Equipamento - Rotas de equipamento
"""
from flask import Blueprint, request, jsonify
from app.services.equipment_service import EquipmentService

bp = Blueprint('equipment', __name__, url_prefix='/equipment')

@bp.route('/equip', methods=['POST'])
def equip():
    """Equipa um item"""
    data = request.get_json()
    result = EquipmentService.equip_item(
        item_id=data.get('item_id'),
        equipment_slot_id=data.get('slot_id')
    )
    
    return jsonify(result)

@bp.route('/unequip', methods=['POST'])
def unequip():
    """Desequipa um item"""
    data = request.get_json()
    
    result = EquipmentService.unequip_item(
        item_id=data.get('item_id'),
        target_bag_item_id=data.get('target_bag_item_id')
    )
    
    return jsonify(result)

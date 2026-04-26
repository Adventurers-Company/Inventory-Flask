"""
Blueprint de Inventário - Rotas principais
"""
from flask import Blueprint, render_template, request, jsonify
from app.models.player import Player
from app.services.inventory_service import InventoryService
from app.services.calculation_service import CalculationService

bp = Blueprint('inventory', __name__, url_prefix='/')

@bp.route('/')
def index():
    """Página principal do inventário"""
    player = Player.query.first()
    
    if not player:
        return "Player not found", 404
    
    selected_bag_item_id = request.args.get('bag_item_id', type=int)
    inventory_data = InventoryService.get_player_inventory(player.id, selected_bag_item_id=selected_bag_item_id)
    equipment_summary = CalculationService.get_equipment_summary(player)
    item_library = InventoryService.get_item_library()
    
    return render_template(
        'index.html',
        player=player,
        inventory_data=inventory_data,
        equipment_summary=equipment_summary,
        item_library=item_library,
    )

@bp.route('/api/player', methods=['GET'])
def get_player_data():
    """API - Retorna dados do jogador"""
    player = Player.query.first()
    
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    selected_bag_item_id = request.args.get('bag_item_id', type=int)
    inventory_data = InventoryService.get_player_inventory(player.id, selected_bag_item_id=selected_bag_item_id)
    equipment_summary = CalculationService.get_equipment_summary(player)
    
    return jsonify({
        'player': inventory_data['player'],
        'bag_slots': inventory_data['bag_slots'],
        'selected_bag': inventory_data['selected_bag'],
        'equipment_slots': inventory_data['equipment_slots'],
        'stats': equipment_summary['total_stats'],
        'total_weight': inventory_data['total_weight'],
        'total_items': inventory_data['total_items'],
    })

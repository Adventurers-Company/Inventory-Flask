"""
Inicialização da aplicação Flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import get_config

db = SQLAlchemy()

def create_app(config_name=None):
    """Factory pattern para criar a aplicação Flask"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Carrega configuração
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Inicializa extensões
    db.init_app(app)
    
    # Registra blueprints
    _register_blueprints(app)
    
    # Cria tabelas do banco de dados
    with app.app_context():
        db.create_all()
        _seed_initial_data()
    
    return app

def _register_blueprints(app):
    """Registra todos os blueprints"""
    from app.blueprints import inventory_bp, equipment_bp, api_bp
    
    app.register_blueprint(inventory_bp.bp)
    app.register_blueprint(equipment_bp.bp)
    app.register_blueprint(api_bp.bp)

def _seed_initial_data():
    """Popula dados iniciais no banco de dados"""
    from app.models.player import Player
    from app.models.bag_slot import BagSlot
    from app.models.equipment_slot import EquipSlot
    from app.models.item import Item
    
    # Verifica se já existe um jogador
    if Player.query.first():
        return
    
    # Cria jogador padrão
    player = Player(name="Heroi da Aventura", level=1, experience=0)
    db.session.add(player)
    db.session.flush()

    # Cria itens de bolsa (bags são items com type="bag")
    bag_items = [
        Item(name="Mochila", item_type="bag", weight=10, rarity="common", data={"slots": 24, "max_weight": 500}),
        Item(name="Bolsa 2", item_type="bag", weight=12, rarity="common", data={"slots": 24, "max_weight": 500}),
        Item(name="Bolsa 3", item_type="bag", weight=12, rarity="uncommon", data={"slots": 24, "max_weight": 500}),
    ]
    db.session.add_all(bag_items)
    db.session.flush()

    # Cria 6 slots fixos de bolsa (inicialmente vazios)
    bag_slots = []
    for i in range(6):
        bag_slots.append(BagSlot(index=i))
    db.session.add_all(bag_slots)
    db.session.flush()

    # Cria slots de equipamento
    equipment_slots = [
        EquipSlot(name="Capacete", accepted_type="helmet"),
        EquipSlot(name="Ombreira", accepted_type="shoulder"),
        EquipSlot(name="Peitoral", accepted_type="chest"),
        EquipSlot(name="Calca", accepted_type="legs"),
        EquipSlot(name="Bota", accepted_type="boots"),
        EquipSlot(name="Colar", accepted_type="necklace"),
        EquipSlot(name="Amuleto", accepted_type="amulet"),
        EquipSlot(name="Anel 1", accepted_type="ring"),
        EquipSlot(name="Anel 2", accepted_type="ring"),
        EquipSlot(name="Anel 3", accepted_type="ring"),
        EquipSlot(name="Capa", accepted_type="cloak"),
        EquipSlot(name="Arma 1", accepted_type="weapon"),
        EquipSlot(name="Arma 2", accepted_type="weapon"),
    ]
    db.session.add_all(equipment_slots)
    db.session.flush()

    # Cria itens de biblioteca
    library_items = [
        Item(
            name="Capacete de Ferro",
            item_type="helmet",
            weight=8,
            rarity="common",
            data={"armor": 5, "constituicao": 2}
        ),
        Item(
            name="Peitoral Mithryl",
            item_type="chest",
            weight=15,
            rarity="rare",
            data={"armor": 12, "constituicao": 4, "resistencia": 3}
        ),
        Item(
            name="Calca de Couro",
            item_type="legs",
            weight=10,
            rarity="common",
            data={"armor": 4, "constituicao": 1}
        ),
        Item(
            name="Botas de Velocidade",
            item_type="boots",
            weight=5,
            rarity="uncommon",
            data={"armor": 2, "destreza": 3, "velocidade": 4}
        ),
        Item(
            name="Colar do Sabio",
            item_type="necklace",
            weight=2,
            rarity="rare",
            data={"inteligencia": 5, "foco": 4, "sabedoria": 3}
        ),
        Item(
            name="Anel de Forca",
            item_type="ring",
            weight=1,
            rarity="uncommon",
            data={"forca": 4, "poder": 2}
        ),
        Item(
            name="Amuleto da Protecao",
            item_type="amulet",
            weight=3,
            rarity="rare",
            data={"armor": 6, "resistencia": 5, "constituicao": 3}
        ),
        Item(
            name="Espada Longa",
            item_type="sword",
            weight=12,
            rarity="common",
            data={"forca": 3, "destreza": 2, "two_handed": False}
        ),
        Item(
            name="Espada Grande de Mithril",
            item_type="sword",
            weight=20,
            rarity="rare",
            data={"forca": 6, "poder": 4, "constituicao": 2, "two_handed": True}
        ),
        Item(
            name="Machado de Batalha",
            item_type="axe",
            weight=18,
            rarity="uncommon",
            data={"forca": 5, "constituicao": 2, "poder": 3, "two_handed": True}
        ),
        Item(
            name="Adaga Envenenada",
            item_type="dagger",
            weight=4,
            rarity="uncommon",
            data={"destreza": 4, "velocidade": 2, "instinto": 2, "two_handed": False}
        ),
        Item(
            name="Arco Elfico",
            item_type="bow",
            weight=10,
            rarity="uncommon",
            data={"destreza": 5, "sentidos": 3, "velocidade": 2, "two_handed": False}
        ),
        Item(
            name="Pocao de Vida Pequena",
            item_type="consumable",
            weight=1,
            rarity="common",
            data={"constituicao": 5}
        ),
        Item(
            name="Pocao de Mana Pequena",
            item_type="consumable",
            weight=1,
            rarity="common",
            data={"foco": 5}
        ),
    ]
    db.session.add_all(library_items)
    db.session.commit()

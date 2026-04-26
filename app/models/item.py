"""
Modelo de Item (Biblioteca e Instância)
"""
from app import db


class Item(db.Model):
    """Item que pode existir na biblioteca ou no inventário"""
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    rarity = db.Column(db.String(30), default='common')
    data = db.Column(db.JSON, default={})

    bag_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    bag_slot_id = db.Column(db.Integer, db.ForeignKey('bag_slot.id'), nullable=True)
    equip_slot_id = db.Column(db.Integer, db.ForeignKey('equipment_slot.id'), nullable=True)

    def __repr__(self):
        return f'<Item {self.name}>'

    def is_equipped(self):
        return self.equip_slot_id is not None

    def is_library_item(self):
        return self.bag_id is None and self.bag_slot_id is None and self.equip_slot_id is None

    def get_stats(self):
        if self.data is None:
            return {}
        return self.data.copy() if isinstance(self.data, dict) else {}

    def get_rarity_color(self):
        colors = {
            'common': '#FFFFFF',
            'uncommon': '#1EFF00',
            'rare': '#0070DD',
            'epic': '#A335EE',
            'legendary': '#FF8000',
        }
        return colors.get(self.rarity, '#FFFFFF')

    def to_dict(self, include_stats=True):
        return {
            'id': self.id,
            'name': self.name,
            'item_type': self.item_type,
            'weight': self.weight,
            'rarity': self.rarity,
            'rarity_color': self.get_rarity_color(),
            'bag_id': self.bag_id,
            'bag_slot_id': self.bag_slot_id,
            'equip_slot_id': self.equip_slot_id,
            'is_equipped': self.is_equipped(),
            'is_library': self.is_library_item(),
            'stats': self.get_stats() if include_stats else None,
        }

"""
Modelo de Slot de Equipamento
"""
from app import db


class EquipSlot(db.Model):
    """Slot fixo para equipamento"""
    __tablename__ = 'equipment_slot'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    accepted_type = db.Column(db.String(50), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)

    def __repr__(self):
        return f'<EquipSlot {self.name}>'

    def get_equipped_item(self):
        from app.models.item import Item
        if not self.item_id:
            return None
        return Item.query.get(self.item_id)

    def is_empty(self):
        return self.item_id is None

    def is_locked(self):
        if self.accepted_type != 'weapon' or self.name != 'Arma 2':
            return False
        from app.models.item import Item
        primary = EquipSlot.query.filter_by(name='Arma 1').first()
        if not primary or not primary.item_id:
            return False
        primary_item = Item.query.get(primary.item_id)
        if not primary_item:
            return False
        return bool(primary_item.get_stats().get('two_handed', False))

    def to_dict(self, include_item=True):
        equipped = self.get_equipped_item()
        return {
            'id': self.id,
            'name': self.name,
            'accepted_type': self.accepted_type,
            'item_id': self.item_id,
            'is_empty': self.is_empty(),
            'is_locked': self.is_locked(),
            'equipped_item': equipped.to_dict() if equipped and include_item else None,
        }

"""
Modelo de Bolsa/Mochila
"""
from app import db


class Bag(db.Model):
    """Modelo de bolsa equipada em um slot fixo"""
    __tablename__ = 'bag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    max_slots = db.Column(db.Integer, nullable=False)
    max_weight = db.Column(db.Float, nullable=False)

    items = db.relationship('Item', backref='bag', lazy=True)

    def __repr__(self):
        return f'<Bag {self.name}>'

    def get_current_weight(self):
        return sum(item.weight for item in self.items)

    def get_used_slots(self):
        return len(self.items)

    def has_space(self, weight=0, slots_needed=1):
        available_slots = self.max_slots - self.get_used_slots()
        current_weight = self.get_current_weight()
        return (available_slots >= slots_needed and current_weight + weight <= self.max_weight)

    def to_dict(self, include_items=True):
        return {
            'id': self.id,
            'name': self.name,
            'max_slots': self.max_slots,
            'max_weight': self.max_weight,
            'used_slots': self.get_used_slots(),
            'current_weight': self.get_current_weight(),
            'items': [item.to_dict() for item in self.items] if include_items else None,
        }

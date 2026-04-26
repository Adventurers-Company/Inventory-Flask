"""
Modelo de Slot de Bolsa (fixo)
"""
from app import db


class BagSlot(db.Model):
    """Slot fixo para bolsa equipada"""
    __tablename__ = 'bag_slot'

    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False, unique=True)  # 0-5
    bag_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)

    bag_item = db.relationship('Item', backref='equipped_bag_slot', uselist=False, foreign_keys=[bag_item_id])

    def __repr__(self):
        return f'<BagSlot {self.index}>'

    def to_dict(self):
        return {
            'id': self.id,
            'index': self.index,
            'bag_item_id': self.bag_item_id,
            'equipped_item': self.bag_item.to_dict() if self.bag_item else None,
        }

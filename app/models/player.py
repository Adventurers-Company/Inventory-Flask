"""
Modelo de Jogador
"""
from app import db
from datetime import datetime


class Player(db.Model):
    """Modelo do jogador"""
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Player {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'experience': self.experience,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

from typing import Any
from sqlalchemy.orm import validates, relationship
from . import db
from .base import BaseModel


class Subscription(BaseModel):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    frequency = db.Column(db.String(20), nullable=False, default='weekly')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    game = relationship("Game", back_populates="subscriptions")

    @validates('email')
    def validate_email(self, key, email: str | None) -> str:
        if email is None or not isinstance(email, str) or '@' not in email or not email.strip():
            raise ValueError("Subscriber email must be a valid email address")
        return email.strip()

    @validates('frequency')
    def validate_frequency(self, key, frequency: str | None) -> str:
        allowed_frequencies = {'immediate', 'daily', 'weekly'}
        if frequency is None:
            raise ValueError("Frequency must be provided")
        normalized = frequency.lower()
        if normalized not in allowed_frequencies:
            raise ValueError("Frequency must be one of immediate, daily, weekly")
        return normalized

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'email': self.email,
            'frequency': self.frequency,
            'isActive': self.is_active,
            'gameId': self.game_id
        }

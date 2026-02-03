from typing import Any
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class StretchGoal(BaseModel):
    __tablename__ = 'stretch_goals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Type of goal: 'pledge_total' for funding amount or 'pledge_count' for number of backers
    goal_type = db.Column(db.String(20), nullable=False)

    # Target amount (in dollars for pledge_total, or number of pledges for pledge_count)
    target_amount = db.Column(db.Integer, nullable=False)

    # Current amount achieved
    current_amount = db.Column(db.Integer, nullable=False, default=0)

    # Foreign key to game
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    # Relationship to game
    game = relationship("Game", back_populates="stretch_goals")

    @validates('title')
    def validate_title(self, key, title):
        return self.validate_string_length('Stretch goal title', title, min_length=2)

    @validates('description')
    def validate_description(self, key, description):
        return self.validate_string_length('Description', description, min_length=10)

    @validates('goal_type')
    def validate_goal_type(self, key, goal_type):
        valid_types = ['pledge_total', 'pledge_count']
        if goal_type not in valid_types:
            raise ValueError(f"Goal type must be one of: {', '.join(valid_types)}")
        return goal_type

    @validates('target_amount')
    def validate_target_amount(self, key, target_amount):
        if target_amount <= 0:
            raise ValueError("Target amount must be greater than 0")
        return target_amount

    @validates('current_amount')
    def validate_current_amount(self, key, current_amount):
        if current_amount < 0:
            raise ValueError("Current amount cannot be negative")
        return current_amount

    def __repr__(self) -> str:
        return f'<StretchGoal {self.title}, Game ID: {self.game_id}>'

    def to_dict(self) -> dict[str, Any]:
        progress_percentage = (self.current_amount / self.target_amount * 100) if self.target_amount > 0 else 0

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'goalType': self.goal_type,
            'targetAmount': self.target_amount,
            'currentAmount': self.current_amount,
            'progressPercentage': round(progress_percentage, 1),
            'isAchieved': self.current_amount >= self.target_amount,
            'gameId': self.game_id
        }

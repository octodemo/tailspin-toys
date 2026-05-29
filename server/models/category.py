from typing import Any, List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from . import db
from .base import BaseModel

if TYPE_CHECKING:
    from .game import Game

class Category(BaseModel):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # One-to-many relationship: one category has many games
    games: Mapped[List["Game"]] = relationship(back_populates="category")
    
    @validates('name')
    def validate_name(self, key, name):
        return self.validate_string_length('Category name', name, min_length=2)
        
    @validates('description')
    def validate_description(self, key, description):
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)
    
    def __repr__(self) -> str:
        return f'<Category {self.name}>'
        
    def to_dict(self) -> dict[str, Any]:
        from .game import Game
        count_stmt = select(func.count(Game.id)).where(Game.category_id == self.id)
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': db.session.scalar(count_stmt) or 0
        }
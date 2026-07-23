from typing import Any, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from .base import BaseModel

if TYPE_CHECKING:
    from .category import Category
    from .publisher import Publisher

class Game(BaseModel):
    __tablename__ = 'games'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    star_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Archived games are hidden from the public catalog but remain restorable
    is_archived: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default='0'
    )

    # Foreign keys for one-to-many relationships
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    publisher_id: Mapped[int] = mapped_column(ForeignKey('publishers.id'), nullable=False)

    # One-to-many relationships (many games belong to one category/publisher)
    category: Mapped["Category"] = relationship(back_populates="games")
    publisher: Mapped["Publisher"] = relationship(back_populates="games")
    
    @validates('title')
    def validate_name(self, key, name):
        return self.validate_string_length('Game title', name, min_length=2)
    
    @validates('description')
    def validate_description(self, key, description):
        return self.validate_string_length('Description', description, min_length=10)

    @validates('star_rating')
    def validate_star_rating(self, key: str, star_rating: Any) -> Optional[float]:
        if star_rating is None:
            return None

        if isinstance(star_rating, bool) or not isinstance(star_rating, (int, float)):
            raise ValueError('Star rating must be a number between 0 and 5')

        if not 0 <= star_rating <= 5:
            raise ValueError('Star rating must be between 0 and 5')

        return float(star_rating)

    def __repr__(self) -> str:
        return f'<Game {self.title}, ID: {self.id}>'

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'publisher': {'id': self.publisher.id, 'name': self.publisher.name} if self.publisher else None,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'starRating': self.star_rating,  # Changed from star_rating to starRating
            'isArchived': self.is_archived,
        }
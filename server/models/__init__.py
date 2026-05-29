from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base for all models."""
    pass

db = SQLAlchemy(model_class=Base)

# Import models after db is defined to avoid circular imports
from .category import Category
from .game import Game
from .publisher import Publisher
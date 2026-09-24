import unittest
from typing import Dict, Any
from flask import Flask
from models import Game, Publisher, Category, db

class TestModels(unittest.TestCase):
    """Test suite for model validations"""
    
    # Test data
    TEST_DATA: Dict[str, Any] = {
        "valid_publisher": {"name": "Test Publisher", "description": "A great publisher for testing"},
        "valid_category": {"name": "Strategy", "description": "Strategic games for testing"},
        "valid_game": {
            "title": "Test Game",
            "description": "An exciting test game with lots of features",
            "star_rating": 4.5
        }
    }

    def setUp(self) -> None:
        """Set up test database"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize in-memory database for testing
        db.init_app(self.app)
        
        # Create tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_game_title_too_short(self) -> None:
        """Test that game title validation rejects titles that are too short"""
        with self.app.app_context():
            # Create required publisher and category
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()
            
            # Attempt to create game with title that's too short
            with self.assertRaises(ValueError) as context:
                game = Game(
                    title="X",  # Only 1 character
                    description=self.TEST_DATA["valid_game"]["description"],
                    publisher=publisher,
                    category=category,
                    star_rating=4.0
                )
                db.session.add(game)
                db.session.commit()
            
            self.assertIn("Game title must be at least 2 characters", str(context.exception))

    def test_game_description_too_short(self) -> None:
        """Test that game description validation rejects descriptions that are too short"""
        with self.app.app_context():
            # Create required publisher and category
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()
            
            # Attempt to create game with description that's too short
            with self.assertRaises(ValueError) as context:
                game = Game(
                    title=self.TEST_DATA["valid_game"]["title"],
                    description="Too short",  # Only 9 characters
                    publisher=publisher,
                    category=category,
                    star_rating=4.0
                )
                db.session.add(game)
                db.session.commit()
            
            self.assertIn("Description must be at least 10 characters", str(context.exception))

    def test_valid_game_creation(self) -> None:
        """Test that a valid game can be created successfully"""
        with self.app.app_context():
            # Create required publisher and category
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()
            
            # Create valid game
            game = Game(
                title=self.TEST_DATA["valid_game"]["title"],
                description=self.TEST_DATA["valid_game"]["description"],
                publisher=publisher,
                category=category,
                star_rating=self.TEST_DATA["valid_game"]["star_rating"]
            )
            db.session.add(game)
            db.session.commit()
            
            # Verify game was created
            self.assertIsNotNone(game.id)
            self.assertEqual(game.title, self.TEST_DATA["valid_game"]["title"])
            self.assertEqual(game.description, self.TEST_DATA["valid_game"]["description"])
            self.assertEqual(game.star_rating, self.TEST_DATA["valid_game"]["star_rating"])

    def _create_publisher_and_category(self) -> tuple[Publisher, Category]:
        """Create the publisher and category a game requires."""
        publisher = Publisher(**self.TEST_DATA["valid_publisher"])
        category = Category(**self.TEST_DATA["valid_category"])
        db.session.add_all([publisher, category])
        db.session.commit()

        return publisher, category

    def _create_valid_game(self, **overrides: Any) -> Game:
        """Create and persist a valid game, applying any field overrides."""
        publisher, category = self._create_publisher_and_category()

        fields: Dict[str, Any] = {
            "title": self.TEST_DATA["valid_game"]["title"],
            "description": self.TEST_DATA["valid_game"]["description"],
            "star_rating": self.TEST_DATA["valid_game"]["star_rating"],
        }
        fields.update(overrides)

        game = Game(**fields, publisher=publisher, category=category)
        db.session.add(game)
        db.session.commit()

        return game

    def test_game_is_not_archived_by_default(self) -> None:
        """A newly created game should be live rather than archived"""
        with self.app.app_context():
            game = self._create_valid_game()

            self.assertFalse(game.is_archived)

    def test_game_can_be_archived(self) -> None:
        """Setting the archived flag should persist"""
        with self.app.app_context():
            game = self._create_valid_game()

            game.is_archived = True
            db.session.commit()

            self.assertTrue(db.session.get(Game, game.id).is_archived)

    def test_game_to_dict_exposes_is_archived(self) -> None:
        """The serialized game should expose the archived state as camelCase"""
        with self.app.app_context():
            game = self._create_valid_game()

            self.assertIn('isArchived', game.to_dict())
            self.assertFalse(game.to_dict()['isArchived'])

    def test_game_star_rating_above_maximum_rejected(self) -> None:
        """A star rating above 5 should be rejected"""
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                self._create_valid_game(star_rating=5.5)

            self.assertIn("Star rating must be between 0 and 5", str(context.exception))

    def test_game_star_rating_below_minimum_rejected(self) -> None:
        """A negative star rating should be rejected"""
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                self._create_valid_game(star_rating=-1)

            self.assertIn("Star rating must be between 0 and 5", str(context.exception))

    def test_game_star_rating_non_numeric_rejected(self) -> None:
        """A non-numeric star rating should be rejected"""
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                self._create_valid_game(star_rating="excellent")

            self.assertIn("Star rating must be a number", str(context.exception))

    def test_game_star_rating_boundaries_allowed(self) -> None:
        """The 0 and 5 boundary values should both be accepted"""
        with self.app.app_context():
            publisher, category = self._create_publisher_and_category()

            for rating in (0, 5):
                game = Game(
                    title=f"Boundary {rating}",
                    description=self.TEST_DATA["valid_game"]["description"],
                    publisher=publisher,
                    category=category,
                    star_rating=rating,
                )
                db.session.add(game)
                db.session.commit()

                self.assertEqual(game.star_rating, float(rating))

    def test_game_star_rating_optional(self) -> None:
        """A game without a star rating should still be valid"""
        with self.app.app_context():
            game = self._create_valid_game(star_rating=None)

            self.assertIsNone(game.star_rating)

    def test_publisher_name_too_short(self) -> None:
        """Test that publisher name validation rejects names that are too short"""
        with self.app.app_context():
            # Attempt to create publisher with name that's too short
            with self.assertRaises(ValueError) as context:
                publisher = Publisher(name="X", description=self.TEST_DATA["valid_publisher"]["description"])
                db.session.add(publisher)
                db.session.commit()
            
            self.assertIn("Publisher name must be at least 2 characters", str(context.exception))

    def test_category_name_too_short(self) -> None:
        """Test that category name validation rejects names that are too short"""
        with self.app.app_context():
            # Attempt to create category with name that's too short
            with self.assertRaises(ValueError) as context:
                category = Category(name="X", description=self.TEST_DATA["valid_category"]["description"])
                db.session.add(category)
                db.session.commit()
            
            self.assertIn("Category name must be at least 2 characters", str(context.exception))

    def test_description_none_allowed(self) -> None:
        """Test that None descriptions are allowed for optional fields"""
        with self.app.app_context():
            # Create publisher without description
            publisher = Publisher(name=self.TEST_DATA["valid_publisher"]["name"], description=None)
            db.session.add(publisher)
            db.session.commit()
            
            # Verify publisher was created with None description
            self.assertIsNotNone(publisher.id)
            self.assertIsNone(publisher.description)

    def test_publisher_description_too_short(self) -> None:
        """Test that publisher description validation rejects descriptions that are too short"""
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                publisher = Publisher(name="Valid Name", description="Too short")
                db.session.add(publisher)
                db.session.commit()
            
            self.assertIn("Description must be at least 10 characters", str(context.exception))

    def test_category_description_too_short(self) -> None:
        """Test that category description validation rejects descriptions that are too short"""
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                category = Category(name="Valid Name", description="Too short")
                db.session.add(category)
                db.session.commit()
            
            self.assertIn("Description must be at least 10 characters", str(context.exception))

    def test_category_description_none_allowed(self) -> None:
        """Test that None descriptions are allowed for categories"""
        with self.app.app_context():
            category = Category(name="Test Category", description=None)
            db.session.add(category)
            db.session.commit()
            
            self.assertIsNotNone(category.id)
            self.assertIsNone(category.description)

    def test_game_description_none_rejected(self) -> None:
        """Test that game description validation rejects None since column is not nullable"""
        with self.app.app_context():
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()
            
            with self.assertRaises(ValueError) as context:
                game = Game(
                    title=self.TEST_DATA["valid_game"]["title"],
                    description=None,
                    publisher=publisher,
                    category=category,
                    star_rating=4.0
                )
                db.session.add(game)
                db.session.commit()
            
            self.assertIn("Description cannot be empty", str(context.exception))

    def test_publisher_to_dict_includes_game_count(self) -> None:
        """Publisher.to_dict() should report the count of related games."""
        with self.app.app_context():
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()

            # No games yet — count should be 0
            self.assertEqual(publisher.to_dict()["game_count"], 0)

            # Add two games to this publisher
            for i in range(2):
                db.session.add(Game(
                    title=f"Game {i}",
                    description="A long enough description for tests",
                    publisher=publisher,
                    category=category,
                    star_rating=4.0,
                ))
            db.session.commit()

            self.assertEqual(publisher.to_dict()["game_count"], 2)

    def test_category_to_dict_includes_game_count(self) -> None:
        """Category.to_dict() should report the count of related games."""
        with self.app.app_context():
            publisher = Publisher(**self.TEST_DATA["valid_publisher"])
            category = Category(**self.TEST_DATA["valid_category"])
            db.session.add_all([publisher, category])
            db.session.commit()

            self.assertEqual(category.to_dict()["game_count"], 0)

            db.session.add(Game(
                title="Lone Game",
                description="A long enough description for tests",
                publisher=publisher,
                category=category,
                star_rating=4.0,
            ))
            db.session.commit()

            self.assertEqual(category.to_dict()["game_count"], 1)

if __name__ == '__main__':
    unittest.main()

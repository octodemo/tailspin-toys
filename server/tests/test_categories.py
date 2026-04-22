import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.categories import categories_bp

class TestCategoriesRoutes(unittest.TestCase):
    """Test suite for categories API endpoints"""

    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
        ],
        "categories": [
            {"name": "Strategy", "description": "Strategic thinking games"},
            {"name": "Action", "description": "Fast-paced action games"},
            {"name": "Puzzle", "description": "Brain teaser puzzle games"},
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5,
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.2,
            },
            {
                "title": "Code Combat",
                "description": "Battle your way through coding challenges and bugs",
                "publisher_index": 0,
                "category_index": 1,
                "star_rating": 3.8,
            },
        ],
    }

    CATEGORIES_API_PATH: str = '/api/categories'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.app.register_blueprint(categories_bp)
        self.client = self.app.test_client()
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        publishers = [Publisher(**p) for p in self.TEST_DATA["publishers"]]
        db.session.add_all(publishers)

        categories = [Category(**c) for c in self.TEST_DATA["categories"]]
        db.session.add_all(categories)
        db.session.commit()

        for game_data in self.TEST_DATA["games"]:
            gd = game_data.copy()
            pub_idx = gd.pop("publisher_index")
            cat_idx = gd.pop("category_index")
            db.session.add(Game(**gd, publisher=publishers[pub_idx], category=categories[cat_idx]))
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_categories_success(self) -> None:
        """Test successful retrieval of all categories sorted by name"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        # Sorted alphabetically
        names = [c['name'] for c in data]
        self.assertEqual(names, ['Action', 'Puzzle', 'Strategy'])

    def test_get_categories_structure(self) -> None:
        """Test response structure has required fields"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        for category in data:
            self.assertIn('id', category)
            self.assertIn('name', category)
            self.assertIn('description', category)
            self.assertIn('gameCount', category)
            self.assertIsInstance(category['id'], int)
            self.assertIsInstance(category['gameCount'], int)

    def test_get_categories_game_count(self) -> None:
        """Test gameCount is correct for each category"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)
        counts = {c['name']: c['gameCount'] for c in data}

        self.assertEqual(counts['Strategy'], 2)
        self.assertEqual(counts['Action'], 1)
        self.assertEqual(counts['Puzzle'], 0)

    def test_get_categories_empty_database(self) -> None:
        """Test retrieval when no categories exist"""
        with self.app.app_context():
            db.session.query(Game).delete()
            db.session.query(Category).delete()
            db.session.commit()

        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)


if __name__ == '__main__':
    unittest.main()

import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Category, Publisher, Game, db
from routes.categories import categories_bp


class TestCategoriesRoutes(unittest.TestCase):
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"},
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
                "category_index": 1,
                "star_rating": 4.2,
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

        games = []
        for game_data in self.TEST_DATA["games"]:
            gd = game_data.copy()
            pub_idx = gd.pop("publisher_index")
            cat_idx = gd.pop("category_index")
            games.append(Game(**gd, publisher=publishers[pub_idx], category=categories[cat_idx]))
        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper to parse response JSON"""
        return json.loads(response.data)

    def test_get_categories_success(self) -> None:
        """Test successful retrieval of all categories"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["categories"]))

    def test_get_categories_sorted_by_name(self) -> None:
        """Test that categories are returned in alphabetical order"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        names = [c['name'] for c in data]
        self.assertEqual(names, sorted(names))

    def test_get_categories_structure(self) -> None:
        """Test the response structure for categories"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        required_fields = ['id', 'name', 'description', 'game_count']
        for category in data:
            for field in required_fields:
                self.assertIn(field, category)

    def test_get_categories_game_count(self) -> None:
        """Test that game_count reflects games assigned to each category"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        total_games = sum(c['game_count'] for c in data)
        self.assertEqual(total_games, len(self.TEST_DATA["games"]))

    def test_get_categories_empty_database(self) -> None:
        """Test retrieval when no categories exist"""
        from sqlalchemy import delete
        with self.app.app_context():
            db.session.execute(delete(Game))
            db.session.execute(delete(Category))
            db.session.commit()

        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])


if __name__ == '__main__':
    unittest.main()

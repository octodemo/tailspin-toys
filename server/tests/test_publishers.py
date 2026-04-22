import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.publishers import publishers_bp

class TestPublishersRoutes(unittest.TestCase):
    """Test suite for publishers API endpoints"""

    TEST_DATA: Dict[str, Any] = {
        "categories": [
            {"name": "Strategy"},
        ],
        "publishers": [
            {"name": "CodeForge Studios", "description": "Innovative game development studio"},
            {"name": "DevMasters Inc", "description": "Masters of developer entertainment"},
            {"name": "GitHub Games", "description": "Open source gaming experiences"},
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
                "publisher_index": 1,
                "category_index": 0,
                "star_rating": 3.8,
            },
        ],
    }

    PUBLISHERS_API_PATH: str = '/api/publishers'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.app.register_blueprint(publishers_bp)
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
        categories = [Category(**c) for c in self.TEST_DATA["categories"]]
        db.session.add_all(categories)

        publishers = [Publisher(**p) for p in self.TEST_DATA["publishers"]]
        db.session.add_all(publishers)
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

    def test_get_publishers_success(self) -> None:
        """Test successful retrieval of all publishers sorted by name"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        names = [p['name'] for p in data]
        self.assertEqual(names, ['CodeForge Studios', 'DevMasters Inc', 'GitHub Games'])

    def test_get_publishers_structure(self) -> None:
        """Test response structure has required fields"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        for publisher in data:
            self.assertIn('id', publisher)
            self.assertIn('name', publisher)
            self.assertIn('description', publisher)
            self.assertIn('gameCount', publisher)
            self.assertIsInstance(publisher['id'], int)
            self.assertIsInstance(publisher['gameCount'], int)

    def test_get_publishers_game_count(self) -> None:
        """Test gameCount is correct for each publisher"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)
        counts = {p['name']: p['gameCount'] for p in data}

        self.assertEqual(counts['CodeForge Studios'], 2)
        self.assertEqual(counts['DevMasters Inc'], 1)
        self.assertEqual(counts['GitHub Games'], 0)

    def test_get_publishers_empty_database(self) -> None:
        """Test retrieval when no publishers exist"""
        with self.app.app_context():
            db.session.query(Game).delete()
            db.session.query(Publisher).delete()
            db.session.commit()

        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)


if __name__ == '__main__':
    unittest.main()

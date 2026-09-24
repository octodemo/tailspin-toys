import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from sqlalchemy import select
from models import Game, Publisher, Category, db
from routes.categories import categories_bp
from routes.publishers import publishers_bp


class TestLookupRoutes(unittest.TestCase):
    """Tests for the publisher and category lookup endpoints used by admin forms."""

    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "Ops Interactive", "description": "Publisher used for lookup tests"},
            {"name": "DevGames Inc", "description": "Another publisher for lookup tests"},
        ],
        "categories": [
            {"name": "Strategy", "description": "Strategic games used for lookup tests"},
            {"name": "Card Game", "description": "Card games used for lookup tests"},
        ],
        "game": {
            "title": "Pipeline Panic",
            "description": "Build your DevOps pipeline before chaos ensues",
            "star_rating": 4.5,
        },
    }

    PUBLISHERS_API_PATH: str = '/api/publishers'
    CATEGORIES_API_PATH: str = '/api/categories'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.app.register_blueprint(publishers_bp)
        self.app.register_blueprint(categories_bp)

        self.client = self.app.test_client()

        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Seed publishers and categories, attaching one game to the first of each."""
        publishers = [Publisher(**data) for data in self.TEST_DATA["publishers"]]
        categories = [Category(**data) for data in self.TEST_DATA["categories"]]
        db.session.add_all(publishers + categories)
        db.session.commit()

        game = Game(
            **self.TEST_DATA["game"],
            publisher=publishers[0],
            category=categories[0],
        )
        db.session.add(game)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_publishers_success(self) -> None:
        """All publishers should be returned under a publishers key."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn('publishers', data)
        self.assertEqual(len(data['publishers']), len(self.TEST_DATA["publishers"]))

    def test_get_publishers_sorted_by_name(self) -> None:
        """Publishers should be alphabetised so dropdowns are predictable."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        names = [publisher['name'] for publisher in self._get_response_data(response)['publishers']]

        self.assertEqual(names, sorted(names))

    def test_get_publishers_structure(self) -> None:
        """Each publisher should expose the fields the admin form relies on."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        publisher = self._get_response_data(response)['publishers'][0]

        for field in ('id', 'name', 'description', 'game_count'):
            self.assertIn(field, publisher)

    def test_get_publishers_includes_game_count(self) -> None:
        """The publisher with a game should report a non-zero count."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        publishers = {p['name']: p for p in self._get_response_data(response)['publishers']}

        self.assertEqual(publishers['Ops Interactive']['game_count'], 1)
        self.assertEqual(publishers['DevGames Inc']['game_count'], 0)

    def test_publisher_game_count_excludes_archived_games(self) -> None:
        """Archived games should not be counted, so counts match the public catalog."""
        with self.app.app_context():
            game = db.session.scalars(select(Game)).one()
            game.is_archived = True
            db.session.commit()

        response = self.client.get(self.PUBLISHERS_API_PATH)
        publishers = {p['name']: p for p in self._get_response_data(response)['publishers']}

        self.assertEqual(publishers['Ops Interactive']['game_count'], 0)

    def test_category_game_count_excludes_archived_games(self) -> None:
        """Archived games should not be counted, so counts match the public catalog."""
        with self.app.app_context():
            game = db.session.scalars(select(Game)).one()
            game.is_archived = True
            db.session.commit()

        response = self.client.get(self.CATEGORIES_API_PATH)
        categories = {c['name']: c for c in self._get_response_data(response)['categories']}

        self.assertEqual(categories['Strategy']['game_count'], 0)

    def test_get_categories_success(self) -> None:
        """All categories should be returned under a categories key."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', data)
        self.assertEqual(len(data['categories']), len(self.TEST_DATA["categories"]))

    def test_get_categories_sorted_by_name(self) -> None:
        """Categories should be alphabetised so dropdowns are predictable."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        names = [category['name'] for category in self._get_response_data(response)['categories']]

        self.assertEqual(names, sorted(names))

    def test_get_categories_structure(self) -> None:
        """Each category should expose the fields the admin form relies on."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        category = self._get_response_data(response)['categories'][0]

        for field in ('id', 'name', 'description', 'game_count'):
            self.assertIn(field, category)

    def test_get_publishers_empty_database(self) -> None:
        """An empty table should return an empty list rather than an error."""
        from sqlalchemy import delete

        with self.app.app_context():
            db.session.execute(delete(Game))
            db.session.execute(delete(Publisher))
            db.session.commit()

        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['publishers'], [])

    def test_get_categories_empty_database(self) -> None:
        """An empty table should return an empty list rather than an error."""
        from sqlalchemy import delete

        with self.app.app_context():
            db.session.execute(delete(Game))
            db.session.execute(delete(Category))
            db.session.commit()

        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['categories'], [])


if __name__ == '__main__':
    unittest.main()

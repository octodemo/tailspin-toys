import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.categories import categories_bp


class TestCategoriesRoutes(unittest.TestCase):
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc", "description": "A publisher of developer-themed strategy games."},
            {"name": "Scrum Masters", "description": "Card games for agile teams and other knowledge workers."}
        ],
        "categories": [
            {"name": "Strategy", "description": "Strategy games for thoughtful planners."},
            {"name": "Card Game", "description": "Card-driven games for groups of any size."}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 1,
                "category_index": 1,
                "star_rating": 4.2
            },
            {
                "title": "Refactor Rampage",
                "description": "Untangle legacy code before the deadline",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.0
            }
        ]
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
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)

        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)

        db.session.commit()

        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")

            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))

        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def _get_category_id_by_name(self, name: str) -> int:
        with self.app.app_context():
            category = db.session.query(Category).filter_by(name=name).first()
            return category.id

    def test_get_categories_success(self) -> None:
        """Test successful retrieval of all categories"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', data)
        self.assertIsInstance(data['categories'], list)
        self.assertEqual(len(data['categories']), len(self.TEST_DATA["categories"]))

    def test_get_categories_alphabetical_order(self) -> None:
        """Test that categories are returned in alphabetical order by name"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        names = [c['name'] for c in data['categories']]
        self.assertEqual(names, sorted(names))

    def test_get_categories_structure(self) -> None:
        """Test the structure of each category in the list response"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        required_fields = ['id', 'name', 'description', 'game_count']
        for category in data['categories']:
            for field in required_fields:
                self.assertIn(field, category)

    def test_get_categories_includes_game_count(self) -> None:
        """Test that the list response includes an accurate game_count per category"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        counts_by_name = {c['name']: c['game_count'] for c in data['categories']}
        self.assertEqual(counts_by_name["Strategy"], 2)
        self.assertEqual(counts_by_name["Card Game"], 1)

    def test_get_category_by_id_success(self) -> None:
        """Test retrieving a single category by id with nested games"""
        category_id = self._get_category_id_by_name("Strategy")

        response = self.client.get(f'{self.CATEGORIES_API_PATH}/{category_id}')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], category_id)
        self.assertEqual(data['name'], "Strategy")
        self.assertIn('description', data)
        self.assertIn('games', data)

    def test_get_category_by_id_nested_games(self) -> None:
        """Test that the detail response includes the category's games"""
        category_id = self._get_category_id_by_name("Strategy")

        response = self.client.get(f'{self.CATEGORIES_API_PATH}/{category_id}')
        data = self._get_response_data(response)

        titles = sorted(game['title'] for game in data['games'])
        self.assertEqual(titles, ['Pipeline Panic', 'Refactor Rampage'])
        for game in data['games']:
            self.assertIn('id', game)
            self.assertIn('title', game)

    def test_get_category_by_id_no_games(self) -> None:
        """Test that a category with no games returns an empty games list"""
        with self.app.app_context():
            empty_category = Category(
                name="Word Game",
                description="Category for word-based puzzle games.",
            )
            db.session.add(empty_category)
            db.session.commit()
            empty_id = empty_category.id

        response = self.client.get(f'{self.CATEGORIES_API_PATH}/{empty_id}')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['games'], [])

    def test_get_category_by_id_not_found(self) -> None:
        """Test that an unknown category id returns 404"""
        response = self.client.get(f'{self.CATEGORIES_API_PATH}/99999')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

    def test_get_category_by_invalid_id(self) -> None:
        """Test that a non-integer id returns 404"""
        response = self.client.get(f'{self.CATEGORIES_API_PATH}/invalid-id')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()

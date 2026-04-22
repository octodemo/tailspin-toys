import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.games import games_bp

class TestGamesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"}
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
            }
        ]
    }
    
    # API paths
    GAMES_API_PATH: str = '/api/games'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the games blueprint
        self.app.register_blueprint(games_bp)
        
        # Initialize the test client
        self.client = self.app.test_client()
        
        # Initialize in-memory database for testing
        db.init_app(self.app)
        
        # Create tables and seed data
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
        # Create test publishers
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create test games
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

    def _get_games_list(self, response: Response) -> list[dict]:
        """Helper to extract games list from paginated response"""
        return self._get_response_data(response)['games']

    def test_get_games_success(self) -> None:
        """Test successful retrieval of multiple games"""
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_games_list(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(games), len(self.TEST_DATA["games"]))
        
        # Games are returned in alphabetical order by title
        games_by_title = {g['title']: g for g in games}
        for test_game in self.TEST_DATA["games"]:
            game_data = games_by_title[test_game["title"]]
            test_publisher = self.TEST_DATA["publishers"][test_game["publisher_index"]]
            test_category = self.TEST_DATA["categories"][test_game["category_index"]]
            
            self.assertEqual(game_data['publisher']['name'], test_publisher["name"])
            self.assertEqual(game_data['category']['name'], test_category["name"])
            self.assertEqual(game_data['starRating'], test_game["star_rating"])

    def test_get_games_structure(self) -> None:
        """Test the paginated response structure for games"""
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('games', data)
        self.assertIn('pagination', data)
        self.assertIsInstance(data['games'], list)
        self.assertEqual(len(data['games']), len(self.TEST_DATA["games"]))
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'starRating']
        for game in data['games']:
            for field in required_fields:
                self.assertIn(field, game)

    def test_get_games_pagination_metadata(self) -> None:
        """Test pagination metadata in response"""
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        pagination = data['pagination']

        self.assertEqual(pagination['page'], 1)
        self.assertEqual(pagination['pageSize'], 9)
        self.assertEqual(pagination['total'], 2)
        self.assertEqual(pagination['totalPages'], 1)

    def test_get_games_custom_page_size(self) -> None:
        """Test requesting a specific page size"""
        response = self.client.get(f'{self.GAMES_API_PATH}?pageSize=1')
        data = self._get_response_data(response)

        self.assertEqual(len(data['games']), 1)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['pageSize'], 1)
        self.assertEqual(data['pagination']['total'], 2)
        self.assertEqual(data['pagination']['totalPages'], 2)

    def test_get_games_second_page(self) -> None:
        """Test retrieving the second page of results"""
        response = self.client.get(f'{self.GAMES_API_PATH}?pageSize=1&page=2')
        data = self._get_response_data(response)

        self.assertEqual(len(data['games']), 1)
        self.assertEqual(data['pagination']['page'], 2)
        self.assertEqual(data['games'][0]['title'], 'Pipeline Panic')

    def test_get_games_page_beyond_results(self) -> None:
        """Test requesting a page beyond available results returns empty games"""
        response = self.client.get(f'{self.GAMES_API_PATH}?page=99')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['games']), 0)
        self.assertEqual(data['pagination']['page'], 99)
        self.assertEqual(data['pagination']['total'], 2)

    def test_get_games_page_size_clamped(self) -> None:
        """Test that page size is clamped to valid range"""
        response = self.client.get(f'{self.GAMES_API_PATH}?pageSize=200')
        data = self._get_response_data(response)

        self.assertEqual(data['pagination']['pageSize'], 100)

    def test_get_games_negative_page_defaults_to_one(self) -> None:
        """Test that negative page number is clamped to 1"""
        response = self.client.get(f'{self.GAMES_API_PATH}?page=-5')
        data = self._get_response_data(response)

        self.assertEqual(data['pagination']['page'], 1)

    def test_get_game_by_id_success(self) -> None:
        """Test successful retrieval of a single game by ID"""
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_games_list(response)
        game_id = games[0]['id']
        game_title = games[0]['title']
        
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], game_title)
        self.assertIn('publisher', data)
        self.assertIn('description', data)
        
    def test_get_game_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent game by ID"""
        response = self.client.get(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_get_games_empty_database(self) -> None:
        """Test retrieval of games when database is empty"""
        with self.app.app_context():
            db.session.query(Game).delete()
            db.session.commit()
        
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['games']), 0)
        self.assertEqual(data['pagination']['total'], 0)
        self.assertEqual(data['pagination']['totalPages'], 1)

    def test_get_game_by_invalid_id_type(self) -> None:
        """Test retrieval of a game with invalid ID type"""
        response = self.client.get(f'{self.GAMES_API_PATH}/invalid-id')
        self.assertEqual(response.status_code, 404)

    # --- Filter tests ---

    def test_filter_by_category(self) -> None:
        """Test filtering games by category ID"""
        # Get category ID for 'Strategy' (index 0)
        with self.app.app_context():
            category = Category.query.filter_by(name='Strategy').first()
            category_id = category.id

        response = self.client.get(f'{self.GAMES_API_PATH}?category={category_id}')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['games']), 1)
        self.assertEqual(data['games'][0]['title'], 'Pipeline Panic')
        self.assertEqual(data['pagination']['total'], 1)

    def test_filter_by_publisher(self) -> None:
        """Test filtering games by publisher ID"""
        with self.app.app_context():
            publisher = Publisher.query.filter_by(name='DevGames Inc').first()
            publisher_id = publisher.id

        response = self.client.get(f'{self.GAMES_API_PATH}?publisher={publisher_id}')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['games']), 1)
        self.assertEqual(data['games'][0]['title'], 'Pipeline Panic')
        self.assertEqual(data['pagination']['total'], 1)

    def test_filter_by_category_and_publisher(self) -> None:
        """Test filtering games by both category and publisher"""
        with self.app.app_context():
            category = Category.query.filter_by(name='Strategy').first()
            publisher = Publisher.query.filter_by(name='DevGames Inc').first()
            category_id = category.id
            publisher_id = publisher.id

        response = self.client.get(
            f'{self.GAMES_API_PATH}?category={category_id}&publisher={publisher_id}'
        )
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['games']), 1)
        self.assertEqual(data['games'][0]['title'], 'Pipeline Panic')

    def test_filter_nonexistent_category_returns_empty(self) -> None:
        """Test that filtering by a nonexistent category ID returns empty results"""
        response = self.client.get(f'{self.GAMES_API_PATH}?category=9999')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['games']), 0)
        self.assertEqual(data['pagination']['total'], 0)

    def test_filter_nonexistent_publisher_returns_empty(self) -> None:
        """Test that filtering by a nonexistent publisher ID returns empty results"""
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher=9999')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['games']), 0)
        self.assertEqual(data['pagination']['total'], 0)

    def test_filter_invalid_category_returns_400(self) -> None:
        """Test that a malformed category param returns 400"""
        response = self.client.get(f'{self.GAMES_API_PATH}?category=abc')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_filter_invalid_publisher_returns_400(self) -> None:
        """Test that a malformed publisher param returns 400"""
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher=xyz')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_filter_pagination_metadata(self) -> None:
        """Test that pagination metadata reflects filtered results"""
        with self.app.app_context():
            category = Category.query.filter_by(name='Strategy').first()
            category_id = category.id

        response = self.client.get(f'{self.GAMES_API_PATH}?category={category_id}&pageSize=1')
        data = self._get_response_data(response)

        self.assertEqual(data['pagination']['total'], 1)
        self.assertEqual(data['pagination']['totalPages'], 1)
        self.assertEqual(data['pagination']['pageSize'], 1)

if __name__ == '__main__':
    unittest.main()
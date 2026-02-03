import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, StretchGoal, db
from routes.stretch_goals import stretch_goals_bp
from routes.games import games_bp

class TestStretchGoalsRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"}
        ],
        "categories": [
            {"name": "Strategy"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            }
        ],
        "stretch_goals": [
            {
                "title": "Extra Game Modes",
                "description": "Unlock 3 additional game modes including hard difficulty",
                "goal_type": "pledge_total",
                "target_amount": 50000,
                "current_amount": 25000,
                "game_index": 0
            },
            {
                "title": "Multiplayer Support",
                "description": "Add online multiplayer for up to 4 players",
                "goal_type": "pledge_count",
                "target_amount": 500,
                "current_amount": 300,
                "game_index": 0
            }
        ]
    }

    # API paths
    STRETCH_GOALS_API_PATH: str = '/api/stretch-goals'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Register blueprints
        self.app.register_blueprint(games_bp)
        self.app.register_blueprint(stretch_goals_bp)

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

        # Create test stretch goals
        stretch_goals = []
        for goal_data in self.TEST_DATA["stretch_goals"]:
            goal_dict = goal_data.copy()
            game_index = goal_dict.pop("game_index")

            stretch_goals.append(StretchGoal(
                **goal_dict,
                game=games[game_index]
            ))

        db.session.add_all(stretch_goals)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def _get_first_game_id(self) -> int:
        """Helper to get first game ID"""
        with self.app.app_context():
            game = db.session.query(Game).first()
            return game.id if game else 1

    def test_get_stretch_goals_for_game_success(self) -> None:
        """Test successful retrieval of stretch goals for a game"""
        # Arrange
        game_id = self._get_first_game_id()

        # Act
        response = self.client.get(f'/api/games/{game_id}/stretch-goals')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["stretch_goals"]))

        # Verify first stretch goal
        first_goal = data[0]
        test_goal = self.TEST_DATA["stretch_goals"][0]
        self.assertEqual(first_goal['title'], test_goal["title"])
        self.assertEqual(first_goal['goalType'], test_goal["goal_type"])
        self.assertEqual(first_goal['targetAmount'], test_goal["target_amount"])
        self.assertEqual(first_goal['currentAmount'], test_goal["current_amount"])
        self.assertIn('progressPercentage', first_goal)
        self.assertIn('isAchieved', first_goal)

    def test_get_stretch_goals_structure(self) -> None:
        """Test the response structure for stretch goals"""
        # Arrange
        game_id = self._get_first_game_id()

        # Act
        response = self.client.get(f'/api/games/{game_id}/stretch-goals')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)

        required_fields = ['id', 'title', 'description', 'goalType', 'targetAmount',
                          'currentAmount', 'progressPercentage', 'isAchieved', 'gameId']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_stretch_goals_for_nonexistent_game(self) -> None:
        """Test retrieval of stretch goals for non-existent game"""
        # Act
        response = self.client.get('/api/games/999/stretch-goals')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_create_stretch_goal_success(self) -> None:
        """Test successful creation of a stretch goal"""
        # Arrange
        game_id = self._get_first_game_id()
        new_goal = {
            "title": "Expansion Pack",
            "description": "Add a new expansion pack with 20 new cards",
            "goalType": "pledge_total",
            "targetAmount": 75000,
            "currentAmount": 0
        }

        # Act
        response = self.client.post(
            f'/api/games/{game_id}/stretch-goals',
            data=json.dumps(new_goal),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['title'], new_goal['title'])
        self.assertEqual(data['targetAmount'], new_goal['targetAmount'])
        self.assertIn('id', data)

    def test_create_stretch_goal_missing_required_field(self) -> None:
        """Test creation with missing required field"""
        # Arrange
        game_id = self._get_first_game_id()
        incomplete_goal = {
            "title": "Test Goal",
            "description": "Test description"
            # Missing goalType and targetAmount
        }

        # Act
        response = self.client.post(
            f'/api/games/{game_id}/stretch-goals',
            data=json.dumps(incomplete_goal),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_create_stretch_goal_invalid_goal_type(self) -> None:
        """Test creation with invalid goal type"""
        # Arrange
        game_id = self._get_first_game_id()
        invalid_goal = {
            "title": "Test Goal",
            "description": "Test description for invalid goal type",
            "goalType": "invalid_type",
            "targetAmount": 10000
        }

        # Act
        response = self.client.post(
            f'/api/games/{game_id}/stretch-goals',
            data=json.dumps(invalid_goal),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_get_stretch_goal_by_id_success(self) -> None:
        """Test successful retrieval of a single stretch goal by ID"""
        # Arrange
        game_id = self._get_first_game_id()
        response = self.client.get(f'/api/games/{game_id}/stretch-goals')
        goals = self._get_response_data(response)
        goal_id = goals[0]['id']

        # Act
        response = self.client.get(f'{self.STRETCH_GOALS_API_PATH}/{goal_id}')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], goal_id)
        self.assertIn('title', data)

    def test_get_stretch_goal_by_id_not_found(self) -> None:
        """Test retrieval of non-existent stretch goal"""
        # Act
        response = self.client.get(f'{self.STRETCH_GOALS_API_PATH}/999')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Stretch goal not found")

    def test_update_stretch_goal_success(self) -> None:
        """Test successful update of a stretch goal"""
        # Arrange
        game_id = self._get_first_game_id()
        response = self.client.get(f'/api/games/{game_id}/stretch-goals')
        goals = self._get_response_data(response)
        goal_id = goals[0]['id']

        update_data = {
            "currentAmount": 30000,
            "title": "Updated Title"
        }

        # Act
        response = self.client.put(
            f'{self.STRETCH_GOALS_API_PATH}/{goal_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['currentAmount'], update_data['currentAmount'])
        self.assertEqual(data['title'], update_data['title'])

    def test_update_stretch_goal_not_found(self) -> None:
        """Test update of non-existent stretch goal"""
        # Arrange
        update_data = {"currentAmount": 5000}

        # Act
        response = self.client.put(
            f'{self.STRETCH_GOALS_API_PATH}/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Stretch goal not found")

    def test_delete_stretch_goal_success(self) -> None:
        """Test successful deletion of a stretch goal"""
        # Arrange
        game_id = self._get_first_game_id()
        response = self.client.get(f'/api/games/{game_id}/stretch-goals')
        goals = self._get_response_data(response)
        goal_id = goals[0]['id']

        # Act
        response = self.client.delete(f'{self.STRETCH_GOALS_API_PATH}/{goal_id}')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)

        # Verify it's deleted
        response = self.client.get(f'{self.STRETCH_GOALS_API_PATH}/{goal_id}')
        self.assertEqual(response.status_code, 404)

    def test_delete_stretch_goal_not_found(self) -> None:
        """Test deletion of non-existent stretch goal"""
        # Act
        response = self.client.delete(f'{self.STRETCH_GOALS_API_PATH}/999')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Stretch goal not found")

    def test_stretch_goals_empty_for_game(self) -> None:
        """Test retrieval when game has no stretch goals"""
        # Arrange - Create a new game without stretch goals
        with self.app.app_context():
            publisher = db.session.query(Publisher).first()
            category = db.session.query(Category).first()
            new_game = Game(
                title="New Game Without Goals",
                description="This game has no stretch goals yet",
                publisher=publisher,
                category=category,
                star_rating=4.0
            )
            db.session.add(new_game)
            db.session.commit()
            new_game_id = new_game.id

        # Act
        response = self.client.get(f'/api/games/{new_game_id}/stretch-goals')
        data = self._get_response_data(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()

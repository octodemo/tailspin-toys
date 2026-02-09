import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Publisher, Category, Game, db
from routes.publishers import publishers_bp


class TestPublishersRoutes(unittest.TestCase):
    """Test cases for the publishers API endpoints."""
    
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc", "description": "Leading developer game studio"},
            {"name": "Scrum Masters", "description": "Agile gaming company"},
            {"name": "Code Warriors", "description": "Epic coding adventures"}
        ]
    }
    
    PUBLISHERS_API_PATH: str = '/api/publishers'

    def setUp(self) -> None:
        """Set up test database and seed data."""
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
        """Clean up test database."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data."""
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data."""
        return json.loads(response.data)

    def test_get_publishers_success(self) -> None:
        """Test successful retrieval of all publishers."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["publishers"]))

    def test_get_publishers_ordered_by_name(self) -> None:
        """Test that publishers are returned ordered by name."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        names = [p['name'] for p in data]
        self.assertEqual(names, sorted(names))

    def test_get_publishers_structure(self) -> None:
        """Test the response structure for publishers (minimal for dropdowns)."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        
        # List endpoint returns minimal structure for dropdown performance
        required_fields = ['id', 'name']
        for field in required_fields:
            self.assertIn(field, data[0])
        # Verify description and game_count are NOT included (N+1 optimization)
        self.assertNotIn('description', data[0])
        self.assertNotIn('game_count', data[0])

    def test_get_publisher_by_id_success(self) -> None:
        """Test successful retrieval of a single publisher by ID."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        publishers = self._get_response_data(response)
        publisher_id = publishers[0]['id']
        
        response = self.client.get(f'{self.PUBLISHERS_API_PATH}/{publisher_id}')
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], publisher_id)
        self.assertIn('name', data)

    def test_get_publisher_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent publisher by ID."""
        response = self.client.get(f'{self.PUBLISHERS_API_PATH}/999')
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Publisher not found")

    def test_get_publishers_empty_database(self) -> None:
        """Test retrieval of publishers when database is empty."""
        with self.app.app_context():
            db.session.query(Publisher).delete()
            db.session.commit()
        
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)


if __name__ == '__main__':
    unittest.main()

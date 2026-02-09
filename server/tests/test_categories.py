import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Category, db
from routes.categories import categories_bp


class TestCategoriesRoutes(unittest.TestCase):
    """Test cases for the categories API endpoints."""
    
    TEST_DATA: Dict[str, Any] = {
        "categories": [
            {"name": "Strategy", "description": "Strategic thinking games"},
            {"name": "Card Game", "description": "Card-based gameplay"},
            {"name": "Puzzle", "description": "Brain teaser puzzles"}
        ]
    }
    
    CATEGORIES_API_PATH: str = '/api/categories'

    def setUp(self) -> None:
        """Set up test database and seed data."""
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
        """Clean up test database."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data."""
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data."""
        return json.loads(response.data)

    def test_get_categories_success(self) -> None:
        """Test successful retrieval of all categories."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["categories"]))

    def test_get_categories_ordered_by_name(self) -> None:
        """Test that categories are returned ordered by name."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        names = [c['name'] for c in data]
        self.assertEqual(names, sorted(names))

    def test_get_categories_structure(self) -> None:
        """Test the response structure for categories (minimal for dropdowns)."""
        response = self.client.get(self.CATEGORIES_API_PATH)
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

    def test_get_category_by_id_success(self) -> None:
        """Test successful retrieval of a single category by ID."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        categories = self._get_response_data(response)
        category_id = categories[0]['id']
        
        response = self.client.get(f'{self.CATEGORIES_API_PATH}/{category_id}')
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], category_id)
        self.assertIn('name', data)

    def test_get_category_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent category by ID."""
        response = self.client.get(f'{self.CATEGORIES_API_PATH}/999')
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Category not found")

    def test_get_categories_empty_database(self) -> None:
        """Test retrieval of categories when database is empty."""
        with self.app.app_context():
            db.session.query(Category).delete()
            db.session.commit()
        
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)


if __name__ == '__main__':
    unittest.main()

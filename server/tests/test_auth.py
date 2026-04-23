import unittest
from flask import Flask
from models import db
from routes.auth import auth_bp


class TestAuthRoutes(unittest.TestCase):
    """Test suite for authentication routes"""

    # API paths
    LOGIN_API_PATH: str = '/api/login'

    def setUp(self) -> None:
        """Set up test client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def tearDown(self) -> None:
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_login_default_redirect(self) -> None:
        """Test that login without next param redirects to home"""
        response = self.client.get(self.LOGIN_API_PATH)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

    def test_login_with_valid_relative_next(self) -> None:
        """Test that login with valid relative next param redirects correctly"""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=/games')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/games')

    def test_login_with_absolute_url_is_blocked(self) -> None:
        """Test that login with absolute URL in next param redirects to home (open redirect prevention)"""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=http://evil.com')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

    def test_login_with_https_url_is_blocked(self) -> None:
        """Test that login with HTTPS URL in next param redirects to home"""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=https://evil.com/steal')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

    def test_login_with_backslash_url_is_sanitized(self) -> None:
        """Test that backslashes are stripped from next param (e.g. input '\\\\evil.com' becomes 'evil.com').

        This prevents browsers that treat '\\' as '/' from turning '\\\\evil.com' into
        '//evil.com' (a protocol-relative URL with an external netloc). After stripping,
        'evil.com' is treated as a relative path and resolves safely within the app.
        """
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=\\\\evil.com')

        # After stripping backslashes, 'evil.com' is a relative path (no scheme, no netloc)
        # It is not an absolute URL; HTTP clients resolve it relative to the current request path
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'evil.com')

    def test_login_with_protocol_relative_url_is_blocked(self) -> None:
        """Test that protocol-relative next URLs (//evil.com) are blocked as they have a netloc"""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=//evil.com')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

    def test_login_with_empty_next_redirects_to_home(self) -> None:
        """Test that login with empty next param redirects to home"""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

    def test_login_with_nested_path(self) -> None:
        """Test that login with nested relative path next param redirects correctly"""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=/game/42')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/game/42')


if __name__ == '__main__':
    unittest.main()

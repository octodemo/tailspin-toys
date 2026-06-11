import unittest
from flask import Flask
from routes.auth import auth_bp


class TestAuthRoutes(unittest.TestCase):
    """Tests for the /api/login endpoint and its open-redirect protections."""

    LOGIN_API_PATH: str = '/api/login'

    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    def test_login_relative_path_redirects_to_next(self) -> None:
        """A relative `next` path should be honored as the redirect target."""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=/games')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/games'))

    def test_login_no_next_falls_back_to_home(self) -> None:
        """With no `next` query param, login should redirect to /."""
        response = self.client.get(self.LOGIN_API_PATH)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/'))

    def test_login_absolute_url_rejected(self) -> None:
        """An absolute URL with a scheme should be rejected (open-redirect guard)."""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=http://evil.com/path')

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.com', response.headers['Location'])
        self.assertTrue(response.headers['Location'].endswith('/'))

    def test_login_protocol_relative_url_rejected(self) -> None:
        """A protocol-relative URL (//host/path) should be rejected."""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=//evil.com/path')

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.com', response.headers['Location'])
        self.assertTrue(response.headers['Location'].endswith('/'))

    def test_login_backslash_normalized_before_validation(self) -> None:
        """Backslashes (which some browsers treat as path separators) should be
        stripped so they cannot smuggle in a protocol-relative redirect."""
        response = self.client.get(f'{self.LOGIN_API_PATH}?next=/\\\\evil.com/path')

        self.assertEqual(response.status_code, 302)
        # After backslash normalization the value becomes "/evil.com/path",
        # which is a relative path on our own host — the netloc check is not
        # bypassed.
        self.assertNotIn('\\', response.headers['Location'])


if __name__ == '__main__':
    unittest.main()

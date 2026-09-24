import unittest
import json
import os
from typing import Any
from unittest.mock import patch
from flask import Flask, Response
from routes.auth import auth_bp
from utils.auth import admin_required


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


class TestAdminSessionRoutes(unittest.TestCase):
    """Tests for password login, logout, and session reporting."""

    LOGIN_API_PATH: str = '/api/login'
    LOGOUT_API_PATH: str = '/api/logout'
    SESSION_API_PATH: str = '/api/session'
    PROTECTED_PATH: str = '/api/protected'
    ADMIN_PASSWORD: str = 'test-admin-password'

    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.register_blueprint(auth_bp)

        # A minimal protected route exercises the decorator in isolation.
        @self.app.route(self.PROTECTED_PATH)
        @admin_required
        def protected() -> Any:
            return {"ok": True}

        self.client = self.app.test_client()

        self._password_patcher = patch.dict(
            os.environ, {'ADMIN_PASSWORD': self.ADMIN_PASSWORD}
        )
        self._password_patcher.start()

    def tearDown(self) -> None:
        self._password_patcher.stop()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def _login(self, password: str | None = None) -> Response:
        """Post the given password (defaults to the correct one) to the login endpoint."""
        return self.client.post(
            self.LOGIN_API_PATH,
            json={"password": self.ADMIN_PASSWORD if password is None else password},
        )

    def test_login_with_correct_password_authenticates(self) -> None:
        """The correct password should establish an authenticated session."""
        response = self._login()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._get_response_data(response)['authenticated'])

    def test_login_with_wrong_password_rejected(self) -> None:
        """An incorrect password should return 401 and not authenticate."""
        response = self._login('not-the-password')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(self._get_response_data(response)['error'], "Invalid password")

    def test_login_with_missing_password_rejected(self) -> None:
        """A request with no password field should return 401."""
        response = self.client.post(self.LOGIN_API_PATH, json={})

        self.assertEqual(response.status_code, 401)

    def test_login_with_empty_password_rejected(self) -> None:
        """An empty password should return 401 rather than pass validation."""
        response = self._login('')

        self.assertEqual(response.status_code, 401)

    def test_login_with_non_string_password_rejected(self) -> None:
        """A non-string password should be rejected without raising."""
        response = self.client.post(self.LOGIN_API_PATH, json={"password": 12345})

        self.assertEqual(response.status_code, 401)

    def test_login_with_non_ascii_password_rejected(self) -> None:
        """A non-ASCII password should be rejected cleanly rather than erroring."""
        response = self._login('pässwörtü')

        self.assertEqual(response.status_code, 401)

    def test_login_succeeds_with_non_ascii_configured_password(self) -> None:
        """A non-ASCII configured password should still authenticate correctly."""
        non_ascii_password = 'sükkérpässwörd'

        with patch.dict(os.environ, {'ADMIN_PASSWORD': non_ascii_password}):
            response = self._login(non_ascii_password)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._get_response_data(response)['authenticated'])

    def test_session_reports_unauthenticated_by_default(self) -> None:
        """A fresh client should report no admin session."""
        response = self.client.get(self.SESSION_API_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._get_response_data(response)['authenticated'])

    def test_session_reports_authenticated_after_login(self) -> None:
        """The session endpoint should reflect a successful login."""
        self._login()

        response = self.client.get(self.SESSION_API_PATH)

        self.assertTrue(self._get_response_data(response)['authenticated'])

    def test_logout_clears_session(self) -> None:
        """Logging out should end the admin session."""
        self._login()

        logout_response = self.client.post(self.LOGOUT_API_PATH)
        session_response = self.client.get(self.SESSION_API_PATH)

        self.assertEqual(logout_response.status_code, 200)
        self.assertFalse(self._get_response_data(logout_response)['authenticated'])
        self.assertFalse(self._get_response_data(session_response)['authenticated'])

    def test_logout_when_not_logged_in_is_safe(self) -> None:
        """Logging out without a session should succeed rather than error."""
        response = self.client.post(self.LOGOUT_API_PATH)

        self.assertEqual(response.status_code, 200)

    def test_admin_required_blocks_anonymous_requests(self) -> None:
        """The decorator should return 401 with a JSON error for anonymous callers."""
        response = self.client.get(self.PROTECTED_PATH)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            self._get_response_data(response)['error'], "Authentication required"
        )

    def test_admin_required_allows_authenticated_requests(self) -> None:
        """The decorator should pass through once the session is authenticated."""
        self._login()

        response = self.client.get(self.PROTECTED_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._get_response_data(response)['ok'])


if __name__ == '__main__':
    unittest.main()

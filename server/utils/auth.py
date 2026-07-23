"""Admin authentication helpers.

Authentication is intentionally minimal: a single admin password supplied via the
``ADMIN_PASSWORD`` environment variable, tracked with Flask's signed session
cookie. There is no user table, so nothing here persists to the database.
"""
import hmac
import os
from functools import wraps
from typing import Any, Callable

from flask import jsonify, session

# Session key used to mark a request as an authenticated admin.
ADMIN_SESSION_KEY = 'is_admin'

# Development fallbacks. These are deliberately obvious, non-secret values used
# only when the environment does not supply real ones, so a fresh clone runs
# without configuration. Production deployments must set both env vars.
DEV_ADMIN_PASSWORD = 'tailspin-admin'
DEV_SECRET_KEY = 'dev-only-insecure-secret-key'


def get_admin_password() -> str:
    """Return the configured admin password, falling back to the dev default."""
    return os.environ.get('ADMIN_PASSWORD') or DEV_ADMIN_PASSWORD


def get_secret_key() -> str:
    """Return the Flask secret key used to sign the session cookie."""
    return os.environ.get('FLASK_SECRET_KEY') or DEV_SECRET_KEY


def using_dev_credentials() -> bool:
    """True when either credential falls back to its development default."""
    return not os.environ.get('ADMIN_PASSWORD') or not os.environ.get('FLASK_SECRET_KEY')


def verify_password(candidate: Any) -> bool:
    """Constant-time comparison of a submitted password against the configured one."""
    if not isinstance(candidate, str) or not candidate:
        return False

    # Compare bytes: compare_digest rejects str arguments containing non-ASCII.
    return hmac.compare_digest(
        candidate.encode('utf-8'), get_admin_password().encode('utf-8')
    )


def is_authenticated() -> bool:
    """True when the current session belongs to a logged-in admin."""
    return bool(session.get(ADMIN_SESSION_KEY))


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Reject unauthenticated requests with a 401 before running the view."""
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401

        return view(*args, **kwargs)

    return wrapped

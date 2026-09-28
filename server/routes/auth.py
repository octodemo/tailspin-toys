from flask import Blueprint, jsonify, request, redirect, session, Response
from urllib.parse import urlparse

from utils.auth import ADMIN_SESSION_KEY, is_authenticated, verify_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['GET'])
def login() -> Response:
    """Post-login redirect helper. Credential login is handled by POST /api/login."""
    next_url = request.args.get('next', '/')

    # Validate the next_url to prevent open redirects. Only allow relative URLs.
    if isinstance(next_url, str):
        # Normalize backslashes which some browsers treat as path separators.
        cleaned_next = next_url.replace('\\', '')
        parsed = urlparse(cleaned_next)
        # Allow only paths without an explicit scheme or network location.
        if not parsed.scheme and not parsed.netloc and cleaned_next:
            return redirect(cleaned_next)

    # Fallback: redirect to home if the next parameter is unsafe or empty.
    return redirect('/')


@auth_bp.route('/api/login', methods=['POST'])
def admin_login() -> tuple[Response, int] | Response:
    """Authenticate an admin with the shared password and start a session."""
    payload = request.get_json(silent=True) or {}
    password = payload.get('password')

    if not verify_password(password):
        return jsonify({"error": "Invalid password"}), 401

    session[ADMIN_SESSION_KEY] = True
    # Session ends with the browser session; admins re-authenticate each time.
    session.permanent = False

    return jsonify({"authenticated": True})


@auth_bp.route('/api/logout', methods=['POST'])
def admin_logout() -> Response:
    """Clear the admin session. Safe to call when not logged in."""
    session.pop(ADMIN_SESSION_KEY, None)

    return jsonify({"authenticated": False})


@auth_bp.route('/api/session', methods=['GET'])
def admin_session() -> Response:
    """Report whether the caller is an authenticated admin."""
    return jsonify({"authenticated": is_authenticated()})

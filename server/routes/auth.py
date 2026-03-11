from flask import Blueprint, request, redirect, Response
from urllib.parse import urlparse

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['GET'])
def login() -> Response:
    """Login page that redirects to the next URL after authentication."""
    next_url = request.args.get('next', '/')

    # Normalize backslashes and validate that the target is a relative URL.
    if next_url:
        normalized = next_url.replace('\\', '/')
        parsed = urlparse(normalized)
        # Only allow relative URLs without scheme or netloc, and with a safe path.
        if not parsed.scheme and not parsed.netloc and (parsed.path.startswith('/') or parsed.path == ''):
            safe_next = normalized
        else:
            safe_next = '/'
    else:
        safe_next = '/'

    # TODO: Add actual authentication logic here
    return redirect(safe_next)

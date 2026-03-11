from flask import Blueprint, request, redirect, Response
from urllib.parse import urlparse

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['GET'])
def login() -> Response:
    """Login page that redirects to the next URL after authentication."""
    next_url = request.args.get('next', '/')
    # TODO: Add actual authentication logic here

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

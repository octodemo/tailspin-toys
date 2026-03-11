from flask import Blueprint, request, redirect, Response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['GET'])
def login() -> Response:
    """Login page that redirects to the next URL after authentication."""
    next_url = request.args.get('next', '/')
    # TODO: Add actual authentication logic here
    return redirect(next_url)

import os
from flask import Flask
from routes.games import games_bp
from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.publishers import publishers_bp
from models import db
from utils.auth import get_secret_key, using_dev_credentials
from utils.database import get_connection_string
from utils.migrations import ensure_schema
from utils.seed_database import seed_database

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)

# Secret key signs the admin session cookie
app.config['SECRET_KEY'] = get_secret_key()

# Configure and initialize the database
app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_string()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables, apply pending column additions, then seed data (all idempotent)
with app.app_context():
    db.create_all()
    ensure_schema()
    seed_database()

# Register blueprints
app.register_blueprint(games_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(publishers_bp)

if using_dev_credentials():
    print(
        'WARNING: using development admin credentials. '
        'Set ADMIN_PASSWORD and FLASK_SECRET_KEY before deploying.'
    )

def _env_flag(name: str, default: bool = False) -> bool:
    value: str = os.environ.get(name, "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on"}


if __name__ == '__main__':
    # Hot-reload is on by default; the interactive Werkzeug debugger is opt-in
    # via FLASK_INTERACTIVE_DEBUGGER because it requires POSIX semaphores that
    # are blocked under some sandboxed environments.
    use_reloader: bool = _env_flag("FLASK_DEBUG", default=True)
    use_debugger: bool = _env_flag("FLASK_INTERACTIVE_DEBUGGER", default=False)
    app.run(
        host='0.0.0.0',
        port=5100,  # Port 5100 to avoid macOS conflicts
        use_reloader=use_reloader,
        use_debugger=use_debugger,
    )
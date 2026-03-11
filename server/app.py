import os
from flask import Flask
from routes.games import games_bp
from models import db
from utils.database import get_connection_string
from utils.seed_database import seed_database

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)

# Configure and initialize the database
app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_string()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables and seed data (idempotent — skips existing records)
with app.app_context():
    db.create_all()
    seed_database()

# Register blueprints
app.register_blueprint(games_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5100) # Port 5100 to avoid macOS conflicts
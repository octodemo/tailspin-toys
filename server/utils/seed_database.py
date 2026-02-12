import csv
import os
import random
from flask import Flask
from models import db, Category, Game, Publisher
from utils.database import get_connection_string

def create_app():
    """Create and configure Flask app for database operations"""
    app = Flask(__name__)

    # Configure and initialize the database
    app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_string()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

def create_games():
    """Create games, categories and publishers from CSV data for crowd funding platform"""
    app = create_app()
    
    with app.app_context():
        # Track which categories and publishers have been created
        categories = {}  # name -> category object
        publishers = {}  # name -> publisher object
        
        # Read the CSV file
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              'seed_data', 'games.csv')
        
        games_created = 0
        games_skipped = 0
        categories_created = 0
        publishers_created = 0
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                # Process category — query DB first for idempotency
                category_name = row['Category']
                if category_name not in categories:
                    category = Category.query.filter_by(name=category_name).first()
                    if not category:
                        category_description = f"Collection of {category_name} games available for crowdfunding"
                        category = Category(
                            name=category_name,
                            description=category_description
                        )
                        db.session.add(category)
                        db.session.flush()  # Get ID without committing
                        categories_created += 1
                    categories[category_name] = category
                
                # Process publisher — query DB first for idempotency
                publisher_name = row['Publisher']
                if publisher_name not in publishers:
                    publisher = Publisher.query.filter_by(name=publisher_name).first()
                    if not publisher:
                        publisher_description = f"{publisher_name} is a game publisher seeking funding for exciting new titles"
                        publisher = Publisher(
                            name=publisher_name,
                            description=publisher_description
                        )
                        db.session.add(publisher)
                        db.session.flush()  # Get ID without committing
                        publishers_created += 1
                    publishers[publisher_name] = publisher
                
                # Check if game already exists by title before creating
                existing_game = Game.query.filter_by(title=row['Title']).first()
                if existing_game:
                    games_skipped += 1
                    continue
                
                # Generate random star rating between 3.0 and 5.0 (one decimal place)
                star_rating = round(random.uniform(3.0, 5.0), 1)
                
                # Create the game with enhanced description for crowdfunding context
                game = Game(
                    title=row['Title'],
                    description=row['Description'] + " Support this game through our crowdfunding platform!",
                    category_id=categories[category_name].id,
                    publisher_id=publishers[publisher_name].id,
                    star_rating=star_rating,
                )
                db.session.add(game)
                games_created += 1
            
            # Commit all changes at once
            db.session.commit()
            
        print(f"Created {games_created} games, {categories_created} categories, {publishers_created} publishers (skipped {games_skipped} existing games)")

def seed_database():
    create_games()

if __name__ == '__main__':
    seed_database()
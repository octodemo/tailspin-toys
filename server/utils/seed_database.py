import csv
import os
import random
from flask import Flask
from models import db, Category, Game, Publisher, StretchGoal
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
        games_list = []  # Track created games for stretch goals

        # Read the CSV file
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'seed_data', 'games.csv')

        game_count = 0
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                game_count += 1
                # Process category
                category_name = row['Category']
                if category_name not in categories:
                    # Create new category if it doesn't exist
                    category_description = f"Collection of {category_name} games available for crowdfunding"
                    category = Category(
                        name=category_name,
                        description=category_description
                    )
                    db.session.add(category)
                    db.session.flush()  # Get ID without committing
                    categories[category_name] = category

                # Process publisher
                publisher_name = row['Publisher']
                if publisher_name not in publishers:
                    # Create new publisher if it doesn't exist
                    publisher_description = f"{publisher_name} is a game publisher seeking funding for exciting new titles"
                    publisher = Publisher(
                        name=publisher_name,
                        description=publisher_description
                    )
                    db.session.add(publisher)
                    db.session.flush()  # Get ID without committing
                    publishers[publisher_name] = publisher

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
                games_list.append(game)

            # Commit all changes at once
            db.session.commit()

        # Add stretch goals to some games
        create_stretch_goals(games_list)

        print(f"Added {game_count} games with {len(categories)} categories and {len(publishers)} publishers")

def create_stretch_goals(games_list: list[Game]) -> None:
    """Create sample stretch goals for some games"""
    # Stretch goal templates
    stretch_goal_templates = [
        {
            "title": "Enhanced Components",
            "description": "Upgrade to premium game components including metal coins and wooden meeples",
            "goal_type": "pledge_total",
            "target_amount": 50000
        },
        {
            "title": "Expansion Pack",
            "description": "Unlock an expansion pack with 20 new cards and 3 additional scenarios",
            "goal_type": "pledge_total",
            "target_amount": 75000
        },
        {
            "title": "Multiplayer Mode",
            "description": "Add online multiplayer support for up to 4 players",
            "goal_type": "pledge_count",
            "target_amount": 500
        },
        {
            "title": "Deluxe Edition",
            "description": "Create a deluxe edition with special art and premium packaging",
            "goal_type": "pledge_total",
            "target_amount": 100000
        },
        {
            "title": "Community Milestone",
            "description": "Reach 1000 backers to unlock exclusive backer rewards",
            "goal_type": "pledge_count",
            "target_amount": 1000
        },
        {
            "title": "Extra Game Modes",
            "description": "Add 3 new game modes including hard difficulty and time trial",
            "goal_type": "pledge_count",
            "target_amount": 750
        }
    ]

    # Add 2-3 stretch goals to each of the first 5 games
    for i, game in enumerate(games_list[:5]):
        num_goals = random.randint(2, 3)
        # Select random templates
        selected_templates = random.sample(stretch_goal_templates, num_goals)

        for template in selected_templates:
            # Calculate random current progress (0-120% of target)
            progress_percentage = random.uniform(0, 1.2)
            current_amount = int(template["target_amount"] * progress_percentage)

            stretch_goal = StretchGoal(
                title=template["title"],
                description=template["description"],
                goal_type=template["goal_type"],
                target_amount=template["target_amount"],
                current_amount=current_amount,
                game_id=game.id
            )
            db.session.add(stretch_goal)

    db.session.commit()
    print(f"Added stretch goals to {min(5, len(games_list))} games")

def seed_database():
    create_games()

if __name__ == '__main__':
    seed_database()
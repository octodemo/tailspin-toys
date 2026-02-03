from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

# TODO: Add Create, Update, Delete endpoints to complete CRUD functionality
# - POST /api/games - Create a new game
# - PUT /api/games/<id> - Update an existing game
# - DELETE /api/games/<id> - Delete a game

def get_games_base_query() -> Query:
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    
    # Use the base query for all games
    base_query = get_games_base_query()
    
    # Get total count
    total_count = base_query.count()
    
    # Calculate pagination values
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Apply pagination
    games_query = base_query.limit(page_size).offset(offset).all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    # Return paginated response with metadata
    return jsonify({
        'games': games_list,
        'pagination': {
            'page': page,
            'pageSize': page_size,
            'totalCount': total_count,
            'totalPages': total_pages
        }
    })

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query, contains_eager

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

# TODO: Add Create, Update, Delete endpoints to complete CRUD functionality
# - POST /api/games - Create a new game
# - PUT /api/games/<id> - Update an existing game
# - DELETE /api/games/<id> - Delete a game

DEFAULT_PAGE_SIZE = 9

def get_games_base_query() -> Query:
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    ).options(
        contains_eager(Game.publisher),
        contains_eager(Game.category)
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=DEFAULT_PAGE_SIZE, type=int)

    # Clamp pagination values
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    games_query = get_games_base_query().order_by(Game.title.asc())

    # Get total count before pagination (clear ordering for performance)
    total = games_query.order_by(None).count()
    total_pages = max(1, (total + page_size - 1) // page_size)

    # Apply pagination
    offset = (page - 1) * page_size
    games_list = [game.to_dict() for game in games_query.offset(offset).limit(page_size).all()]
    
    return jsonify({
        "games": games_list,
        "pagination": {
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": total_pages,
        },
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

from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query, contains_eager
from sqlalchemy import func

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

def get_available_filters() -> dict[str, list[str]]:
    """Return distinct publisher and category names for filter dropdowns."""
    publishers = [
        name for (name,) in db.session.query(Publisher.name)
        .join(Game, Game.publisher_id == Publisher.id)
        .distinct().order_by(Publisher.name).all()
    ]
    categories = [
        name for (name,) in db.session.query(Category.name)
        .join(Game, Game.category_id == Category.id)
        .distinct().order_by(Category.name).all()
    ]
    return {"publishers": publishers, "categories": categories}

VALID_SORT_OPTIONS: dict[str, list] = {
    'rating': [Game.star_rating.desc().nulls_last(), Game.title.asc()],
    'title': [Game.title.asc()],
}
DEFAULT_SORT = 'rating'

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    publisher_filter = request.args.get('publisher', type=str)
    category_filter = request.args.get('category', type=str)
    sort_param = request.args.get('sort', default=DEFAULT_SORT, type=str)
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=DEFAULT_PAGE_SIZE, type=int)

    # Clamp pagination values
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    games_query = get_games_base_query()

    if publisher_filter and publisher_filter.strip():
        normalized_publisher = publisher_filter.strip().lower()
        games_query = games_query.filter(
            func.lower(Publisher.name) == normalized_publisher
        )

    if category_filter and category_filter.strip():
        normalized_category = category_filter.strip().lower()
        games_query = games_query.filter(
            func.lower(Category.name) == normalized_category
        )

    # Apply sorting
    sort_key = sort_param.strip().lower() if sort_param else DEFAULT_SORT
    order_clauses = VALID_SORT_OPTIONS.get(sort_key, VALID_SORT_OPTIONS[DEFAULT_SORT])
    games_query = games_query.order_by(*order_clauses)

    # Get total count before pagination
    total = games_query.count()
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
        "filters": get_available_filters(),
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

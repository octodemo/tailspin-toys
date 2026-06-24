from flask import jsonify, Response, Blueprint, request
from sqlalchemy import Select, func, select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import contains_eager
from models import db, Game, Publisher, Category

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

# TODO: Add Create, Update, Delete endpoints to complete CRUD functionality
# - POST /api/games - Create a new game
# - PUT /api/games/<id> - Update an existing game
# - DELETE /api/games/<id> - Delete a game

DEFAULT_PAGE_SIZE = 9

SORT_OPTIONS: dict[str, ColumnElement] = {
    "title": Game.title.asc(),
    "mostFunded": Game.star_rating.desc().nullslast(),
}

def get_games_base_stmt() -> Select:
    return (
        select(Game)
        .join(Publisher, Game.publisher_id == Publisher.id, isouter=True)
        .join(Category, Game.category_id == Category.id, isouter=True)
        .options(
            contains_eager(Game.publisher),
            contains_eager(Game.category),
        )
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=DEFAULT_PAGE_SIZE, type=int)
    sort = request.args.get('sort', default='title', type=str)
    order_by = SORT_OPTIONS.get(sort or 'title', SORT_OPTIONS['title'])

    # Clamp pagination values
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    base_stmt = get_games_base_stmt().order_by(order_by)

    # Get total count before pagination (clear ordering for performance)
    count_stmt = select(func.count()).select_from(base_stmt.order_by(None).subquery())
    total = db.session.scalar(count_stmt) or 0
    total_pages = max(1, (total + page_size - 1) // page_size)

    # Apply pagination
    offset = (page - 1) * page_size
    paginated_stmt = base_stmt.offset(offset).limit(page_size)
    games_list = [game.to_dict() for game in db.session.scalars(paginated_stmt).unique().all()]

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
    # Use the base statement and add filter for specific game
    stmt = get_games_base_stmt().where(Game.id == id)
    game = db.session.scalars(stmt).unique().one_or_none()

    # Return 404 if game not found
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Convert the result using the model's to_dict method
    return jsonify(game.to_dict())

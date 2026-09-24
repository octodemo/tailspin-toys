from flask import jsonify, Response, Blueprint, request
from sqlalchemy import Select, func, select
from sqlalchemy.orm import contains_eager
from models import db, Game, Publisher, Category
from utils.auth import admin_required, is_authenticated

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

DEFAULT_PAGE_SIZE = 9

# Fields accepted when creating or updating a game, mapped to their model attribute.
GAME_FIELDS: dict[str, str] = {
    'title': 'title',
    'description': 'description',
    'starRating': 'star_rating',
    'categoryId': 'category_id',
    'publisherId': 'publisher_id',
}

REQUIRED_CREATE_FIELDS = ('title', 'description', 'categoryId', 'publisherId')


def get_games_base_stmt(include_archived: bool = False) -> Select:
    stmt = (
        select(Game)
        .join(Publisher, Game.publisher_id == Publisher.id, isouter=True)
        .join(Category, Game.category_id == Category.id, isouter=True)
        .options(
            contains_eager(Game.publisher),
            contains_eager(Game.category),
        )
    )

    if not include_archived:
        stmt = stmt.where(Game.is_archived.is_(False))

    return stmt


def _get_game(id: int, include_archived: bool = False) -> Game | None:
    stmt = get_games_base_stmt(include_archived=include_archived).where(Game.id == id)
    return db.session.scalars(stmt).unique().one_or_none()


def _related_id_error(payload: dict, field: str, model: type, label: str) -> str | None:
    """Validate that a submitted foreign key references an existing row."""
    if field not in payload:
        return None

    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        return f"{label} id must be an integer"

    if db.session.get(model, value) is None:
        return f"{label} not found"

    return None


def _apply_payload(game: Game, payload: dict) -> None:
    """Copy known fields from a request payload onto a game instance."""
    for field, attribute in GAME_FIELDS.items():
        if field in payload:
            setattr(game, attribute, payload[field])


def _validate_related_ids(payload: dict) -> str | None:
    """Return the first foreign-key validation error, if any."""
    for field, model, label in (
        ('categoryId', Category, 'Category'),
        ('publisherId', Publisher, 'Publisher'),
    ):
        error = _related_id_error(payload, field, model, label)
        if error:
            return error

    return None


@games_bp.route('/api/games', methods=['GET'])
def get_games() -> tuple[Response, int] | Response:
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=DEFAULT_PAGE_SIZE, type=int)
    include_archived = request.args.get('includeArchived', '').lower() in {'1', 'true', 'yes'}

    # Archived games are admin-only, so surface them just to authenticated callers.
    if include_archived and not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401

    # Clamp pagination values
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    base_stmt = get_games_base_stmt(include_archived=include_archived).order_by(Game.title.asc())

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
    # Admins can inspect archived games so they can review before restoring.
    game = _get_game(id, include_archived=is_authenticated())

    # Return 404 if game not found
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Convert the result using the model's to_dict method
    return jsonify(game.to_dict())


@games_bp.route('/api/games', methods=['POST'])
@admin_required
def create_game() -> tuple[Response, int]:
    payload = request.get_json(silent=True) or {}

    missing = [field for field in REQUIRED_CREATE_FIELDS if payload.get(field) in (None, '')]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    related_error = _validate_related_ids(payload)
    if related_error:
        return jsonify({"error": related_error}), 400

    game = Game()
    try:
        _apply_payload(game, payload)
        db.session.add(game)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400

    created = _get_game(game.id, include_archived=True)

    return jsonify(created.to_dict()), 201


@games_bp.route('/api/games/<int:id>', methods=['PUT'])
@admin_required
def update_game(id: int) -> tuple[Response, int] | Response:
    game = _get_game(id, include_archived=True)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    payload = request.get_json(silent=True) or {}

    related_error = _validate_related_ids(payload)
    if related_error:
        return jsonify({"error": related_error}), 400

    try:
        _apply_payload(game, payload)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400

    return jsonify(game.to_dict())


@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
@admin_required
def archive_game(id: int) -> tuple[Response, int] | Response:
    """Soft delete: hide the game from the public catalog but keep the record."""
    game = _get_game(id, include_archived=True)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    game.is_archived = True
    db.session.commit()

    return jsonify(game.to_dict())


@games_bp.route('/api/games/<int:id>/restore', methods=['POST'])
@admin_required
def restore_game(id: int) -> tuple[Response, int] | Response:
    """Return a previously archived game to the public catalog."""
    game = _get_game(id, include_archived=True)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    game.is_archived = False
    db.session.commit()

    return jsonify(game.to_dict())

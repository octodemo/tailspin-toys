from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category, Subscription
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

def _get_game_or_404(game_id: int) -> Game | None:
    return get_games_base_query().filter(Game.id == game_id).first()

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = _get_game_or_404(id)
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

@games_bp.route('/api/games/<int:game_id>/subscriptions', methods=['POST'])
def create_subscription(game_id: int) -> tuple[Response, int]:
    game = _get_game_or_404(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    payload = request.get_json(silent=True) or {}
    email = payload.get('email')
    frequency = payload.get('frequency', 'weekly')

    try:
        subscription = Subscription(email=email, frequency=frequency, game=game)
        db.session.add(subscription)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400

    return jsonify(subscription.to_dict()), 201

@games_bp.route('/api/games/<int:game_id>/subscriptions', methods=['GET'])
def list_subscriptions(game_id: int) -> tuple[Response, int]:
    game = _get_game_or_404(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    subscriptions = db.session.query(Subscription).filter(
        Subscription.game_id == game_id,
        Subscription.is_active.is_(True)
    ).all()

    return jsonify([sub.to_dict() for sub in subscriptions]), 200

@games_bp.route('/api/subscriptions/<int:subscription_id>', methods=['PATCH'])
def update_subscription(subscription_id: int) -> tuple[Response, int]:
    subscription: Subscription | None = db.session.get(Subscription, subscription_id)
    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    payload = request.get_json(silent=True) or {}
    frequency = payload.get('frequency')
    is_active = payload.get('isActive')

    try:
        if frequency is not None:
            subscription.frequency = frequency
        if is_active is not None:
            subscription.is_active = bool(is_active)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400

    return jsonify(subscription.to_dict())

@games_bp.route('/api/subscriptions/<int:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id: int) -> tuple[Response, int]:
    subscription: Subscription | None = db.session.get(Subscription, subscription_id)
    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    subscription.is_active = False
    db.session.commit()
    return jsonify({"message": "Unsubscribed successfully", "id": subscription_id})

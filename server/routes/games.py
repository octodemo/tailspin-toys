from flask import jsonify, request, Response, Blueprint
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

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
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    return jsonify(games_list)

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


@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'description', 'publisher_id', 'category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Validate publisher exists
    publisher = db.session.get(Publisher, data['publisher_id'])
    if not publisher:
        return jsonify({"error": "Publisher not found"}), 404
    
    # Validate category exists
    category = db.session.get(Category, data['category_id'])
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    # Create new game
    game = Game(
        title=data['title'],
        description=data['description'],
        publisher_id=data['publisher_id'],
        category_id=data['category_id'],
        star_rating=data.get('star_rating')
    )
    
    db.session.add(game)
    db.session.commit()
    
    # Refresh to load relationships
    db.session.refresh(game)
    
    return jsonify(game.to_dict()), 201


@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int] | Response:
    game = db.session.get(Game, id)
    
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        game.title = data['title']
    if 'description' in data:
        game.description = data['description']
    if 'star_rating' in data:
        game.star_rating = data['star_rating']
    
    # Validate and update publisher if provided
    if 'publisher_id' in data:
        publisher = db.session.get(Publisher, data['publisher_id'])
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 404
        game.publisher_id = data['publisher_id']
    
    # Validate and update category if provided
    if 'category_id' in data:
        category = db.session.get(Category, data['category_id'])
        if not category:
            return jsonify({"error": "Category not found"}), 404
        game.category_id = data['category_id']
    
    db.session.commit()
    db.session.refresh(game)
    
    return jsonify(game.to_dict())


@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    game = db.session.get(Game, id)
    
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    db.session.delete(game)
    db.session.commit()
    
    return jsonify({"message": "Game deleted successfully"}), 200

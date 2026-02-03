from flask import jsonify, Response, Blueprint, request
from models import db, StretchGoal, Game
from sqlalchemy.orm import Query

# Create a Blueprint for stretch goals routes
stretch_goals_bp = Blueprint('stretch_goals', __name__)

def get_stretch_goals_base_query() -> Query:
    """Base query for stretch goals with game relationship"""
    return db.session.query(StretchGoal).join(
        Game,
        StretchGoal.game_id == Game.id,
        isouter=True
    )

@stretch_goals_bp.route('/api/games/<int:game_id>/stretch-goals', methods=['GET'])
def get_stretch_goals(game_id: int) -> tuple[Response, int] | Response:
    """Get all stretch goals for a specific game"""
    # First check if the game exists
    game = db.session.query(Game).filter(Game.id == game_id).first()
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Get all stretch goals for this game
    stretch_goals = get_stretch_goals_base_query().filter(
        StretchGoal.game_id == game_id
    ).all()

    # Convert the results using the model's to_dict method
    goals_list = [goal.to_dict() for goal in stretch_goals]

    return jsonify(goals_list)

@stretch_goals_bp.route('/api/games/<int:game_id>/stretch-goals', methods=['POST'])
def create_stretch_goal(game_id: int) -> tuple[Response, int]:
    """Create a new stretch goal for a specific game"""
    # Check if the game exists
    game = db.session.query(Game).filter(Game.id == game_id).first()
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Get JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate required fields
    required_fields = ['title', 'description', 'goalType', 'targetAmount']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Create new stretch goal
    try:
        stretch_goal = StretchGoal(
            title=data['title'],
            description=data['description'],
            goal_type=data['goalType'],
            target_amount=data['targetAmount'],
            current_amount=data.get('currentAmount', 0),
            game_id=game_id
        )
        db.session.add(stretch_goal)
        db.session.commit()

        return jsonify(stretch_goal.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create stretch goal"}), 500

@stretch_goals_bp.route('/api/stretch-goals/<int:id>', methods=['GET'])
def get_stretch_goal(id: int) -> tuple[Response, int] | Response:
    """Get a specific stretch goal by ID"""
    stretch_goal = get_stretch_goals_base_query().filter(StretchGoal.id == id).first()

    if not stretch_goal:
        return jsonify({"error": "Stretch goal not found"}), 404

    return jsonify(stretch_goal.to_dict())

@stretch_goals_bp.route('/api/stretch-goals/<int:id>', methods=['PUT'])
def update_stretch_goal(id: int) -> tuple[Response, int]:
    """Update a specific stretch goal"""
    stretch_goal = db.session.query(StretchGoal).filter(StretchGoal.id == id).first()

    if not stretch_goal:
        return jsonify({"error": "Stretch goal not found"}), 404

    # Get JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update fields if provided
    try:
        if 'title' in data:
            stretch_goal.title = data['title']
        if 'description' in data:
            stretch_goal.description = data['description']
        if 'goalType' in data:
            stretch_goal.goal_type = data['goalType']
        if 'targetAmount' in data:
            stretch_goal.target_amount = data['targetAmount']
        if 'currentAmount' in data:
            stretch_goal.current_amount = data['currentAmount']

        db.session.commit()
        return jsonify(stretch_goal.to_dict()), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update stretch goal"}), 500

@stretch_goals_bp.route('/api/stretch-goals/<int:id>', methods=['DELETE'])
def delete_stretch_goal(id: int) -> tuple[Response, int]:
    """Delete a specific stretch goal"""
    stretch_goal = db.session.query(StretchGoal).filter(StretchGoal.id == id).first()

    if not stretch_goal:
        return jsonify({"error": "Stretch goal not found"}), 404

    try:
        db.session.delete(stretch_goal)
        db.session.commit()
        return jsonify({"message": "Stretch goal deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete stretch goal"}), 500

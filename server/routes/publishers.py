from flask import jsonify, Response, Blueprint
from models import db, Publisher, Game

publishers_bp = Blueprint('publishers', __name__)


@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    publishers = db.session.query(Publisher).order_by(Publisher.name.asc()).all()
    return jsonify({
        "publishers": [publisher.to_dict() for publisher in publishers],
    })


@publishers_bp.route('/api/publishers/<int:id>', methods=['GET'])
def get_publisher(id: int) -> tuple[Response, int] | Response:
    publisher = db.session.query(Publisher).filter(Publisher.id == id).first()

    if not publisher:
        return jsonify({"error": "Publisher not found"}), 404

    games = db.session.query(Game).filter(
        Game.publisher_id == id
    ).order_by(Game.title.asc()).all()

    return jsonify({
        "id": publisher.id,
        "name": publisher.name,
        "description": publisher.description,
        "games": [
            {"id": game.id, "title": game.title}
            for game in games
        ],
    })

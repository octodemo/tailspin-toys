from flask import jsonify, Response, Blueprint
from sqlalchemy import func
from models import db, Publisher, Game

publishers_bp = Blueprint('publishers', __name__)


@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    results = (
        db.session.query(
            Publisher.id,
            Publisher.name,
            Publisher.description,
            func.count(Game.id).label('game_count')
        )
        .outerjoin(Game, Game.publisher_id == Publisher.id)
        .group_by(Publisher.id)
        .order_by(Publisher.name.asc())
        .all()
    )

    publishers = [
        {
            'id': row.id,
            'name': row.name,
            'description': row.description,
            'gameCount': row.game_count,
        }
        for row in results
    ]

    return jsonify(publishers)

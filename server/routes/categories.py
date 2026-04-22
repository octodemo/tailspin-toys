from flask import jsonify, Response, Blueprint
from sqlalchemy import func
from models import db, Category, Game

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    results = (
        db.session.query(
            Category.id,
            Category.name,
            Category.description,
            func.count(Game.id).label('game_count')
        )
        .outerjoin(Game, Game.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
        .all()
    )

    categories = [
        {
            'id': row.id,
            'name': row.name,
            'description': row.description,
            'gameCount': row.game_count,
        }
        for row in results
    ]

    return jsonify(categories)

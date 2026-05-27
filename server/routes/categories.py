from flask import jsonify, Response, Blueprint
from models import db, Category, Game

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    categories = db.session.query(Category).order_by(Category.name.asc()).all()
    return jsonify({
        "categories": [category.to_dict() for category in categories],
    })


@categories_bp.route('/api/categories/<int:id>', methods=['GET'])
def get_category(id: int) -> tuple[Response, int] | Response:
    category = db.session.query(Category).filter(Category.id == id).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    games = db.session.query(Game).filter(
        Game.category_id == id
    ).order_by(Game.title.asc()).all()

    return jsonify({
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "games": [
            {"id": game.id, "title": game.title}
            for game in games
        ],
    })

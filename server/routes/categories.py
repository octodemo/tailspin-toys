from flask import jsonify, Response, Blueprint
from models import db, Category
from sqlalchemy.orm import Query

# Create a Blueprint for categories routes
categories_bp = Blueprint('categories', __name__)


def get_categories_base_query() -> Query:
    """Return base query for categories ordered by name."""
    return db.session.query(Category).order_by(Category.name)


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    """Get all categories for dropdown population."""
    categories_query = get_categories_base_query().all()
    categories_list = [category.to_dict_minimal() for category in categories_query]
    return jsonify(categories_list)


@categories_bp.route('/api/categories/<int:id>', methods=['GET'])
def get_category(id: int) -> tuple[Response, int] | Response:
    """Get a single category by ID."""
    category = get_categories_base_query().filter(Category.id == id).first()
    
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    return jsonify(category.to_dict())

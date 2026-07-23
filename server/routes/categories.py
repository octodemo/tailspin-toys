from flask import jsonify, Response, Blueprint
from sqlalchemy import Select, select
from models import db, Category

# Create a Blueprint for category routes
categories_bp = Blueprint('categories', __name__)


def get_categories_base_stmt() -> Select:
    return select(Category).order_by(Category.name.asc())


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    """List all categories, used to populate admin form dropdowns."""
    categories = db.session.scalars(get_categories_base_stmt()).unique().all()

    return jsonify({"categories": [category.to_dict() for category in categories]})

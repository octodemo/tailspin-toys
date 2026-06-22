from flask import jsonify, Response, Blueprint
from sqlalchemy import select
from models import db, Category

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    stmt = select(Category).order_by(Category.name.asc())
    categories = db.session.scalars(stmt).all()
    return jsonify([category.to_dict() for category in categories])

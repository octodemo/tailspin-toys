from flask import jsonify, Response, Blueprint
from models import db, Publisher
from sqlalchemy.orm import Query

# Create a Blueprint for publishers routes
publishers_bp = Blueprint('publishers', __name__)


def get_publishers_base_query() -> Query:
    """Return base query for publishers ordered by name."""
    return db.session.query(Publisher).order_by(Publisher.name)


@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    """Get all publishers for dropdown population."""
    publishers_query = get_publishers_base_query().all()
    publishers_list = [publisher.to_dict() for publisher in publishers_query]
    return jsonify(publishers_list)


@publishers_bp.route('/api/publishers/<int:id>', methods=['GET'])
def get_publisher(id: int) -> tuple[Response, int] | Response:
    """Get a single publisher by ID."""
    publisher = get_publishers_base_query().filter(Publisher.id == id).first()
    
    if not publisher:
        return jsonify({"error": "Publisher not found"}), 404
    
    return jsonify(publisher.to_dict())

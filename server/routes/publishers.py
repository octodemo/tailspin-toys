from flask import jsonify, Response, Blueprint
from sqlalchemy import Select, select
from models import db, Publisher

# Create a Blueprint for publisher routes
publishers_bp = Blueprint('publishers', __name__)


def get_publishers_base_stmt() -> Select:
    return select(Publisher).order_by(Publisher.name.asc())


@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    """List all publishers, used to populate admin form dropdowns."""
    publishers = db.session.scalars(get_publishers_base_stmt()).unique().all()

    return jsonify({"publishers": [publisher.to_dict() for publisher in publishers]})

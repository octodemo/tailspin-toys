from flask import jsonify, Response, Blueprint
from sqlalchemy import select
from models import db, Publisher

publishers_bp = Blueprint('publishers', __name__)


@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    stmt = select(Publisher).order_by(Publisher.name.asc())
    publishers = db.session.scalars(stmt).all()
    return jsonify([publisher.to_dict() for publisher in publishers])

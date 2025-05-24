from flask import Blueprint, jsonify

ping_bp = Blueprint('ping', __name__, url_prefix='/ping')

@ping_bp.route('/')
def ping():
    return jsonify({"status": "ok"}), 200
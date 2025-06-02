import os
from flask import Blueprint, Flask, request, jsonify, abort

BASE_IMPORT_DIR = os.getcwd()  # Set the base import directory to the current working directory

import_path_bp = Blueprint('import_path', __name__, url_prefix='/import_path')

@import_path_bp.route("/")
def index():
    cwd = os.getcwd()
    return jsonify({"message": "Import Path API is running", "cwd":cwd}), 200

def safe_join(base, *paths):
    # Prevents directory traversal attacks
    final_path = os.path.abspath(os.path.join(base, *paths))
    if not final_path.startswith(base):
        raise ValueError("Attempted directory traversal")
    return final_path

@import_path_bp.route('/browse', methods=['GET'])
def browse_dir():
    rel_path = request.args.get('path', '')
    try:
        abs_path = safe_join(BASE_IMPORT_DIR, rel_path)
    except ValueError:
        abort(400, "Invalid path")

    if not os.path.isdir(abs_path):
        abort(404, "Directory not found")

    dirs = []
    for entry in os.listdir(abs_path):
        full_entry = os.path.join(abs_path, entry)
        if os.path.isdir(full_entry):
            dirs.append(entry)

    # Add '..' unless at root
    parent_path = os.path.relpath(os.path.dirname(abs_path), BASE_IMPORT_DIR)
    if abs_path != BASE_IMPORT_DIR:
        dirs = ['..'] + dirs
    else:
        parent_path = None

    return jsonify({
        "current_path": os.path.relpath(abs_path, BASE_IMPORT_DIR),
        "parent_path": parent_path if parent_path != '.' else None,
        "directories": dirs
    })
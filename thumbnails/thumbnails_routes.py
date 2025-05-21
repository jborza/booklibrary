import os
from flask import Blueprint, jsonify, request
from models import Book
import hashlib

from thumbnails.thumbnails import make_large_cover_image, make_tiny_cover_image

thumbnails_bp = Blueprint("thumbnails", __name__, url_prefix="/thumbnails")

SIZE_THUMBNAIL = (128, 200)


@thumbnails_bp.route("/upload", methods=["POST"])
def upload_thumbnail():
    if request.method != "POST":
        return jsonify({"status": "error", "message": "Invalid request method"}), 405

    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"}), 400
    # save file to /tmp
    os.makedirs("tmp", exist_ok=True)
    file_path = os.path.join("tmp", file.filename)
    file.save(file_path)
    # make a hash of the file name
    file_hash = hashlib.sha1(file.filename.encode()).hexdigest() + ".jpg"
    # use the same extension as the original file
    # file_extension = os.path.splitext(file.filename)[1]
    large_name = make_large_cover_image(file_path, file_hash)
    os.remove(file_path)
    # save the file with the hash as the name
    # file_path = os.path.join('static', 'covers', file_hash + file_extension)
    # file.save(file_path)
    # TODO resize to thumbnail size
    file_path_tiny = make_tiny_cover_image(large_name)
    return (
        jsonify(
            {
                "status": "success",
                "message": "File uploaded successfully",
                "file_path": large_name,
                "file_path_tiny": file_path_tiny,
            }
        ),
        200,
    )

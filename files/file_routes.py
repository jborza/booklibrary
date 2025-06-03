from flask import abort, request, send_from_directory
from flask import Blueprint, jsonify
from files.files import BOOKS_DIR, get_supported_extensions, save_book_file
from models import Book, db
import os
from werkzeug.utils import secure_filename

files_bp = Blueprint('files', __name__, url_prefix='/files')

# endpoints - upload and download files
# files can be book files and cover images
# TODO let's migrate book covers from the static folder to this endpoint

@files_bp.route('/<book_id>/<filename>')
def serve_book_file(book_id, filename):
    # Sanitize filename to prevent directory traversal
    filename = secure_filename(filename)
    book_folder = os.path.join(BOOKS_DIR, book_id)
    if not os.path.exists(os.path.join(book_folder, filename)):
        abort(404)
    return send_from_directory(book_folder, filename, as_attachment=True)

@files_bp.route('/<int:book_id>/cover', methods=['POST'])
def upload_cover_image(book_id):
    book = Book.query.get_or_404(book_id)
    if 'cover' not in request.files:
        return jsonify({'error': 'No cover image part'}), 400
    cover = request.files['cover']
    if cover.filename == '':
        return jsonify({'error': 'No selected cover image'}), 400
    # save the cover image to the book's cover_image
    path = f'{book.id}/{cover.filename}'
    path = os.path.join(BOOKS_DIR, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cover.save(path)
    book.cover_image = path
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Cover image uploaded successfully'}), 200

@files_bp.route('/<int:book_id>/file', methods=['POST'])
def upload_book_file(book_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    try:
        path = save_book_file(
            book_id, file, file.filename, get_supported_extensions()
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    book = Book.query.get_or_404(book_id)
    book.file_path = path
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'File uploaded successfully'}), 200
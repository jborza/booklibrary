import os
from flask import Blueprint, request, jsonify, abort
from authors.authors_tools import get_author_by_name
from files.files import get_supported_extensions, save_book_file
from models import Book, db
from tools.metadata_calibre import get_metadata

BASE_IMPORT_DIR = os.getcwd()  # Set the base import directory to the current working directory

import_path_bp = Blueprint('import_path', __name__, url_prefix='/import_path')

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


@import_path_bp.route('/import', methods=['GET'])
def import_dir():
    rel_path = request.args.get('path', '')
    try:
        abs_path = safe_join(BASE_IMPORT_DIR, rel_path)
    except ValueError:
        abort(400, "Invalid path")

    if not os.path.isdir(abs_path):
        abort(404, "Directory not found")

    supported_extensions = get_supported_extensions()

    added_books = [] # will store tuple of (book, file_path)

    # List all files in the directory - but recursively
    for root, dirs, files in os.walk(abs_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Process the file
            # if it's not a supported file type, skip it
            if not any(file_path.lower().endswith(ext) for ext in supported_extensions):
                continue
            # Here you can add logic to import the file
            # For now, we will just print the file path
            print(f"Found supported file: {file_path}")
            author, title = get_metadata(file_path)

            # try to get author and title from file name if metadata extraction fails
            if author is None or title is None:
                just_filename = os.path.splitext(filename)[0]
                author, title = just_filename.split(' - ', 1) if ' - ' in just_filename else (None, None)
            if author is None:
                # If we still don't have an author, we can set a default value
                # Fallback to file name
                author = "Unknown"
                title = os.path.splitext(filename)[0]
            # generate a Book object
            # the same code as in confirm_import_api()
            author = get_author_by_name(author.strip())
            new_book = Book()
            new_book.author = author
            new_book.title = title.strip()
            db.session.add(new_book)
            # copy the file to the books directory - we can use upload_book_file -
            # but we don't have the book ID yet
            added_book_info = (new_book, file_path)
            added_books.append(added_book_info)
    db.session.commit()
    # after importing, get book IDs
    # now upload the files - we can use the upload_book_file endpoint
    for book, file_path in added_books:
        with open(file_path, 'rb') as f:
            file_path = os.path.basename(file_path)
            dest_path = save_book_file(
                book.id, f, file_path, get_supported_extensions()
            )
            book.file_path = os.path.basename(dest_path)
        # delete the original file
        os.remove(file_path)

    added_ids = [book.id for book, _ in added_books]
    db.session.commit()
    return jsonify({
        "message": "Books imported successfully",
        "added_books": added_ids
    }), 200

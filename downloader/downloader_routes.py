from flask import Blueprint, jsonify
from sqlalchemy.orm.exc import NoResultFound
from thumbnails.thumbnails import download_cover_image
from models import db, Book

downloader_bp = Blueprint('downloader', __name__, url_prefix='/download_book_covers')

@downloader_bp.route('/')
def download_book_covers():
    # look in the database for books with a remote_image_url, fetch one
    book = Book.query.filter(Book.remote_image_url.isnot(None)).first()
    if not book:
        return jsonify(message="No books with remote_image_url found"), 200
    url = book.remote_image_url
    if url == '':
        # broken remote image url, fix it
        book.remote_image_url = None
        db.session.commit()
        return jsonify(message="Book has no remote_image_url"), 200
    cover_image = download_cover_image(url)
    book.cover_image = cover_image
    book.remote_image_url = None
    db.session.commit()
    return jsonify({"message": "Cover image downloaded and saved."}), 200
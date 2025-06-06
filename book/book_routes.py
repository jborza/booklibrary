from flask import Blueprint, flash, jsonify, redirect, request, url_for
from authors.authors_tools import fill_author_data, get_author_by_name
from metadata.providers import PROVIDER_AMAZON, PROVIDER_FUNCTIONS, PROVIDER_GOODREADS, PROVIDER_GOOGLE, PROVIDER_OPENLIBRARY
from models import Author, Book, db
from thumbnails.thumbnails import download_cover_image
from sqlalchemy.orm import joinedload
book_bp = Blueprint('book', __name__, url_prefix='/book')

@book_bp.route('/api/<int:book_id>')
def book_detail_api(book_id):
    book = Book.query.options(joinedload(Book.author)).get_or_404(book_id)
    return jsonify(book.as_dict())

def fill_book_data(book: Book, data):
    # json to Book
    fields = {
        'title': 'title',
        'year': 'year_published',
        'isbn': 'isbn',
        'rating': 'rating',
        'book_type': 'book_type',
        'status': 'status',
        'genre': 'genre',
        'language': 'language',
        'synopsis': 'synopsis',
        'review': 'review',
        'pages': 'page_count',
        'series': 'series',
        'tags': 'tags',
        'page_count': 'page_count',
        # 'publisher': 'publisher',
        'cover_image': 'cover_image',
        'cover_image_tiny': 'cover_image_tiny',
        'notes': 'notes',
    }

    for key, attr in fields.items():
        if key in data and data[key] is not None:
            setattr(book, attr, data[key])

    return book

# TODO rename API method urls
@book_bp.route('/add_book_api', methods=['POST'])
def add_book_api():
    book = Book()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, no JSON body found"}), 400
    fill_book_data(book, data)
    # maybe author already exists
    author = get_author_by_name(data['author_name'].strip())
    # add the book to the author
    book.author = author
    db.session.add(book)
    db.session.commit()
    # add the cover image
    if 'cover_image' in data and data['cover_image'] is not None:
        download_thumbnail(book, data)
    return jsonify({'status': 'success', 'message': 'Book saved successfully', 'id':book.id}), 200

# TODO rename API method urls
@book_bp.route('/<int:book_id>/edit_api', methods=['POST'])
def edit_book_api(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, no JSON body found"}), 400
    # author data
    author = Author.query.filter_by(name=data['author_name']).first()
    if author is None:
        # create a new author
        author = Author()
        fill_author_data(author, data['author_name'])
        db.session.add(author)
        db.session.commit()
    fill_book_data(book, data)
    # sometimes the year is formatted like "2023-10-01", so we need to extract the year
    if isinstance(book.year_published, str) and '-' in book.year_published:
        book.year_published = book.year_published.split('-')[0]
    book.author = author
    # handle cover image URL
    if 'cover_image' in data and data['cover_image'] is not None and data['cover_image'].startswith('http'):
        download_thumbnail(book, data)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Book saved successfully'}), 200

def download_thumbnail(book, results):
    if 'cover_image' not in results:
        return False
    cover_image_url = results['cover_image']
    if cover_image_url is not None:
        if cover_image_url.startswith('http'):
            cover_image = download_cover_image(cover_image_url)
            # update the book object with the new cover image
            book.cover_image = cover_image
            db.session.commit()
            return True

def regenerate_thumbnail(provider, book_id):
    book = Book.query.get_or_404(book_id)
    # construct the search query
    query = f"{book.author_name} {book.title}"
    function = PROVIDER_FUNCTIONS.get(provider)
    results = function(query, count=1)

    result = download_thumbnail(book, results[0])
    if not result:
        return jsonify({'status': 'error', 'message': 'Thumbnail not found'}), 500
    return jsonify({'status': 'success', 'message': 'Thumbnail regenerated successfully'}), 200

@book_bp.route('/<int:book_id>/regenerate_thumbnail_openlibrary', methods=['POST'])
def regenerate_thumbnail(book_id):
    return regenerate_thumbnail(PROVIDER_OPENLIBRARY, book_id)

@book_bp.route('/<int:book_id>/regenerate_thumbnail_google', methods=['POST'])
def regenerate_thumbnail_google(book_id):
    return regenerate_thumbnail(PROVIDER_GOOGLE, book_id)

@book_bp.route('/<int:book_id>/regenerate_thumbnail_amazon', methods=['POST'])
def regenerate_thumbnail_amazon(book_id):
    return regenerate_thumbnail(PROVIDER_AMAZON, book_id)

@book_bp.route('/<int:book_id>/regenerate_thumbnail_goodreads', methods=['POST'])
def regenerate_thumbnail_goodreads(book_id):
    return regenerate_thumbnail(PROVIDER_GOODREADS, book_id)

# an API version - add provider
@book_bp.route('/<int:book_id>/match', methods=['GET'])
def match_book(book_id):
    book = Book.query.get_or_404(book_id)
    provider = request.args.get('provider', default=PROVIDER_GOOGLE, type=str)
    # construct the search query
    query = f"{book.author_name} {book.title}"
    function = PROVIDER_FUNCTIONS.get(provider)
    results = function(query, count=5)
    if len(results) == 0:
        flash("No results found", 'error')
        return redirect(url_for('book.book_detail', book_id=book.id))
    flash(f"Search completed", 'success')
    return jsonify(results)

@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Book deleted successfully'}), 200

# GET /books/<int:book_id>/collections — List collections for a book
@book_bp.route('/<int:book_id>/collections', methods=['GET'])
def get_collections_for_book(book_id):
    book = Book.query.get_or_404(book_id)
    collections = book.collections
    return jsonify([
        {"id": c.id, "name": c.name, "description": c.description}
        for c in collections
    ])
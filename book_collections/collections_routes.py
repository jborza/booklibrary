from flask import Blueprint, request, jsonify, abort
from models import db
from models import Book, Collection

collections_bp = Blueprint('collections', __name__, url_prefix='/collections')

# GET /collections — List all collections
@collections_bp.route('/', methods=['GET'])
def get_collections():
    collections = Collection.query.all()
    return jsonify([
        {"id": c.id, "name": c.name, "description": c.description}
        for c in collections
    ])

# POST /collections — Create new collection
@collections_bp.route('/', methods=['POST'])
def create_collection():
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description="Missing collection name")
    new_collection = Collection(
        name=data['name'],
        description=data.get('description')
    )
    db.session.add(new_collection)
    db.session.commit()
    return jsonify({"id": new_collection.id, "name": new_collection.name, "description": new_collection.description}), 201

# POST /collections/<int:collection_id>/books/<int:book_id> — Add book to collection
@collections_bp.route('/<int:collection_id>/books/<int:book_id>', methods=['POST'])
def add_book_to_collection(collection_id, book_id):
    collection = Collection.query.get_or_404(collection_id)
    book = Book.query.get_or_404(book_id)
    if book not in collection.books:
        collection.books.append(book)
        db.session.commit()
    return jsonify({"message": "Book added to collection."}), 200

# DELETE /collections/<int:collection_id>/books/<int:book_id> — Remove book from collection
@collections_bp.route('/<int:collection_id>/books/<int:book_id>', methods=['DELETE'])
def remove_book_from_collection(collection_id, book_id):
    collection = Collection.query.get_or_404(collection_id)
    book = Book.query.get_or_404(book_id)
    if book in collection.books:
        collection.books.remove(book)
        db.session.commit()
    return jsonify({"message": "Book removed from collection."}), 200

# TODO move to books_routes.py, meh
# GET /books/<int:book_id>/collections — List collections for a book
@collections_bp.route('/books/<int:book_id>/collections', methods=['GET'])
def get_collections_for_book(book_id):
    book = Book.query.get_or_404(book_id)
    collections = book.collections
    return jsonify([
        {"id": c.id, "name": c.name, "description": c.description}
        for c in collections
    ])
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

@collections_bp.route('/with_covers', methods=['GET'])
def get_collections_with_covers():
    collections = Collection.query.all()
    result = []
    for collection in collections:
        item = {'name': collection.name, 'id': collection.id, 'description': collection.description}

        book_ids_list = [book.id for book in collection.books]
        # grab all books in the collections
        cover_images = Book.query.where(Book.id.in_(book_ids_list)).with_entities(Book.cover_image).all()
        # replace empty cover image with default image
        item['cover_images'] = [r for (r, ) in cover_images]
        item['cover_images'] = [img if img else 'placeholder_book.png' for img in item['cover_images']]
        result.append(item)
    return jsonify(collections=result)

# POST /collections — Create new collection
@collections_bp.route('/create_api', methods=['POST'])
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

# add multiple books to collection
@collections_bp.route('/<int:collection_id>/add_books_api', methods=['POST'])
def add_books_to_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    data = request.get_json()
    if not data or 'book_ids' not in data:
        abort(400, description="Missing book IDs")

    book_ids = data['book_ids']
    books = Book.query.filter(Book.id.in_(book_ids)).all()

    for book in books:
        if book not in collection.books:
            collection.books.append(book)
    
    db.session.commit()
    return jsonify({"message": "Books added to collection."}), 200

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


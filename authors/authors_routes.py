from flask import Blueprint, jsonify, redirect, url_for
from models import Author

authors_bp = Blueprint('authors', __name__, url_prefix='/authors')


@authors_bp.route('/api')
def list_authors_api():
    query = Author.query.order_by(Author.surname_first).all()
    # take name and surname
    authors = [a.as_dict() for a in query]
    return jsonify(authors=authors)

@authors_bp.route('/<string:author_name>/api')
def author_books_api(author_name):
    # use search API like in library search
    return redirect(url_for('books.search_books', search_query=author_name))

# probably not needed
@authors_bp.route('/<string:author_name>')
def author_books(author_name):
    # TODO use search API like in library search
    return redirect(url_for('books.search_books', search_query=author_name))
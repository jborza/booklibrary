from flask import Blueprint, redirect, render_template, url_for
from models import Book

authors_bp = Blueprint('authors', __name__, url_prefix='/authors')

@authors_bp.route('/')
def list_authors():
    query = Book.query.with_entities(Book.author_name).distinct().order_by(Book.author_name).all()
    authors = [r for (r, ) in query]
    return render_template('authors.html', authors=authors)

@authors_bp.route('/<string:author_name>')
def author_books(author_name):
    # use search API like in library search
    return redirect(url_for('books.search_books', search_query=author_name))
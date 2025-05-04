from flask import Blueprint, render_template
from models import Book

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def list_books():
    books = Book.query.all()
    return render_template('books.html', books=books)
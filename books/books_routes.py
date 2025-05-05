import os
from pathlib import Path
from urllib.parse import urlparse
from flask import Blueprint, app, redirect, render_template, request
from models import Book, db
import requests
from PIL import Image
from book.thumbnails import make_tiny_cover_image, download_cover_image

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def list_books():
    books = Book.query.all()
    return render_template('books.html', books=books)


@books_bp.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author_name = request.form['author_name']
    year_published = request.form['year_published']
    isbn = request.form['isbn']
    genre = request.form['genre']
    language = request.form['language']
    synopsis = request.form['synopsis']
    cover_image_url = request.form['cover_image']

    # Download the cover image and save it to a local directory
    cover_image = download_cover_image(cover_image_url)
    cover_image_tiny = make_tiny_cover_image(cover_image)

    # Create a new book
    book = Book(
        title=title,
        author_name=author_name,
        year_published=year_published,
        book_type = None,
        status = None,
        rating = None,
        genre = genre,
        language=language,
        isbn=isbn,
        cover_image = cover_image,
        cover_image_tiny = cover_image_tiny,
    )
    db.session.add(book)

    db.session.commit()
    return redirect('/books/')


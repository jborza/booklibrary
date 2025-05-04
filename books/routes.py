import os
from pathlib import Path
from urllib.parse import urlparse
from flask import Blueprint, app, redirect, render_template, request
from models import Book, db
import requests

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def list_books():
    books = Book.query.all()
    return render_template('books.html', books=books)

def download_cover_image(cover_image_url):
    """
    Download the cover image from the given URL and save it to a local directory.
    
    Args:
        url (str): The URL of the cover image.
        
    Returns:
        str: The path to the saved image file.
    """
    try:
        response = requests.get(cover_image_url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Extract filename from URL
        parsed_url = urlparse(cover_image_url)
        filename = Path(parsed_url.path).name

        # Save the image to the 'covers' directory
        filepath = os.path.join('./static', 'covers', filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        cover_image = 'covers/' + filename  # Store relative path in DB
        return cover_image
    except requests.exceptions.RequestException as e:
        print(f"Error downloading cover image: {e}")
        return None

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

    # TODO Download the cover image and save it to a local directory
    cover_image = download_cover_image(cover_image_url)

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
        cover_image= cover_image
    )
    db.session.add(book)

    db.session.commit()
    return redirect('/books/')
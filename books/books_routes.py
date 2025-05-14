from flask import Blueprint, jsonify, redirect, render_template, request
from sqlalchemy import or_
from models import Book, db
from book.thumbnails import make_tiny_cover_image, download_cover_image

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def list_books():
    # parameters
    book_type = request.args.get('type')
    book_status = request.args.get('status')
    all_books = Book.query 
    filtered_books = all_books

    if book_type:
        filtered_books = filtered_books.filter_by(book_type=book_type)
    if book_status:
        filtered_books = filtered_books.filter_by(status=book_status)

    return render_template('books.html', books=filtered_books.all())

def add_cover_images(book_list : list):
    # Add a cover image URL for each book
    for book in book_list:
        if book['cover_image']:
            book['cover_image'] = book['cover_image']
        else:
            book['cover_image'] = 'placeholder_book.png'
            book['cover_image_tiny'] = 'placeholder_book_tiny.png'
    return book_list

@books_bp.route('/api')  # Use a separate route for the API
def list_books_json():
    # Parameters
    book_type = request.args.get('type')
    book_status = request.args.get('status')

    all_books = Book.query
    filtered_books = all_books

    if book_type:
        filtered_books = filtered_books.filter_by(book_type=book_type)
    if book_status:
        filtered_books = filtered_books.filter_by(status=book_status)

    # search by title by default
    filtered_books = filtered_books.order_by(Book.title)

    books = filtered_books.all()
    book_list = [book.as_dict() for book in books]
    # Add a cover image URL for each book
    add_cover_images(book_list)

    return jsonify(book_list), 200 

@books_bp.route('/search')
def search_books():
    query = request.args.get('search_query')
    if query:        
        books = Book.query.filter(Book.title.ilike(f'%{query}%')).all()
        # Search books by title, author, ISBN, or year
        books = Book.query.filter(
            or_(
                # Use ilike for case-insensitive search
                Book.title.ilike(f'%{query}%'),
                Book.author_name.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%'),
                Book.year_published.ilike(f'%{query}%')  
            )
        ).all()
    else:
        books = Book.query.all()
    return render_template('books.html', books=books, search_query=query)

@books_bp.route('/search_api')
def search_books_api():
    query = request.args.get('search_query')
    series = request.args.get('series')
    if query:
        # Search books by title, author, ISBN, or year or genre
        books = Book.query.filter(
            or_(
                # Use ilike for case-insensitive search
                Book.title.ilike(f'%{query}%'),
                Book.author_name.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%'),
                Book.year_published.ilike(f'%{query}%'),
                Book.genre.ilike(f'%{query}%')  
            )
        ).all()
    elif series:
        books = Book.query.filter(Book.series.ilike(f'%{series}%')).all()
    else:
        books = Book.query.all()
    book_list = [book.as_dict() for book in books]
    add_cover_images(book_list)

    return jsonify(book_list), 200 


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
        synopsis=synopsis,
        cover_image = cover_image,
        cover_image_tiny = cover_image_tiny,
    )
    db.session.add(book)

    db.session.commit()
    return redirect('/books/')

@books_bp.route('/add_book_api', methods=['POST'])
def add_book_api():
    # Parse the JSON payload
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Extract fields from the JSON payload
    title = data.get('title')
    author_name = data.get('author_name')
    year_published = data.get('year_published')
    isbn = data.get('isbn')
    genre = data.get('genre')
    language = data.get('language')
    synopsis = data.get('synopsis')
    cover_image_url = data.get('cover_image')

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
        synopsis=synopsis,
        cover_image = cover_image,
        cover_image_tiny = cover_image_tiny,
    )
    db.session.add(book)

    db.session.commit()
    return jsonify(book.as_dict()), 201

@books_bp.route('/api/byid', methods=['GET'])
def list_books_by_ids():
    ids_to_filter = request.args.get('ids', '')

    if ids_to_filter:
        # Filter books by IDs
        ids_to_filter = [int(id) for id in ids_to_filter.split(',')]
        existing_books = Book.query.filter(Book.id.in_(ids_to_filter)).all()
        return jsonify([book.as_dict() for book in existing_books])
    else:
        return jsonify({"error": "No IDs provided"}), 400


from flask import Blueprint, jsonify, redirect, render_template, request
from sqlalchemy import func, or_, select
from books.filters import BookFilter
from models import Book, db
from book.thumbnails import make_tiny_cover_image, download_cover_image
from dataclasses import dataclass

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

def add_cover_images_tiny(book_list : list):
    # Add a cover image URL for each book
    for book in book_list:
        if not book['cover_image_tiny']:
            book['cover_image_tiny'] = 'placeholder_book_tiny.png'
    return book_list

@books_bp.route('/api/authors', methods=['GET'])
def list_authors():
    # TODO add filters
    book_type = request.args.get('type')
    book_status = request.args.get('status')
    search = request.args.get('search')
    filter = BookFilter(
        search=search,
        book_type=book_type,
        book_status=book_status,
        # TODO add other filters
    )
    authors = get_authors(db.session, filter)
    return jsonify(authors), 200

def get_authors(session, filters: dict):
    """
    Get a list of authors based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A list of authors
    """
    query = session.query(Book.author_name).order_by(Book.author_name).distinct()
    # TODO Apply filters to the query
    result = query.all()
    # Convert result to a list of author names
    authors = [author[0] for author in result]
    return authors

def get_genres(session, filters: BookFilter):
    """
    Get a list of genres based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A list of genres
    """
    query = session.query(Book.genre).order_by(Book.genre).distinct()
    query = filter_books(query, filters)
    result = query.all()
    # Convert result to a list of genre names
    genres = [genre[0] for genre in result]
    # remove the None values
    genres = [g for g in genres if g is not None]
    # split the genres if they are comma separated
    genres = [g.strip() for genre in genres for g in genre.split(',')]
    return genres

def get_langages(session, filters: BookFilter):
    """
    Get a list of languages based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A list of languages
    """
    query = session.query(Book.language).order_by(Book.language).distinct()
    query = filter_books(query, filters)
    result = query.all()
    # Convert result to a list of language names
    languages = [language[0] for language in result]
    # remove the None values
    languages = [l for l in languages if l is not None]
    # split the genres if they are comma separated
    languages = [l.strip() for lang in languages for l in lang.split(',')]
    # remove duplicates
    languages = list(set(languages))
    languages.sort()
    return languages

def get_series(session, filters: BookFilter):
    """
    Get a list of series based on filters.

    :param session: SQLAlchemy session
    :return: A list of series
    """
    query = session.query(Book.series).order_by(Book.series).distinct()
    query = filter_books(query, filters)
    result = query.all()
    # Convert result to a list of series names
    series = [s[0] for s in result]
    # remove the None values
    series = [s for s in series if s is not None]
    return series

def get_count(session, filters: BookFilter):
    """
    Get the count of books based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A dictionary containing the count of books
    """
    query = session.query(func.count(Book.id).label("count"))
    query = filter_books(query, filters)
    # TODO Apply filters to the query
    result = query.one()
    return result.count

def get_min_max_values(session, filters: BookFilter):
    """
    Get minimum and maximum values for page_count, year, and rating based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A dictionary containing min/max values for page_count, year, and rating
    """
    query = session.query(
        func.min(Book.page_count).label("min_page_count"),
        func.max(Book.page_count).label("max_page_count"),
        func.min(Book.year_published).label("min_year"),
        func.max(Book.year_published).label("max_year"),
        func.min(Book.rating).label("min_rating"),
        func.max(Book.rating).label("max_rating")
    )
    query = filter_books(query, filters)
    result = query.one()
    return {
        "page_count": {"min": result.min_page_count, "max": result.max_page_count},
        "year": {"min": result.min_year, "max": result.max_year},
        "rating": {"min": result.min_rating, "max": result.max_rating},
    }

def filter_books(query, filter: BookFilter):
    if filter.book_type:
        query = query.filter_by(book_type=filter.book_type)
    if filter.book_status:
        query = query.filter_by(status=filter.book_status)

    if filter.search:
        # Search books by title, author, ISBN, or year
        search = filter.search.lower()
        query = query.filter(
            or_(
                # Use ilike for case-insensitive search
                Book.title.ilike(f'%{search}%'),
                Book.author_name.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%'),
                Book.year_published.ilike(f'%{search}%')
            )
        )
    return query

@books_bp.route('/api')  # Use a separate route for the API
def list_books_json():
    # Parameters
    book_type = request.args.get('type')
    book_status = request.args.get('status')
    page_size = int(request.args.get('page_size'))
    page = int(request.args.get('page'))
    search = request.args.get('search')
    filter = BookFilter(
        search=search,
        book_type=book_type,
        book_status=book_status,
        # TODO add other filters
    )


    # skip some columns
    excluded_columns = {'synopsis', 'cover_thumbnail', 'review', 'tags', 'genre', 'language', 'cover_image', 'page_count'}

    # Dynamically include only the columns that are NOT in the excluded list
    columns_to_select = [column for column in Book.__table__.columns if column.name not in excluded_columns]

    # Create a query and select the columns
    query = select(*columns_to_select)
    # search by title by default
    query = query.order_by(Book.title)
    # filter by book type and status
    query = filter_books(query, filter)

    # just the first 'count' books
    offset = page_size * (page - 1)
    print('offset', offset, ' page_size', page_size)
    query = query.offset(offset).limit(page_size)
    # query = query.limit(count)
    # Execute the query
    results = db.session.execute(query).all()

    # Convert results to dictionaries
    all_books = [
        {column.name: value for column, value in zip(columns_to_select, row)}
        for row in results
    ]

    # get the min/max value for page count, year, rating
    # TODO add filters to all
    minmax = get_min_max_values(db.session, filter)
    genres = get_genres(db.session, filter)
    languages = get_langages(db.session, filter)
    series = get_series(db.session, filter)
    count = get_count(db.session, filter)

    # Add a cover image URL for each book
    add_cover_images_tiny(all_books)
    result = {'books': all_books,
              'minmax': minmax,
              'genres': genres,
              'languages': languages,
              'series': series,
              'count': count
              }

    return jsonify(result), 200

@books_bp.route('/search')
def search_books():
    query = request.args.get('search_query')
    if query:        
        # books = Book.query.filter(Book.title.ilike(f'%{query}%')).all()
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


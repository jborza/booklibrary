from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from authors.authors_tools import capitalize_name, get_author_by_name
from book.book_tools import format_title
from books.filters import BookFilter
from books.search_options import NONE_OPTION
from metadata.google_books import get_googlebooks_data
from metadata.openlibrary import get_openlibrary_data_api
from models import Author, Book, db
from thumbnails.thumbnails import make_tiny_cover_image, download_cover_image

books_bp = Blueprint("books", __name__, url_prefix="/books")


def add_cover_images(book_list: list):
    # Add a cover image URL for each book
    for book in book_list:
        if book["cover_image"]:
            book["cover_image"] = book["cover_image"]
        else:
            book["cover_image"] = "placeholder_book.png"
            book["cover_image_tiny"] = "placeholder_book_tiny.png"
    return book_list


def add_cover_images_tiny(book_list: list):
    # Add a cover image URL for each book
    for book in book_list:
        if not book["cover_image_tiny"]:
            book["cover_image_tiny"] = "placeholder_book_tiny.png"
    return book_list


@books_bp.route("/api/authors", methods=["GET"])
def list_authors():
    book_type = request.args.get("type")
    book_status = request.args.get("status")
    search = request.args.get("search")
    author = request.args.get("author")
    genre = request.args.get("genre")
    language = request.args.get("language")
    series = request.args.get("series")
    pages_min = request.args.get("pages_min")
    pages_max = request.args.get("pages_max")
    year_min = request.args.get("year_min")
    year_max = request.args.get("year_max")
    rating_min = request.args.get("rating_min")
    rating_max = request.args.get("rating_max")
    collection = request.args.get("collection")
    filter = BookFilter(
        search=search,
        book_type=book_type,
        book_status=book_status,
        author=author,
        genre=genre,
        language=language,
        series=series,
        rating_min=rating_min,
        rating_max=rating_max,
        pages_min=pages_min,
        pages_max=pages_max,
        year_min=year_min,
        year_max=year_max,
        collection=collection,
    )
    authors = get_authors(db.session, filter)
    return jsonify(authors), 200


def get_authors(session, filters: BookFilter):
    """
    Get a list of authors based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A list of authors
    """

    query = session.query(Author.name).join(Book).order_by(Author.name).distinct()

    query = filter_books(query, filters)

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
    query = session.query(Book.genre, Author.name).join(Author)
    query = query.order_by(Book.genre).distinct()
    query = filter_books(query, filters)
    result = query.all()
    # Convert result to a list of genre names
    genres = [genre[0] for genre in result]
    # remove the None values
    genres = [g for g in genres if g is not None]
    # split the genres if they are comma separated
    genres = [g.strip() for genre in genres for g in genre.split(",")]
    # remove duplicates
    genres = list(set(genres))
    genres.sort()
    return genres


def get_langages(session, filters: BookFilter):
    """
    Get a list of languages based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A list of languages
    """
    query = session.query(Book.language, Author.name).join(Author).order_by(Book.language).distinct()
    query = filter_books(query, filters)
    result = query.all()
    # Convert result to a list of language names
    languages = [language[0] for language in result]
    # remove the None values
    languages = [l for l in languages if l is not None]
    # split the genres if they are comma separated
    languages = [l.strip() for lang in languages for l in lang.split(",")]
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
    query = session.query(Book.series, Author.name).join(Author).order_by(Book.series).distinct()
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
    query = query.join(Author)
    query = filter_books(query, filters)
    result = query.one()
    return result.count


def get_min_max_values(session, filters: BookFilter):
    """
    Get minimum and maximum values for page_count, year, and rating based on filters.

    :param session: SQLAlchemy session
    :param filters: Dictionary containing filters (e.g., genre, author, etc.)
    :return: A dictionary containing min/max values for page_count, year, and rating
    """
    # TODO add Authors
    query = session.query(
        func.min(Book.page_count).label("min_page_count"),
        func.max(Book.page_count).label("max_page_count"),
        func.min(Book.year_published).label("min_year"),
        func.max(Book.year_published).label("max_year"),
        func.min(Book.rating).label("min_rating"),
        func.max(Book.rating).label("max_rating"),
    )
    query = query.join(Author)
    query = filter_books(query, filters)
    result = query.one()
    return {
        "page_count": {"min": result.min_page_count, "max": result.max_page_count},
        "year": {"min": result.min_year, "max": result.max_year},
        "rating": {"min": result.min_rating, "max": result.max_rating},
    }


def filter_books(query, filter: BookFilter):
    if filter.book_type:
        if filter.book_type == NONE_OPTION:
            query = query.filter(Book.book_type.is_(None))
        else:
            query = query.filter(Book.book_type == filter.book_type)
    if filter.book_status:
        if filter.book_status == NONE_OPTION:
            query = query.filter(Book.status.is_(None))
        else:
            query = query.filter(Book.status == filter.book_status)

    if filter.search:
        # Search books by title, author, ISBN, or year
        search = filter.search.lower()
        query = query.filter(
            or_(
                # Use ilike for case-insensitive search
                Book.title.ilike(f"%{search}%"),
                Author.name.ilike(f"%{search}%"),
                Book.isbn.ilike(f"%{search}%"),
                Book.year_published.ilike(f"%{search}%"),
            )
        )
    if filter.author:
        query = query.filter(Author.name.ilike(f"%{filter.author}%"))
    if filter.genre:
        if filter.genre == NONE_OPTION:
            query = query.filter(Book.genre.is_(None))
        else:
            query = query.filter(Book.genre.ilike(f"%{filter.genre}%"))
    if filter.language:
        if filter.language == NONE_OPTION:
            query = query.filter(Book.language.is_(None))
        else:
            query = query.filter(Book.language.ilike(f"%{filter.language}%"))
    if filter.series:
        if filter.series == NONE_OPTION:
            query = query.filter(Book.series.is_(None))
        else:
            query = query.filter(Book.series.ilike(f"%{filter.series}%"))
    # rating, pages, year
    if filter.rating_min:
        query = query.filter(Book.rating >= filter.rating_min)
    if filter.rating_max:
        query = query.filter(Book.rating <= filter.rating_max)
    if filter.pages_min:
        query = query.filter(Book.page_count >= filter.pages_min)
    if filter.pages_max:
        query = query.filter(Book.page_count <= filter.pages_max)
    if filter.year_min:
        query = query.filter(Book.year_published >= filter.year_min)
    if filter.year_max:
        query = query.filter(Book.year_published <= filter.year_max)
    if filter.collection:
        # Filter by collection
        query = query.join(Book.collections).filter(Book.collections.any(id=filter.collection))

    return query


@books_bp.route("/api")  # Use a separate route for the API
def list_books_json():
    # Parameters
    book_type = request.args.get("type")
    book_status = request.args.get("status")
    if "page_size" in request.args:
        page_size = int(request.args.get("page_size"))
    else:
        page_size = 50
    if "page" in request.args:
        page = int(request.args.get("page"))
    else:
        page = 1
    search = request.args.get("search")
    author = request.args.get("author")
    genre = request.args.get("genre")
    language = request.args.get("language")
    series = request.args.get("series")
    pages_min = request.args.get("pages_min")
    pages_max = request.args.get("pages_max")
    year_min = request.args.get("year_min")
    year_max = request.args.get("year_max")
    rating_min = request.args.get("rating_min")
    rating_max = request.args.get("rating_max")
    sort_ascending = request.args.get("sort_ascending")
    sort_column = request.args.get("sort_column")
    if not sort_column:
        sort_column = 'title'
    collection = request.args.get("collection")
    filter = BookFilter(
        search=search,
        book_type=book_type,
        book_status=book_status,
        author=author,
        genre=genre,
        language=language,
        series=series,
        rating_min=rating_min,
        rating_max=rating_max,
        pages_min=pages_min,
        pages_max=pages_max,
        year_min=year_min,
        year_max=year_max,
        collection=collection,
    )

    # skip some columns
    book_columns = [
        "id",
        "title",
        "year_published",
        "rating",
        "book_type",
        "status",
        "cover_image",
        "cover_image_tiny",
        "genre",
        "page_count",
        "language",
        "publisher",
        "isbn",
        "series"
    ]
    author_columns = ["name", "surname_first"]
    query = Book.query.join(Author)
    sort_column_sqlalchemy = getattr(Book, sort_column, None)
    if sort_column in ['surname_first']:
        sort_column_sqlalchemy = getattr(Author, sort_column, None)
    if sort_ascending == "true":
        query = query.order_by(sort_column_sqlalchemy)
    else:
        query = query.order_by(sort_column_sqlalchemy.desc())
    # filter by book type and status
    query = filter_books(query, filter)

    # just the first 'count' books
    offset = page_size * (page - 1)
    query = query.offset(offset).limit(page_size)
    # Execute the query
    results = db.session.execute(query).all()

    # Convert results to dictionaries
    all_books = []
    for row in results:
        book = row.Book
        data = {col: getattr(book, col) for col in book_columns}
        author = book.author
        for acol in author_columns:
            data[f"author_{acol}"] = getattr(author, acol, None)
        all_books.append(data)

    # get the min/max value for page count, year, rating
    minmax = get_min_max_values(db.session, filter)
    genres = get_genres(db.session, filter)
    languages = get_langages(db.session, filter)
    series = get_series(db.session, filter)
    count = get_count(db.session, filter)

    # Add a cover image URL for each book
    add_cover_images(all_books)
    add_cover_images_tiny(all_books)
    result = {
        "books": all_books,
        "minmax": minmax,
        "genres": genres,
        "languages": languages,
        "series": series,
        "count": count,
    }

    return jsonify(result), 200


@books_bp.route("/search_api")
def search_books_api():
    query = request.args.get("search_query")
    series = request.args.get("series")
    if query:
        # Search books by title, author, ISBN, or year or genre
        books = (
            Book.query.join(Author)
            .filter(
                or_(
                    # Use ilike for case-insensitive search
                    Book.title.ilike(f"%{query}%"),
                    Author.name.ilike(f"%{query}%"),
                    Book.isbn.ilike(f"%{query}%"),
                    Book.year_published.ilike(f"%{query}%"),
                    Book.genre.ilike(f"%{query}%"),
                )
            )
            .order_by(Book.title)
            .all()
        )
    elif series:
        books = Book.query.join(Author).filter(Book.series.ilike(f"%{series}%")).order_by(Book.title).all()
    else:
        books = Book.query.join(Author).order_by(Book.title).all()
    book_list = [book.as_dict() for book in books]
    add_cover_images(book_list)

    return jsonify(book_list), 200

@books_bp.route("/add_book_api", methods=["POST"])
def add_book_api():
    # Parse the JSON payload
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Extract fields from the JSON payload
    title = data.get("title")
    author_name = data.get("author_name")
    year_published = data.get("year_published")
    isbn = data.get("isbn")
    genre = data.get("genre")
    language = data.get("language")
    synopsis = data.get("synopsis")
    cover_image_url = data.get("cover_image")

    # Download the cover image and save it to a local directory
    cover_image = download_cover_image(cover_image_url)
    cover_image_tiny = make_tiny_cover_image(cover_image)

    # Create a new book
    book = Book(
        title=title,
        author_name=author_name,
        year_published=year_published,
        book_type=None,
        status=None,
        rating=None,
        genre=genre,
        language=language,
        isbn=isbn,
        synopsis=synopsis,
        cover_image=cover_image,
        cover_image_tiny=cover_image_tiny,
    )
    db.session.add(book)

    db.session.commit()
    return jsonify(book.as_dict()), 201


@books_bp.route("/api/byid", methods=["GET"])
def list_books_by_ids():
    ids_to_filter = request.args.get("ids", "")

    if ids_to_filter:
        # Filter books by IDs
        ids_to_filter = [int(id) for id in ids_to_filter.split(",")]
        existing_books = Book.query.filter(Book.id.in_(ids_to_filter)).all()
        return jsonify([book.as_dict() for book in existing_books])
    else:
        return jsonify([])  # no IDs provided

@books_bp.route("/delete_books_api", methods=["POST"])
def delete_books_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    book_ids = data.get("book_ids", [])
    if not book_ids:
        return jsonify({"error": "No book IDs provided"}), 400
    # Loop through the book IDs and update each book
    for book_id in book_ids:
        # Find the book by ID
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": f"Book with ID {book_id} not found"}), 404
        # Delete the book
        db.session.delete(book)
    # Commit the changes to the database
    db.session.commit()
    return jsonify({"status": "success", "message": "Books deleted successfully"}), 200
    

@books_bp.route("/update_books_api", methods=["POST"])
def update_books_api():
    # Parse the JSON payload
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    book_ids = data.get("book_ids", [])
    if not book_ids:
        return jsonify({"error": "No book IDs provided"}), 400
    items = data.get("data", [])
    if not items:
        return jsonify({"error": "No data provided"}), 400
    # Loop through the book IDs and update each book
    for book_id in book_ids:
        # Find the book by ID
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": f"Book with ID {book_id} not found"}), 404

        # Update the book's attributes
        for key, value in items.items():
            setattr(book, key, value)

        # update author
        if "author_name" in items:
            author = get_author_by_name(items['author_name'].strip())
            book.author = author


        # Commit the changes to the database
        db.session.commit()

    return jsonify({"status": "success", "message": "Books updated successfully"}), 200

@books_bp.route("/match_books_api", methods=["POST"])
def match_books():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    book_ids = data.get("book_ids", [])
    if not book_ids:
        return jsonify({"error": "No book IDs provided"}), 400
    match_metadata = data.get("match_metadata", False)
    match_covers = data.get("match_covers", False)
    if not match_metadata and not match_covers:
        return jsonify({"error": "No matching criteria provided"}), 400
    provider = data.get("provider", "google_books")
    if provider not in ["google_books", "openlibrary"]:
        return jsonify({"error": "Invalid provider"}), 400
    
    # Loop through the book IDs and update each book
    for book_id in book_ids:
        print('Matching book with ID:', book_id)
        # Find the book by ID
        book = Book.query.filter(Book.id == book_id).join(Author).first()
        if not book:
            return jsonify({"error": f"Book with ID {book_id} not found"}), 404
        # ping search API with 1 result
        if provider == "google_books":
            results = get_googlebooks_data(f"{book.author.name} {book.title}", count=1)
        else:
            results = get_openlibrary_data_api(f"{book.author.name} {book.title}", count=1)
        # Download the cover image and save it to a local directory
        result = results[0] if results else None
        if match_covers:
            if not result or 'cover_image' not in result:
                return jsonify({"error": f"No cover image found for book {book_id}"}), 404
            cover_image_url = result['cover_image']
            if cover_image_url:
                cover_image = download_cover_image(cover_image_url)
                book.cover_image = cover_image
                book.cover_image_tiny = make_tiny_cover_image(cover_image)
        if match_metadata:
            if result:
                # Update author if author_name is provided
                name = result.get('author_name', book.author.name)
                name = capitalize_name(name) 
                if name != book.author.name:
                    # for now, skip if the name changed, we probably got something completely different by suggestions
                    continue                    
                book.title = result.get('title', book.title)
                book.title = format_title(book.title)  # Ensure title is formatted correctly
                book.language = result.get('language', book.language)
                book.year_published = result.get('year_published', book.year_published)
                book.synopsis = result.get('synopsis', book.synopsis)
                book.page_count = result.get('page_count', book.page_count)
                book.isbn = result.get('isbn', book.isbn)
                book.genre = result.get('genre', book.genre)
                book.publisher = result.get('publisher', book.publisher)
                book.rating = result.get('rating', book.rating)
                # fix year_published if it's like '2020-01-01'
                if book.year_published and isinstance(book.year_published, str):
                    try:
                        book.year_published = int(book.year_published.split('-')[0])
                    except ValueError:
                        book.year_published = None
           
                              
        db.session.commit()
    return jsonify({"status": "success", "message": "Books matched successfully"}), 200
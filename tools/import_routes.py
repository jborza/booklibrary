import csv
from io import StringIO
import itertools
import re
from flask import Blueprint, jsonify, request
from authors.authors_tools import extract_main_author, get_author_by_name
from book.book_types import AUDIOBOOK, EBOOK, PHYSICAL
from book_tools import extract_genres, extract_isbn, extract_status, extract_year
from genres.genres_db import get_genres_ids
from models import Author, Book, OtherBook, db
from dataclasses import dataclass
import_bp = Blueprint('import', __name__, url_prefix='/import')


@dataclass
class BookImport:
    title: str
    author_name: str
    book_type: str = None
    status: str = None
    rating: float = None
    genre: str = None
    isbn: str = None
    existing_book: bool = False
    existing_book_id: int = None
    synopsis: str = None
    page_count: int = None
    year_published: int = None
    series: str = None
    cover_image: str = None
    language: str = None

class DictToClass:
    def __init__(self, **entries):
        self.__dict__.update(entries)



def update_book_fields(result, book: Book):
    book.title = result['title']
    book.author_name = result['author_name']
    if 'year' in result:
        book.year_published = result['year']
    if 'year_published' in result:
        book.year_published = result['year_published']
    if 'isbn' in result: 
        book.isbn = result['isbn']
    if 'book_type' in result:
        book.book_type = result['book_type']
    if 'status' in result:
        book.status = result['status']
    if 'rating' in result:
        book.rating = result['rating']
    if 'genre' in result:
        book.genre = result['genre']
    if 'language' in result:
        book.language = result['language']
    if 'synopsis' in result:
        book.synopsis = result['synopsis']
    if 'series' in result:
        book.series = result['series']
    if 'tags' in result:
        book.tags = result['tags']
    if 'page_count' in result:
        book.page_count = result['page_count']
    if 'cover_image' in result:
        book.remote_image_url = result['cover_image']
    if 'language' in result:
        book.language = result['language']
    if 'status' in result:
        book.status = result['status']


def lower_first(iterator):
    return itertools.chain([next(iterator).lower()], iterator)

@import_bp.route('/import_csv_api', methods=['POST'])
def import_csv_api():
    if request.method != 'POST':
        return jsonify({'status': 'error', 'message': 'Invalid request method'}), 405

    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    csv_file = request.files['file']
    if csv_file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    if csv_file:
        try:
            csv_text = csv_file.read().decode('utf-8')
            csv_data = StringIO(csv_text)
            reader = csv.DictReader(lower_first(csv_data))
            imported_count = 0
            import_books = []

            for row in reader:
                import_book = BookImport(title=None, author_name=None)

                title = row.get('title')
                author_name = row.get('author')
                author_name = extract_main_author(author_name)
                isbn = row.get('isbn')
                isbn13 = row.get('isbn13')
                isbn = extract_isbn(isbn, isbn13)

                average_rating = row.get('average rating')
                if not average_rating:
                    average_rating = row.get('rating')
                number_of_pages = row.get('number of pages')
                if not number_of_pages:
                    number_of_pages = row.get('pages')
                # extract just the number from there
                if number_of_pages:
                    try:
                        match = re.search(r'\d+', number_of_pages)
                        if match:
                            number_of_pages = match.group(0)
                    except Exception:
                        pass
                year_published = extract_year(row)

                bookshelves = row.get('bookshelves')
                description = row.get('description')
                language = row.get('language')
                
                series = row.get('series')
                # if series is in the format "Series Name #1", extract the name
                if series:
                    series = series.split('#')[0].strip()
                cover_image = row.get('coverimg')
                genres = row.get('genres')
                genres = extract_genres(genres)

                # Check for required fields
                if not all([title, author_name]):
                    print(f"Skipping row with missing data: {row}")
                    continue

                # Convert data types
                try:
                    average_rating = float(average_rating) if average_rating else None
                    number_of_pages = int(number_of_pages) if number_of_pages else None
                    year_published = int(year_published) if year_published else None
                except (ValueError, TypeError) as e:
                    print(f"Skipping row due to invalid data: {row} - {e}")
                    continue
                
                status = extract_status(bookshelves)

                existing_book = (
                    Book.query
                    .join(Author)
                    .filter(Book.title.ilike(title))
                    .filter(Author.name.ilike(author_name))
                    .first()  # Retrieve the first matching book
                )
                if existing_book:
                    import_book.existing_book = True
                    import_book.existing_book_id = existing_book.id

                import_book.title = title
                import_book.author_name = author_name
                import_book.book_type = EBOOK
                import_book.year_published = year_published
                import_book.isbn = isbn
                import_book.rating = average_rating
                import_book.page_count = number_of_pages
                import_book.status = status
                import_book.synopsis = description
                import_book.series = series
                import_book.cover_image = cover_image
                import_book.genre = genres
                import_book.language = language
                import_books.append(import_book)
                imported_count += 1
            return jsonify({'status': 'success', 'import_books': import_books}), 200
        except Exception as e:
            print(f"Error processing CSV file: {e}")
            return jsonify({'status': 'error', 'message': 'Error processing CSV file'}), 500


@import_bp.route('/import_notes_api', methods=['POST'])
def import_notes_api():
    if request.method != 'POST':
        return jsonify({'status': 'error', 'message': 'Invalid request method'}), 405
    # data in request.form - notes, importFormat
    notes_data = request.form['notes']
    # can be either authorTitle or titleAuthor
    # TODO use this!!!
    importFormat = request.form['importFormat']
    AUTHORTITLE = 'authorTitle'
    TITLEAUTHOR = 'titleAuthor'
    # Process the notes data as needed
    lines = notes_data.splitlines()
    imported_count = 0
    # list of BookImport objects
    import_books = []
    for line in lines:
        import_book = BookImport(title=None, author_name=None)
        # Try both formats: "title - author" and "title (author)"
        # markdown lines begin with a dash
        if line.startswith("- "):
            line = line[2:]
        # Check if the line contains " - " or " (" and ")" to separate title and author
        if " - " in line:
            split = line.split(" - ")
            if importFormat == AUTHORTITLE:
                title, author_name = split[1], split[0]
            else:
                title, author_name = split[0], split[1]
        elif " (" in line and ")" in line:
            title = line[:line.index(" (")]
            author_name = line[line.index(" (") + 2:line.index(")")]
        else:
            # Skip lines that don't match either format
            print(f"Skipping invalid line: {line}")
            continue
        # there can be the book format in the line
        format = None
        if "pdf" in line:
            format = EBOOK
        elif "epub" in line:
            format = EBOOK
        elif "mobi" in line:
            format = EBOOK
        elif "physical" in line:
            format = PHYSICAL
        elif "audiobook" in line:
            format = AUDIOBOOK
        # remove the format from the title
        title = title.replace("pdf", "").replace("epub", "").replace("mobi","").replace("physical", "").replace("audiobook", "")
        # also from the author name
        author_name = author_name.replace("pdf", "").replace("epub", "").replace("mobi","").replace("physical", "").replace("audiobook", "")

        title = title.strip()
        author_name = author_name.strip()

        # Check if the book already exists in the database
        existing_book = (
            Book.query
            .join(Author)  
            .filter(Book.title.ilike(title))
            .filter(Author.name.ilike(author_name)) 
            .first()  # Retrieve the first matching book
        )
        if existing_book:
            import_book.existing_book = True
            import_book.existing_book_id = existing_book.id

        import_book.title = title
        import_book.author_name = author_name
        import_book.book_type = format
        import_books.append(import_book)
        imported_count += 1

    # Redirect to the import details page
    return jsonify({'status': 'success', 'import_books': import_books}), 200


@import_bp.route('/confirm_import_api', methods=['POST'])
def confirm_import_api():
    if request.method != 'POST':
        return jsonify({'status': 'error', 'message': 'Invalid request method'}), 405
    import_books = request.json

    for i, result in enumerate(import_books):
        action = 'add'  # default action is to add a new book
        if 'action' in result:
            action = result['action']
        if action == f'merge':
            # Find existing book by id
            existing_book = Book.query.get(result['existing_book_id'])

            if existing_book:
                # Update existing book
                update_book_fields(result, existing_book)
                author = get_author_by_name(result['author_name'].strip())
                existing_book.author = author
        else:
            # Create a new book
            author = get_author_by_name(result['author_name'].strip())
            new_book = Book()
            new_book.author = author
            # add other fields if added
            update_book_fields(result, new_book)
            db.session.add(new_book)

        db.session.commit()

    return jsonify({'status': 'success', 'message': 'Books imported successfully'}), 200

# Other (all) books import
# TODO refactor
@import_bp.route('/import_csv_all_api', methods=['POST'])
def import_csv_all_api():
    if request.method != 'POST':
        return jsonify({'status': 'error', 'message': 'Invalid request method'}), 405

    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    csv_file = request.files['file']
    if csv_file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    if csv_file:
        try:
            csv_text = csv_file.read().decode('utf-8')
            csv_data = StringIO(csv_text)
            reader = csv.DictReader(lower_first(csv_data))
            imported_count = 0

            for row in reader:
                title = row.get('title')
                if len(title) > 190:
                    # truncate title to 190 characters
                    title = title[:190] + "..."
                author_name = row.get('author')
                author_name = extract_main_author(author_name)
                isbn = row.get('isbn')
                isbn13 = row.get('isbn13')
                isbn = extract_isbn(isbn, isbn13)

                average_rating = row.get('average rating')
                if not average_rating:
                    average_rating = row.get('rating')
                year_published = extract_year(row)

                description = row.get('description')
                # shorten to 300 characters
                if description and len(description) > 300:
                    description = description[:300] + '...'
                genres = row.get('genres')
                genres = extract_genres(genres)
                language = row.get('language')
                # if language has commas, split it and take the first one
                if language and ',' in language:
                    language = language.split(',')[0].strip()
                if language and ';' in language:
                    language = language.split(';')[0].strip()
                # strip to 20 characters
                if language and len(language) > 20:
                    language = language[:20]

                # Check for required fields
                if not all([title, author_name]):
                    print(f"Skipping row with missing data: {row}")
                    continue

                # Convert data types
                try:
                    average_rating = float(average_rating) if average_rating else None
                    year_published = int(year_published) if year_published else None
                except (ValueError, TypeError) as e:
                    print(f"Skipping row due to invalid data: {row} - {e}")
                    continue
                
                book = None
                existing_book = (
                    OtherBook.query
                    .join(Author)
                    .filter(OtherBook.title.ilike(title))
                    .filter(Author.name.ilike(author_name))
                    .first()  # Retrieve the first matching book
                )
                if existing_book:
                    book = existing_book
                else:
                    # Create a new book
                    book = OtherBook()
                    author = get_author_by_name(author_name.strip())
                    book.author = author
                    db.session.add(book)

                book.title = title
                book.book_type = EBOOK
                book.year_published = year_published
                book.isbn = isbn
                book.rating = average_rating
                book.synopsis = description
                book.language = language
                # push in genres
                book.genre = genres
                genre_ids = get_genres_ids(genres)
                book.genre_ids = ','.join(map(str, genre_ids))
                imported_count += 1
            db.session.commit()
            return jsonify({'status': f'success, imported {imported_count} books'}), 200
        except Exception as e:
            print(f"Error processing CSV file: {e}")
            return jsonify({'status': 'error', 'message': 'Error processing CSV file'}), 500
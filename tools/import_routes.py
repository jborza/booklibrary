import csv
from datetime import datetime
from io import StringIO
import itertools
import re
from flask import Blueprint, json, jsonify, request
from authors.authors_tools import extract_main_author, get_author_by_name
from book.book_status import WISHLIST, CURRENTLY_READING, TO_READ, READ
from book.book_types import AUDIOBOOK, EBOOK, PHYSICAL
from models import Author, Book, db
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
                # prefer isbn13 if both are present
                if isbn and isbn13:
                    isbn = isbn13
                # goodreads isbn format looks like '="9781604865301"' - extract the value
                match = re.search(r'"(\d+)"', isbn)
                if match:
                    isbn = match.group(1)
                # sometimes isbn stays like ="" - in this case it's empty
                if isbn == '=""':
                    isbn = None
                # sometimes it's 9999999999999 - remove it
                if isbn == '9999999999999':
                    isbn = None

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
                year_published = row.get('year published')
                # or publishDate?
                if year_published == None:
                    year_published = row.get('publishdate')
                # sometimes it says just 'Published' - take other column
                if year_published == 'Published':
                    year_published = row.get('firstpublishdate')



                # it could be in this format: 09/14/08
                try:
                    date = datetime.strptime(year_published, '%m/%d/%y')
                    year_published = date.year
                except ValueError:
                    pass
                # it could also be in this format: July 7th 2013
                if isinstance(year_published, str):
                    try:
                        date_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', year_published)
                        dt = datetime.strptime(date_clean, "%B %d %Y")
                        year_published = dt.year
                    except Exception:
                        pass
                    # it could be 'December 2002'
                if isinstance(year_published, str) and len(year_published) > 3:
                    match = re.search(r'\b\d{4}\b', year_published)
                    if match:
                        year_published = match.group(0)
                if year_published == '':
                    year_published = None
                # otherwise, disregard the value
                if isinstance(year_published, str) and len(year_published) > 10:
                    year_published = None



                bookshelves = row.get('bookshelves')
                description = row.get('description')
                series = row.get('series')
                # if series is in the format "Series Name #1", extract the name
                if series:
                    series = series.split('#')[0].strip()
                cover_image = row.get('coverimg')
                genres = row.get('genres')
                # genres may be a json-formatted array, like "['Fiction', 'Fantasy']"
                try:
                    genres = json.loads(genres.replace('\'','\"'))
                except json.JSONDecodeError as e:
                    pass
                if genres:
                    # if genres is a list, join it into a string
                    if isinstance(genres, list):
                        genres = ', '.join(genres)
                    else:
                        genres = ', '.join([genre.strip() for genre in genres.split(',')])
                # if it's an empty list, set it to None
                if isinstance(genres, list) and len(genres) == 0:
                    genres = None

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

                # Handle bookshelves - can be currently-reading, to-read, read, wishlist
                status = None
                if bookshelves:
                    bookshelves = [shelf.strip() for shelf in bookshelves.split(',')]
                    # maybe just use the shelf name as status
                    for shelf in bookshelves:
                        if shelf == 'currently-reading':
                            status = CURRENTLY_READING
                        elif shelf == 'to-read':
                            status = TO_READ
                        elif shelf == 'read':
                            status = READ
                        elif shelf == 'wishlist':
                            status = WISHLIST

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
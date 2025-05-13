import csv
from io import StringIO
from flask import Blueprint, jsonify, redirect, render_template, request, url_for, flash, session
from book.book_status import WISHLIST, CURRENTLY_READING, TO_READ, READ
from book.book_types import AUDIOBOOK, EBOOK, PHYSICAL
from metadata.openlibrary import get_book_data
from models import Book, db
from dataclasses import dataclass, field
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

class DictToClass:
    def __init__(self, **entries):
        self.__dict__.update(entries)

@import_bp.route('/')
def search():
    # show a page with multiple import options
    return render_template('import.html')

@import_bp.route('/import_results')
def import_results():
    import_books = session.get('import_books', [])  # Get from session, default to empty list
    # find all existing books in the database
    for book in import_books:
        book_item = DictToClass(**book)
        if book_item.existing_book:
            existing_book = Book.query.get(book_item.existing_book_id)
            book['existing_book_item'] = existing_book
    return render_template('import_results.html', import_books=import_books)

@import_bp.route('/confirm_import', methods=['POST'])
def confirm_import():
    import_books = session.get('import_books', [])

    for i, result in enumerate(import_books):        
        action_suffix = result['author_name'] + result['title']
        action_id = f'action_{action_suffix}'
        action = 'add'  # default action is to add a new book
        if action_id in request.form:
            action = request.form[action_id]
        if action == f'merge':
            # Find existing book by id
            existing_book = Book.query.get(result['existing_book_id'])

            if existing_book:
                # Update existing book
                update_book_fields(result, existing_book)
        else:
            # Create a new book
            new_book = Book()
            # add other fields if added
            update_book_fields(result, new_book)

            db.session.add(new_book)

        db.session.commit()

    # Clear import results from session
    session.pop('import_books', None)

    return redirect(url_for('books.list_books'))

def update_book_fields(result, book):
    book.title = result['title']
    book.author_name = result['author_name']
    if 'year' in result:
        book.year_published = result['year']
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

@import_bp.route('/import_notes', methods=['GET', 'POST'])
def import_notes():
    if request.method == 'POST':
        notes_data = request.form['notes']  # Access the textarea data
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
            elif "physical" in line:
                format = PHYSICAL
            elif "audiobook" in line:
                format = AUDIOBOOK

            title = title.strip()
            author_name = author_name.strip()

            # Check if the book already exists in the database
            existing_book = Book.query.filter(Book.title.ilike(title),Book.author_name.ilike(author_name)).first()
            if existing_book:
                print(f"Book already exists: {title} by {author_name}")
                import_book.existing_book = True
                import_book.existing_book_id = existing_book.id

            import_book.title = title
            import_book.author_name = author_name
            import_book.book_type = format
            import_books.append(import_book)           
            imported_count += 1

        # Redirect to the import details page
        session['import_books'] = import_books

        return redirect(url_for('import.import_results'))
    
    # TODO remove, this page doesn't exist
    return render_template('import_results.html')

@import_bp.route('/import_csv', methods=['POST'])
def import_csv():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            return "No file part", 400

        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return "No selected file", 400

        if csv_file:
            try:
                csv_text = csv_file.read().decode('utf-8')
                csv_data = StringIO(csv_text)
                reader = csv.DictReader(csv_data)
                imported_count = 0
                import_books = [] 

                for row in reader:
                    import_book = BookImport(title=None, author_name=None)

                    title = row.get('Title')
                    author_name = row.get('Author')
                    isbn = row.get('ISBN')
                    isbn13 = row.get('ISBN13')
                    isbn = ", ".join([s for s in [isbn, isbn13] if s is not None])

                    average_rating = row.get('Average Rating')
                    number_of_pages = row.get('Number of Pages')
                    year_published = row.get('Year Published')
                    bookshelves = row.get('Bookshelves')

                    # Check for required fields
                    if not all([title, author_name]):
                        print(f"Skipping row with missing data: {row}")
                        continue

                    # Convert data types
                    try:
                        average_rating = float(average_rating) if average_rating else None
                        number_of_pages = int(number_of_pages) if number_of_pages else None
                        year_published = int(year_published)
                    except ValueError as e:
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

                    existing_book = Book.query.filter(Book.title.ilike(title),Book.author_name.ilike(author_name)).first()
                    if existing_book:
                        print(f"Book already exists: {title} by {author_name}")
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
                    import_books.append(import_book)  
                    imported_count += 1

                # Redirect to the books page after importing
                #flash(f"Successfully imported {imported_count} books!", 'success')  # Flash the message
                    
                session['import_books'] = import_books
                return redirect(url_for('import.import_results'))
            except Exception as e:
                print(f"Error processing CSV file: {e}")
                flash("Error processing CSV file", 'danger')
                return "Error processing CSV file", 500

    # TODO remove, this page doesn't exist
    return render_template('goodreads_import_form.html')

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
            reader = csv.DictReader(csv_data)
            imported_count = 0
            import_books = []

            for row in reader:
                import_book = BookImport(title=None, author_name=None)

                title = row.get('Title')
                author_name = row.get('Author')
                isbn = row.get('ISBN')
                isbn13 = row.get('ISBN13')
                isbn = ", ".join([s for s in [isbn, isbn13] if s is not None])

                average_rating = row.get('Average Rating')
                number_of_pages = row.get('Number of Pages')
                year_published = row.get('Year Published')
                bookshelves = row.get('Bookshelves')

                # Check for required fields
                if not all([title, author_name]):
                    print(f"Skipping row with missing data: {row}")
                    continue

                # Convert data types
                try:
                    average_rating = float(average_rating) if average_rating else None
                    number_of_pages = int(number_of_pages) if number_of_pages else None
                    year_published = int(year_published)
                except ValueError as e:
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

                existing_book = Book.query.filter(Book.title.ilike(title),Book.author_name.ilike(author_name)).first()
                if existing_book:
                    print(f"Book already exists: {title} by {author_name}")
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
        existing_book = Book.query.filter(Book.title.ilike(title),Book.author_name.ilike(author_name)).first()
        if existing_book:
            print(f"Book already exists: {title} by {author_name}")
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
        else:
            # Create a new book
            new_book = Book()
            # add other fields if added
            update_book_fields(result, new_book)
            db.session.add(new_book)

        db.session.commit()

    return jsonify({'status': 'success', 'message': 'Books imported successfully'}), 200
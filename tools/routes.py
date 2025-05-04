import csv
from io import StringIO
from flask import Blueprint, redirect, render_template, request, url_for, flash, session
from metadata.openlibrary import get_book_data
from models import Book, db


import_bp = Blueprint('import', __name__, url_prefix='/import')

@import_bp.route('/')
def search():
    # show a page with multiple import options
    return render_template('import.html')

@import_bp.route('/import_notes', methods=['GET', 'POST'])
def import_notes():
    if request.method == 'POST':
        notes_data = request.form['notes']  # Access the textarea data
        # Process the notes data as needed
        lines = notes_data.splitlines()
        imported_count = 0

        for line in lines:
            # Try both formats: "title - author" and "title (author)"
            # markdown lines begin with a dash
            if line.startswith("- "):
                line = line[2:]
            # Check if the line contains " - " or " (" and ")" to separate title and author
            if " - " in line:
                title, author_name = line.split(" - ")
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
                format = "pdf"
            elif "epub" in line:
                format = "epub"
            elif "physical" in line:
                format = "physical"

            title = title.strip()
            author_name = author_name.strip()
            # Create a new book
            book = Book(
                title=title, 
                author_name=author_name,
                book_type=format,)
            db.session.add(book)
            imported_count += 1
        db.session.commit()
        # Redirect to the books page after importing
        flash(f"Successfully imported {imported_count} books!", 'success')  # Flash the message
        return redirect(url_for('books.list_books'))

    return render_template('import_notes.html')

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

                for row in reader:
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

                    # Create the book
                    book = Book(
                        title=title,
                        author_name=author_name,
                        year_published=year_published,
                        isbn=isbn,
                        rating=average_rating,
                        page_count=number_of_pages,
                        # Add other fields as needed
                    )

                    # Handle bookshelves - can be currently-reading, to-read, read
                    if bookshelves:
                        bookshelves = [shelf.strip() for shelf in bookshelves.split(',')]
                        # maybe just use the shelf name as status
                        for shelf in bookshelves:
                            if shelf == 'currently-reading':
                                book.status = 'currently-reading'
                            elif shelf == 'to-read':
                                book.status = 'to-read'
                            elif shelf == 'read':
                                book.status = 'read'
                            elif shelf == 'wishlist':
                                book.status = 'wishlist'
                    
                    db.session.add(book)
                    imported_count += 1

                db.session.commit()
                # Redirect to the books page after importing
                # TODO figure out a way to show import status - the same in the import_notes
                flash(f"Successfully imported {imported_count} books!", 'success')  # Flash the message
                    
                return redirect(url_for('books.list_books'))
            except Exception as e:
                print(f"Error processing CSV file: {e}")
                flash("Error processing CSV file", 'danger')
                return "Error processing CSV file", 500

    return render_template('goodreads_import_form.html')
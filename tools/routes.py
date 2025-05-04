from flask import Blueprint, redirect, render_template, request, url_for
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
        db.session.commit()
        # Redirect to the books page after importing
        return redirect(url_for('books.list_books'))

    return render_template('import_notes.html')
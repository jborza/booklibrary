from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from models import Book, db
from metadata.openlibrary import get_book_data
from metadata.google_books import search
from book.thumbnails import make_tiny_cover_image, download_cover_image
book_bp = Blueprint('book', __name__, url_prefix='/book')

@book_bp.route('/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)

@book_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.author_name = request.form['author_name']
        book.year_published = request.form['year_published'] if request.form['year_published'] else None
        if 'isbn' in request.form:
            book.isbn = request.form['isbn']
        if 'rating' in request.form:
            book.rating = request.form['rating'] 
        if 'book_type' in request.form:
            book.book_type = request.form['book_type']
        if 'status' in request.form:
            book.status = request.form['status']
        if 'genre' in request.form:
            book.genre = request.form['genre']
        if 'language' in request.form:
            book.language = request.form['language']
        if 'synopsis' in request.form:
            book.synopsis = request.form['synopsis']
        if 'review' in request.form:
            book.review = request.form['review']
        if 'page_count' in request.form:
            book.page_count = request.form['page_count']
        # TODO handle 'None' values better
        if 'series' in request.form and request.form['series'] != 'None':
            book.series = request.form['series']
        if 'tags' in request.form and request.form['tags'] != 'None':
            book.tags = request.form['tags']
        # TODO handle cover image upload
        # book.cover_image = request.form['cover_image']

        db.session.commit()
        flash(f"Book saved", 'success')  
        return redirect(url_for('book.book_detail', book_id=book.id))
    return render_template('edit_book.html', book=book)


@book_bp.route('/<int:book_id>/openlibrary_search')
def openlibrary_search(book_id):
    book = Book.query.get_or_404(book_id)
    # construct the search query
    query = f"{book.title}"
    results = get_book_data(query)
    if len(results) == 0:
        flash("No results found", 'error')
        return redirect(url_for('book.book_detail', book_id=book.id))
    # download the covers
    download_thumbnail(book, results)
    flash(f"Search completed", 'success')
    return jsonify(results)

def download_thumbnail(book, results):
    if 'cover_image' in results[0]:
        cover_image_url = results[0]['cover_image']
        if cover_image_url is not None:
            cover_image = download_cover_image(cover_image_url)
            cover_image_tiny = make_tiny_cover_image(cover_image)
            # update the book object with the new cover image
            book.cover_image = cover_image
            book.cover_image_tiny = cover_image_tiny
            db.session.commit()

@book_bp.route('/<int:book_id>/regenerate_thumbnail', methods=['POST'])
def regenerate_thumbnail(book_id):
    book = Book.query.get_or_404(book_id)
    # construct the search query
    query = f"{book.title}"
    results = get_book_data(query)
    download_thumbnail(book, results)
    flash(f"Thumbnail regenerated", 'success')
    return redirect(url_for('book.book_detail', book_id=book_id))

@book_bp.route('/<int:book_id>/regenerate_thumbnail_google', methods=['POST'])
def regenerate_thumbnail_google(book_id):
    book = Book.query.get_or_404(book_id)
    # construct the search query
    query = f"{book.title}"
    results = search(query)
    download_thumbnail(book, results)
    flash(f"Thumbnail regenerated", 'success')
    return redirect(url_for('book.book_detail', book_id=book_id))

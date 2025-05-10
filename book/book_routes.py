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

@book_bp.route('/api/<int:book_id>')
def book_detail_api(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.as_dict())

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

# TODO rename API method urls
@book_bp.route('/<int:book_id>/edit_api', methods=['POST'])
def edit_book_api(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, no JSON body found"}), 400
    book.title = data['title']
    book.author_name = data['author_name']
    if data['year'] is not None:
        book.year_published = data['year']
    if data['isbn'] is not None:
        book.isbn = data['isbn']
    if data['rating'] is not None:
        book.rating = data['rating']
    if data['book_type'] is not None:
        book.book_type = data['book_type']
    if data['status'] is not None:
        book.status = data['status']
    if data['genre'] is not None:
        book.genre = data['genre']
    if data['language'] is not None:
        book.language = data['language']
    if data['synopsis'] is not None:
        book.synopsis = data['synopsis']
    if data['review'] is not None:
        book.review = data['review']
    if data['page_count'] is not None:
        book.page_count = data['page_count']
    if data['series'] is not None:
        book.series = data['series']
    if data['tags'] is not None:
        book.tags = data['tags']
    #if data['publisher'] is not None:
    #    book.publisher = data['publisher']
    # TODO handle cover image URL / upload?
    # book.cover_image = request.form['cover_image']
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Book saved successfully'}), 200

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
            return True
    return False

@book_bp.route('/<int:book_id>/regenerate_thumbnail', methods=['POST'])
def regenerate_thumbnail(book_id):
    book = Book.query.get_or_404(book_id)
    # construct the search query
    query = f"{book.title}"
    results = get_book_data(query)
    result = download_thumbnail(book, results)
    if not result:
        return jsonify({'status': 'error', 'message': 'Thumbnail not found'}), 500
    return jsonify({'status': 'success', 'message': 'Thumbnail regenerated successfully'}), 200

@book_bp.route('/<int:book_id>/regenerate_thumbnail_google', methods=['POST'])
def regenerate_thumbnail_google(book_id):
    book = Book.query.get_or_404(book_id)
    # construct the search query
    query = f"{book.author_name} {book.title}"
    results = search(query)
    result = download_thumbnail(book, results)
    if not result:
        return jsonify({'status': 'error', 'message': 'Thumbnail not found'}), 500
    return jsonify({'status': 'success', 'message': 'Thumbnail regenerated successfully'}), 200

# an API version
@book_bp.route('/<int:book_id>/match', methods=['GET'])
def match_book(book_id):
    book = Book.query.get_or_404(book_id)
    # construct the search query - search on google books now, but can on openlibrary too
    query = f"{book.author_name} {book.title}"
    results = search(query, count=5)
    if len(results) == 0:
        flash("No results found", 'error')
        return redirect(url_for('book.book_detail', book_id=book.id))
    flash(f"Search completed", 'success')
    return jsonify(results)
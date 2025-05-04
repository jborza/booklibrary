from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from models import Book, db
from .thumbnails import generate_thumbnail

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
        if 'series' in request.form:
            book.series = request.form['series']
        if 'tags' in request.form:
            book.tags = request.form['tags']
        # TODO handle cover image upload
        # book.cover_image = request.form['cover_image']

        db.session.commit()
        flash(f"Book saved", 'success')  
        return redirect(url_for('book.book_detail', book_id=book.id))
    return render_template('edit_book.html', book=book)

@book_bp.route('/<int:book_id>/regenerate_thumbnail', methods=['POST'])
def regenerate_thumbnail(book_id):
    book = Book.query.get_or_404(book_id)
    # use blurhash
    # save the new thumbnail to book.cover_image
    generate_thumbnail(book)
    return jsonify({'success': True})
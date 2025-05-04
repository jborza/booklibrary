from flask import Blueprint, redirect, render_template, request, url_for
from models import Book, db

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
        book.year_published = request.form['year_published']
        book.isbn = request.form['isbn']
        book.rating = request.form['rating']
        book.book_type = request.form['book_type']
        book.status = request.form['status']
        book.genre = request.form['genre']
        book.language = request.form['language']
        book.synopsis = request.form['synopsis']
        book.review = request.form['review']
        book.cover_image = request.form['cover_image']
        book.page_count = request.form['page_count']
        book.series = request.form['series']
        book.tags = request.form['tags']

        db.session.commit()
        return redirect(url_for('book.book_detail', book_id=book.id))
    return render_template('edit_book.html', book=book)
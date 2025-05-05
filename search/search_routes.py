from flask import Blueprint, redirect, render_template, request, url_for
from metadata.openlibrary import get_book_data

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/openlibrary')
def search_openlibrary():
    query = request.args.get('search_query')
    # search with openlibrary API
    if query:
        # Call the Open Library API to get book data
        results = get_book_data(query)
        # display the results in a user-friendly format
        # also show the image from results['cover_image']
    else:
        # If no query is provided, return an empty list or a message
        results = []
    return render_template('search.html', query=query, results=results) 

@search_bp.route('/books')
def search_books():
    query = request.args.get('search_query')
    if query:
        # move to books, with search parameter
        return redirect(url_for('books.search_books', search_query=query))
    else:
        # If no query is provided, return an empty list or a message
        results = []
    return render_template('search.html', query=query, results=results)
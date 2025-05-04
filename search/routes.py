from flask import Blueprint, render_template, request
from metadata.openlibrary import get_book_data

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/')
def search():
    query = request.args.get('search_query')
    # TODO: Implement search functionality here
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
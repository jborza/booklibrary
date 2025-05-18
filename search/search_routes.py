from flask import Blueprint, jsonify, request
from metadata.openlibrary import get_book_data_api
from metadata.google_books import search

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/google_books_api')
def search_google_books_api(count=1):
    count = request.args.get('count', default=1, type=int)
    if count > 10:
        count = 10
    # search with google books API
    query = request.args.get('search_query')
    if query:
        # Call the Google Books API to get book data
        results = search(query, count)
        print(results)
        # display the results in a user-friendly format
        # also show the image from results['cover_image']
    else:
        # If no query is provided, return an empty list or a message
        results = []
    return jsonify(results)

@search_bp.route('/openlibrary_api')
def search_openlibrary_api(count=1):
    count = request.args.get('count', default=1, type=int)
    # limit to 10
    if count > 10:
        count = 10

    query = request.args.get('search_query')
    # search with openlibrary API
    if query:
        # Call the Open Library API to get book data
        results = get_book_data_api(query, count)
    else:
        # If no query is provided, return an empty list or a message
        results = []
    return jsonify(results)


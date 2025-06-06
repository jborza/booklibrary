from flask import Blueprint, jsonify, request
from metadata.providers import PROVIDER_AMAZON, PROVIDER_FUNCTIONS, PROVIDER_GOODREADS, PROVIDER_GOOGLE, PROVIDER_OPENLIBRARY

search_bp = Blueprint('search', __name__, url_prefix='/search')

# use providers from metadata.providers
def search_provider_api(provider, count=1):
    count = request.args.get('count', default=count, type=int)
    # limit to 10
    if count > 10:
        count = 10
    query = request.args.get('search_query')
    # search with provider API
    if query:
        # Call the provider API to get book data
        function = PROVIDER_FUNCTIONS[provider]
        results = function(query, count)
    else:
        # If no query is provided, return an empty list or a message
        results = []
    return jsonify(results)


@search_bp.route('/google_books_api')
def search_google_books_api(count=1):
    return search_provider_api(PROVIDER_GOOGLE, count)


@search_bp.route('/openlibrary_api')
def search_openlibrary_api(count=1):
    return search_provider_api(PROVIDER_OPENLIBRARY, count)


@search_bp.route('/amazon_api')
def search_amazon_api(count=1):
    return search_provider_api(PROVIDER_AMAZON, count)

@search_bp.route('/goodreads_api')
def search_goodreads_api(count=1):
    return search_provider_api(PROVIDER_GOODREADS, count)
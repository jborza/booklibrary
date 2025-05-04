from flask import Blueprint, render_template, request

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/')
def search():
    query = request.args.get('search_query')
    # TODO: Implement search functionality here
    results = []
    return render_template('search.html', query=query, results=results)
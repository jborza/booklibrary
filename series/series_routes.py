from flask import Blueprint, jsonify
from models import Book

series_bp = Blueprint('series', __name__, url_prefix='/series')

@series_bp.route('/api')
def list_series_api():
    query = Book.query.with_entities(Book.series).order_by(Book.series).distinct().all()
    # TODO handle empty series
    # TODO put books in series together
    items = [r for (r, ) in query]
    # some genres are in a json format
    # "['Religion']" or "['Fiction','Fantasy']"
    # buuut - do this when we store the book, not when we read it!!!!
    # remove duplicates
    items = list(set(items))
    # remove empty items
    items = [item for item in items if item]
    # sort the items
    items.sort()
    items = [{'name': x} for x in items]
    return jsonify(series=items)

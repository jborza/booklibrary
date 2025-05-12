from flask import Blueprint, jsonify
from models import Book

series_bp = Blueprint('series', __name__, url_prefix='/series')

SIZE_THUMBNAIL = (128, 200) 

@series_bp.route('/api')
def list_series_api():
    query = Book.query.with_entities(Book.series).order_by(Book.series).distinct().all()
    # TODO handle empty series
    # TODO put books in series together
    series_names = [r for (r, ) in query]
    # remove duplicates
    series_names = list(set(series_names))
    # remove empty items
    series_names = [item for item in series_names if item]
    # sort the items
    series_names.sort()
    series = [{'name': x} for x in series_names]
    # add book cover image for each series
    for s in series:
        # retrieve all books in the series
        books = Book.query.filter_by(series=s['name']).with_entities(Book.id).all()
        s['books'] = [r for (r, ) in books]
    return jsonify(series=series)

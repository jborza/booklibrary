from flask import Blueprint, jsonify
from models import Book

genres_bp = Blueprint('genres', __name__, url_prefix='/genres')

@genres_bp.route('/api')
def list_genres_api():
    query = Book.query.with_entities(Book.genre).distinct().order_by(Book.genre).all()
    items = [r for (r, ) in query]
    # some genres are in a json format
    # "['Religion']" or "['Fiction','Fantasy']"
    # buuut - do this when we store the book, not when we read it!!!!
    # some genres are in an array, so we need to flatten them
    # some genres are separated by commas, so we need to split them
    items = [item.split(',') for item in items if isinstance(item, str)]
    # flatten the list of lists
    items = [item for sublist in items for item in sublist]
    items = [item.strip() for item in items if item]  
    # remove duplicates
    items = list(set(items))
    # remove empty items
    items = [item for item in items if item]
    # sort the genres
    items.sort()
    items = [{'name': x} for x in items]
    return jsonify(genres=items)

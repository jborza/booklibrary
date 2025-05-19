from flask import Blueprint, jsonify, request
from models import Author, Book, OtherBook
from recommendations.recommendations import get_recommendations_for_book

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')

@recommendations_bp.route('/<int:book_id>')
def list_authors_api(book_id):
    # recommended book id
    # amount of recommendations
    count = 10
    if "count" in request.args:
        count = int(request.args.get("count"))
    if count > 20:
        count = 20
    recommended_book_ids = get_recommendations_for_book(book_id, count)
    # load the book data - grab title, author
    titles_authors = OtherBook.query.join(Author).filter(OtherBook.id.in_(recommended_book_ids)).all()
    # grab the titles and authors
    recommendations = []
    for rec in titles_authors:
        recommendations.append({
            'title': rec.title,
            'author': rec.author.name if rec.author else None
        })        
    
    for rec in recommendations:
        print(rec)
    return jsonify(recommendations)
    
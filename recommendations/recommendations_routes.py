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
    print(f"Recommended book ids: {recommended_book_ids}")
    id_to_index = {id_: index for index, id_ in enumerate(recommended_book_ids)}
    # load the book data - grab title, author
    titles_authors = OtherBook.query.join(Author).filter(OtherBook.id.in_(recommended_book_ids)).all()
    # sort the titles_authors by the order of recommended_book_ids
    titles_authors.sort(key=lambda x: id_to_index[x.id])
    # grab the titles and authors
    recommendations = []
    for rec in titles_authors:
        recommendations.append({
            'id': rec.id,
            'title': rec.title,
            'author': rec.author.name if rec.author else None
        })        
    
    for rec in recommendations:
        print(rec)
    return jsonify(recommendations)
    
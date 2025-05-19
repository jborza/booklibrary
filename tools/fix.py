# try to reload genres for Book from OtherBook
from flask import Blueprint, jsonify, request
from models import Author, Book, Genre, OtherBook, db
from recommendations.recommendations import get_recommendations_for_book

fix_bp = Blueprint('fix', __name__, url_prefix='/fix')

def genres_to_ids(genre_str):
    return set(int(g.strip()) for g in genre_str.split(',') if g.strip().isdigit())


@fix_bp.route('/genres')
def fix_genres():
    # get all books that don't have genres
    books = Book.query.join(Author).filter(Book.genre == None).all()
        
    # get all other books
    other_books = OtherBook.query.join(Author).all()
    
    for book in books:
        # get the other book with the same title and author
        other_book = next((ob for ob in other_books if ob.title == book.title), None)        
        if other_book and other_book.genre:            
            book.genre = other_book.genre
            
            print(f"Fixed {book.title} with {other_book.genre}")
    db.session.commit()
    return jsonify({'status': 'ok'})
    
from genres.genres_db import get_genres_ids
from models import Book, OtherBook, db


def genres_to_ids(genre_str):
    return set(int(g.strip()) for g in genre_str.split(',') if g.strip().isdigit())

# Compute recommendations for a given book
def recommend_books(target_book, session, top_n=10):
    # collect book genre ids
    target_genres = set(get_genres_ids(target_book.genre))
    # grab all other books from the database, with id and genres
    other_books = session.query(OtherBook.id, OtherBook.genre_ids).filter(OtherBook.genre_ids != None).filter(OtherBook.genre_ids != '')
    # skip this author as we'd like to recommend books from other authors
    other_books = other_books.filter(OtherBook.author_id != target_book.author_id).all()
    
    # maybe move them to a dictionary id:genre_ids
    scores = []
    for book in other_books:
        # convert genre ids to a set of ids
        genre_ids = genres_to_ids(book.genre_ids)
        # calculate the similarity score - Jaccard similarity
        sim = len(target_genres & genre_ids) / len(target_genres | genre_ids) if (target_genres | genre_ids) else 0
        # add the similarity score to the book object
        if sim == 0:
            continue
        
        scores.append((sim,book))
    
    # get the top n books
    scores.sort(reverse=True, key=lambda x: x[0])
    ID = 0
    return [book[ID] for sim, book in scores[:top_n] if sim > 0]

def get_recommendations_for_book(desired_book_id, top_n=10):
    session = db.session
    # Fetch the target book from the database
    target_book = session.query(Book).get(desired_book_id)
    
    recommendations = recommend_books(target_book, session, top_n)
    return recommendations
from genres.genres_db import get_genres_ids
from models import Book, OtherBook, db


# def prepare_recommendations(session):
#     all_genres = set()
#     # do first 1000 books
#     for book in session.query(Book).limit(50000):
#         if book.genre is None:
#             continue
#         all_genres.update([g.strip() for g in book.genre.split(',')])

#     genre2id = {genre: idx for idx, genre in enumerate(sorted(all_genres))}
#     return genre2id

# 2. Function to convert string to ID set
def genres_to_ids(genre_str, genre2id):
    return set(genre2id[g.strip()] for g in genre_str.split(',') if g.strip() in genre2id)

# 3. Compute recommendations for a given book
def recommend_books(target_book, session, top_n=10):
    # collect book genre ids
    book_genres = get_genres_ids(target_book.genre)
    # grab all other books from the database, with id and genres
    other_books = session.query(OtherBook.id, OtherBook.genre_ids, OtherBook.title).all()
    only_data = [book._asdict() for book in other_books]
    return only_data
    
    # target_genres = genres_to_ids(target_book.genre, genre2id)
    # scores = []
    # for book in session.query(Book).filter(Book.id != target_book.id):
    #     if book.genre is None:
    #         continue
    #     book_genres = genres_to_ids(book.genre, genre2id)
    #     sim = len(target_genres & book_genres) / len(target_genres | book_genres) if (target_genres | book_genres) else 0
    #     scores.append((sim, book))
    # scores.sort(reverse=True, key=lambda x: x[0])
    # return [book for sim, book in scores[:top_n] if sim > 0]

def get_recommendations_for_book(desired_book_id, top_n=10):
    session = db.session
    # genre2id = prepare_recommendations(session)
    print('prepared recommendations')
    # Fetch the target book from the database
    target_book = session.query(Book).get(desired_book_id)
    
    recommendations = recommend_books(target_book, session, top_n)
    return recommendations
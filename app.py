"""
Flask application for a book management system.

    Import necessary modules (Flask, database libraries, etc.).
    Create a Flask app instance.
    Define routes for different pages (home, search, authors, wishlist, etc.).
    Handle form submissions (e.g., for adding a book).
    Interact with the database to retrieve and store data.
    Render templates to display content.

"""
import secrets
from flask import Flask, jsonify, redirect, url_for
from flask_cors import CORS
from downloader import downloader
from recommendations.recommendations import get_recommendations_for_book
from models import Author, Book, OtherBook, db
from search.search_routes import search_bp
from books.books_routes import books_bp  
from book.book_routes import book_bp
from tools.import_routes import import_bp
from authors.authors_routes import authors_bp
from genres.genres_routes import genres_bp
from series.series_routes import series_bp
from downloader.downloader_routes import downloader_bp
from recommendations.recommendations_routes import recommendations_bp
from tools.fix import fix_bp

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16) # Generate a random secret key
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(search_bp)
app.register_blueprint(books_bp)
app.register_blueprint(book_bp)
app.register_blueprint(import_bp)
app.register_blueprint(authors_bp)
app.register_blueprint(genres_bp)
app.register_blueprint(series_bp)
app.register_blueprint(downloader_bp)
app.register_blueprint(recommendations_bp)
app.register_blueprint(fix_bp)

@app.route('/')
def home():
    return redirect(url_for('books.list_books'))

if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()
    # TODO re-enable later
    #downloader.schedule_cover_download(app)


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
from flask import Flask, render_template, request, redirect, url_for
from models import db, Book  
from search.search_routes import search_bp
from books.books_routes import books_bp  
from book.book_routes import book_bp
from tools.import_routes import import_bp
from authors.authors_routes import authors_bp

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16) # Generate a random secret key
db.init_app(app)

app.register_blueprint(search_bp)
app.register_blueprint(books_bp)
app.register_blueprint(book_bp)
app.register_blueprint(import_bp)
app.register_blueprint(authors_bp)

@app.route('/')
def home():
    return redirect(url_for('books.list_books'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
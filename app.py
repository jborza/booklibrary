"""
Flask application for a book management system.

    Import necessary modules (Flask, database libraries, etc.).
    Create a Flask app instance.
    Define routes for different pages (home, search, authors, wishlist, etc.).
    Handle form submissions (e.g., for adding a book).
    Interact with the database to retrieve and store data.
    Render templates to display content.

"""
from flask import Flask, render_template, request, redirect, url_for
from models import db, Book  
from search.routes import search_bp
from books.routes import books_bp  
from book.routes import book_bp
from tools.routes import import_bp

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(search_bp)
app.register_blueprint(books_bp)
app.register_blueprint(book_bp)
app.register_blueprint(import_bp)

@app.route('/')
def home():
    return redirect(url_for('books.list_books'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
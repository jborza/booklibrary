"""
Flask application for a book management system.

    Import necessary modules (Flask, database libraries, etc.).
    Create a Flask app instance.
    Define routes for different pages (home, search, authors, wishlist, etc.).
    Handle form submissions (e.g., for adding a book).
    Interact with the database to retrieve and store data.
    Render templates to display content.

"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('books.html')

@app.route('/books')
def books():
    return render_template('books.html')

if __name__ == '__main__':
    app.run(debug=True)
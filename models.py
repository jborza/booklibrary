from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
db = SQLAlchemy()

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    surname = db.Column(db.String(200), nullable=False)
    surname_first = db.Column(db.String(200), nullable=False)  # Surname first, used for sorting
    cover_image = db.Column(db.String(200))  # URL or path to the cover image
    cover_image_tiny = db.Column(db.String(200))  # URL or path to the small version of cover image
    description = db.Column(db.Text)

    def as_dict(self):
        dict = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        # Handle date serialization (if necessary)
        for key, value in dict.items():
            if isinstance(value, datetime):
                dict[key] = value.isoformat()  # Convert datetime to ISO string
        return dict

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)  # Foreign key to Author
    author = db.relationship('Author', backref=db.backref('books', lazy=True))
    year_published = db.Column(db.Integer)
    isbn = db.Column(db.String(20))  # ISBN number
    rating = db.Column(db.Float)
    book_type = db.Column(db.String(20))  # ebook, audiobook, physical
    status = db.Column(db.String(20))  # to read, reading, read, wishlist
    genre = db.Column(db.Text) # List of genres (e.g., fiction, non-fiction, etc.)
    language = db.Column(db.String(20))  # Language of the book
    synopsis = db.Column(db.Text)
    review = db.Column(db.Text)
    cover_image = db.Column(db.String(200))  # URL or path to the cover image
    cover_image_tiny = db.Column(db.String(200))  # URL or path to the small version of cover image
    page_count = db.Column(db.Integer)  # Number of pages for physical books
    series = db.Column(db.String(100))  # Series name if applicable
    tags = db.Column(db.String(200))  # Comma-separated tags for easy searching
    cover_thumbnail = db.Column(db.Text)  # URL or path to the thumbnail image
    def __repr__(self):
        return f'<Book {self.title}>'
    
    def as_dict(self):
        book_dict = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        # Handle date serialization (if necessary)
        for key, value in book_dict.items():
            if isinstance(value, datetime):
                book_dict[key] = value.isoformat()  # Convert datetime to ISO string
        return book_dict

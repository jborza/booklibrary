from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
db = SQLAlchemy()


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)  # Redundant for easier querying
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
        # todo isn't there a better way to do this?
        # return {
        #     'id': self.id,
        #     'title': self.title,
        #     'author_name': self.author_name,
        #     'book_type': self.book_type,
        #     'status': self.status,
        #     'date_added': self.date_added.isoformat() if self.date_added else None  # Handle datetime
        # }
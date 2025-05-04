from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)  # Redundant for easier querying
    year_published = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True, nullable=False)  # ISBN number
    rating = db.Column(db.Float)
    book_type = db.Column(db.String(20))  # ebook, audiobook, physical
    status = db.Column(db.String(20))  # to read, read, wishlist
    genre = db.Column(db.Text) # List of genres (e.g., fiction, non-fiction, etc.)
    language = db.Column(db.String(20))  # Language of the book
    synopsis = db.Column(db.Text)
    review = db.Column(db.Text)
    cover_image = db.Column(db.String(200))  # URL or path to the cover image
    page_count = db.Column(db.Integer)  # Number of pages for physical books
    series = db.Column(db.String(100))  # Series name if applicable
    tags = db.Column(db.String(200))  # Comma-separated tags for easy searching

    def __repr__(self):
        return f'<Book {self.title}>'
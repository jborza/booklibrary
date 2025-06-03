import os
from models import Book, db

BOOKS_DIR = os.path.abspath("data")
os.makedirs(BOOKS_DIR, exist_ok=True)

BOOK_FILENAME = 'book'

def get_supported_extensions():
    # Returns a list of supported file extensions
    return ['.pdf', '.epub', '.mobi', '.txt', '.azw3', '.htm', '.html', '.pdb', '.djvu', '.fb2']

def save_book_file(book_id, file_obj, original_filename, supported_extensions):
    file_extension = os.path.splitext(original_filename)[1].lower()
    if file_extension not in supported_extensions:
        raise ValueError(f'Unsupported file type: {file_extension}')
    path = f'{book_id}/{BOOK_FILENAME}{file_extension}'
    path = os.path.join(BOOKS_DIR, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_obj.seek(0)
    file_obj.save(path) if hasattr(file_obj, 'save') else open(path, 'wb').write(file_obj.read())
    return path
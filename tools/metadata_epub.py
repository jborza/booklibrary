from ebooklib import epub
from tools.metadata import UNKNOWN

def get_metadata_epub(epub_path):
    """Extract author and title metadata from an EPUB file."""
    try:
        book = epub.read_epub(epub_path)
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else UNKNOWN
        author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else UNKNOWN
        return author, title
    except Exception as e:
        print(f"Error reading {epub_path}: {e}")
        return None, None
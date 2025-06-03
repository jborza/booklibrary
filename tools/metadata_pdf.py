from PyPDF2 import PdfReader
from tools.metadata import UNKNOWN


def get_metadata_pdf(pdf_path):
    """Extract author and title metadata from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata
        title = metadata.title if metadata and metadata.title else UNKNOWN
        author = metadata.author if metadata and metadata.author else UNKNOWN
        return author, title
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None, None
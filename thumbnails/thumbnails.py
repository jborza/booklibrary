import hashlib
from pathlib import Path
from urllib.parse import urlparse
import requests
from files.files import BOOKS_DIR
from models import Book, db
from PIL import Image

import os

THUMBNAIL_SIZE = (64, 64)  # Set the desired thumbnail size
THUMBNAIL_SIZE_LARGE = (128, 200)


def download_cover_image(book_id, cover_image_url):
    """
    Download the cover image from the given URL and save it to a local directory.

    Args:
        url (str): The URL of the cover image.

    Returns:
        str: The path to the saved image file.
    """
    try:
        response = requests.get(cover_image_url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Extract filename from URL
        # we suppose it's jpeg, not png
        ext = '.jpg'
        path = f'{book_id}/cover{ext}'
        path = os.path.join(BOOKS_DIR, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        filename = os.path.basename(path)
        return filename
    except requests.exceptions.RequestException as e:
        print(f"Error downloading cover image: {e}")
        return None

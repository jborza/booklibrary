import hashlib
from pathlib import Path
from urllib.parse import urlparse
import requests
from models import Book, db
from PIL import Image
import secrets

import os

THUMBNAIL_SIZE = (64, 64)  # Set the desired thumbnail size


def make_tiny_cover_image(cover_image):
    original_image = Image.open(os.path.join("static", cover_image))
    original_image.thumbnail(THUMBNAIL_SIZE)
    thumb_name = "tiny_" + os.path.basename(cover_image)
    original_image.save(os.path.join("static", "covers", thumb_name), format="JPEG")
    return "covers/" + thumb_name  # Store relative path in DB


def download_cover_image(cover_image_url):
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

        # Extract filename from URL # TODO hash - import hashlib - hashlib.sha1(sample_string.encode()).hexdigest()
        filename = hashlib.sha1(cover_image_url.encode()).hexdigest() + ".jpg"
        # maybe the file already exists
        existing_file = os.path.join("./static", "covers", filename)
        if os.path.exists(existing_file):
            return "covers/" + filename  # Store relative path in DB
        # Save the image to the 'covers' directory
        os.makedirs("./static/covers", exist_ok=True)
        filepath = os.path.join("./static", "covers", filename)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        cover_image = "covers/" + filename  # Store relative path in DB
        return cover_image
    except requests.exceptions.RequestException as e:
        print(f"Error downloading cover image: {e}")
        return None

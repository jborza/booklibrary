import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('GOOGLE_BOOKS_API_KEY')

def search(query, count=1):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "key": api_key, "maxResults": count}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("items", []):
        volume = item.get("volumeInfo", {})
        results.append({
            "title": volume.get("title"),
            "author_name": volume.get("authors")[0] if volume.get("authors") else "Unknown",
            "language": volume.get("language"),
            "year_published": volume.get("publishedDate"),
            "synopsis": volume.get("description"),
            "cover_image": volume.get("imageLinks", {}).get("thumbnail"),
            "page_count": volume.get("pageCount"),
            "isbn": volume.get("industryIdentifiers", [{}])[0].get("identifier"),
            "genre": ','.join(volume.get("categories")) if volume.get("categories") else None,
        })
    return results
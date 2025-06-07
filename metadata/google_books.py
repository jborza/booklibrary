import os
from dotenv import load_dotenv
import requests

from tools.levenshtein import sort_by_levenshtein_distance


load_dotenv()

api_key = os.getenv('GOOGLE_BOOKS_API_KEY')

def separate_genres(genres):
    return ', '.join(item.strip() for item in genres.replace('&', ',').split(','))

def get_googlebooks_data_list(query, count=1):
    url = "https://www.googleapis.com/books/v1/volumes"
    # ask for more results than needed, so we can sort
    if count < 10:
        queryCount = 10
    params = {"q": query, "key": api_key, "maxResults": queryCount}
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
            "publisher": volume.get("publisher"),
            "rating": volume.get("averageRating"),
        })
        # if genres are like Biography & Autobiography, replace & with ,
        if results[-1]['genre']:
            results[-1]['genre'] = separate_genres(results[-1]['genre'])
    # sort by levenshtein distance
    results = sort_by_levenshtein_distance(results, query)
    # return only the first 'count' results
    results = results[:count]
    return results


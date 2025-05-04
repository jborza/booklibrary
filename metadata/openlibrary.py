#see C:\projects\_github\colibri\apps\app\src\lib\metadata\open-library.ts 
# example request: 
# https://openlibrary.org/search.json?title=the%20chronology%20of%20water&fields=*&limit=1
# https://openlibrary.org/search.json?q=Gaming%20the%20Iron%20Curtain&fields=*&limit=1
import requests
import requests_cache

# Configure the cache
cache_name = 'openlibrary_cache'
expire_after = 3600  # Cache expires after 1 hour (3600 seconds)
session = requests_cache.CachedSession(cache_name, expire_after=expire_after)

def fetch_book_data(title):
    url = f"https://openlibrary.org/search.json?title={title}&fields=*&limit=1"
    
    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        if data['numFound'] == 0:
            return {"error": "No results found"}
        
        book_data = data['docs'][0]
        return book_data
    except requests.RequestException as e:
            return {"error": str(e)}

def get_book_data(title):
    """
    Fetch book data from Open Library API based on the title.
    
    Args:
        title (str): The title of the book to search for.
        
    Returns:
        dict: A dictionary containing book data or an error message.
    """
    
    book_data = fetch_book_data(title)
    if "error" in book_data:
        return book_data

    # TODO obtain cover image from cover_i
    # TODO use blurha.sh to generate a placeholder image
    
    # Extract relevant fields
    result = {
        "title": book_data.get("title"),
        "author_name": book_data.get("author_name", ["Unknown"])[0],
        "year_published": book_data.get("first_publish_year"),
        "isbn": book_data.get("isbn", [""])[0], # multiple ISBNs possible
        "rating": None,  # Open Library does not provide ratings
        "book_type": None,  # Not available in Open Library
        "status": None,  # Not available in Open Library
        "genre": ", ".join(book_data.get("subject", [])),
        "language": ", ".join(book_data.get("language", [])),
        "synopsis": book_data.get("description", ""),
        "review": None,  # Not available in Open Library
        "cover_image": f"https://covers.openlibrary.org/b/id/{book_data.get('cover_i')}-L.jpg" if book_data.get("cover_i") else None,
        "page_count": book_data.get("number_of_pages_median",0),  # Not available in Open Library
        "series": None,  # Not available in Open Library
        "tags": None,  # Not available in Open Library
        "subject": ", ".join(book_data.get("subject", [])),
    }

    # also available:
    # subject: Europe, eastern, history
    
    return result
#see C:\projects\_github\colibri\apps\app\src\lib\metadata\open-library.ts 
# example request: 
# https://openlibrary.org/search.json?title=the%20chronology%20of%20water&fields=*&limit=1
# https://openlibrary.org/search.json?q=Gaming%20the%20Iron%20Curtain&fields=*&limit=1
import requests
import requests_cache

from tools.levenshtein import sort_by_levenshtein_distance

# Configure the cache
cache_name = 'openlibrary_cache'
expire_after = 3600  # Cache expires after 1 hour (3600 seconds)
session = requests_cache.CachedSession(cache_name, expire_after=expire_after)

def fetch_book_data(title, limit):
    url = f"https://openlibrary.org/search.json?title={title}&fields=*&limit={limit}"

    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if data['numFound'] == 0:
            return {"error": "No results found"}

        # n entries - data['docs]
        book_data = data['docs']
        return book_data
    except requests.RequestException as e:
        return {"error": str(e)}

def fetch_book_data_api(title, limit):
    # TODO we could also search by author, and so with
    # https://openlibrary.org/search.json?q=the+lord+of+the+rings
    # see https://openlibrary.org/dev/docs/api/search?v=43
    url = f"https://openlibrary.org/search.json?title={title}&fields=*&limit={limit}"

    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if data['numFound'] == 0:
            return []

        # n entries - data['docs]
        book_data = data['docs']
        return book_data
    except requests.RequestException as e:
        return []

def get_openlibrary_data(title, count=1):
    """
    Fetch book data from Open Library API based on the title.
    
    Args:
        title (str): The title of the book to search for.
        
    Returns:
        dict: A dictionary containing book data or an error message.
    """

    book_data = fetch_book_data(title, count)
    if "error" in book_data:
        return book_data

    # Extract relevant fields
    result = [fill_book_data(b) for b in book_data]
    return result

def get_openlibrary_data_list(title, count=1):
    """
    Fetch book data from Open Library API based on the title.
    
    Args:
        title (str): The title of the book to search for.
        
    Returns:
        dict: A dictionary containing book data or an error message.
    """
    # ask for more results than needed, so we can sort
    if count < 10:
        queryCount = 10
    else:
        queryCount = count
    book_data = fetch_book_data_api(title, queryCount)
    if "error" in book_data:
        return book_data

    # Extract relevant fields
    results = [fill_book_data(b) for b in book_data]
    # sort by levenshtein distance
    results = sort_by_levenshtein_distance(results, title)
    # return only the first 'count' results
    results = results[:count]
    return results

def fill_book_data(book_data):
    result = {
        "title": book_data.get("title"),
        "author_name": book_data.get("author_name", ["Unknown"])[0],
        "year_published": book_data.get("first_publish_year"),
        "isbn": book_data.get("isbn", [""])[0], # multiple ISBNs possible
        "language": ", ".join(book_data.get("language", [])),
        "synopsis": book_data.get("description", ""),
        "cover_image": f"https://covers.openlibrary.org/b/id/{book_data.get('cover_i')}-L.jpg" if book_data.get("cover_i") else None,
        "page_count": book_data.get("number_of_pages_median",0),  # Not available in Open Library
        "subject": ", ".join(book_data.get("subject", [])),
        # some books have also ratings_average
        "rating": round(book_data.get("ratings_average", 0), 1),  # Not available in Open Library
    }
    
    return result
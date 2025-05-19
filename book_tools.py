from datetime import datetime
import re

import json
from book.book_status import WISHLIST, CURRENTLY_READING, TO_READ, READ
from book.book_types import AUDIOBOOK, EBOOK, PHYSICAL

def extract_isbn(isbn, isbn13):
    # prefer isbn13 if both are present
    if isbn and isbn13:
        isbn = isbn13
    # goodreads isbn format looks like '="9781604865301"' - extract the value
    match = re.search(r'"(\d+)"', isbn)
    if match:
        isbn = match.group(1)
    # sometimes isbn stays like ="" - in this case it's empty
    if isbn == '=""':
        isbn = None
    # sometimes it's 9999999999999 - remove it
    if isbn == '9999999999999':
        isbn = None
    return isbn
        
def extract_year(row):
    year_published = row.get('year published')
    # or publishDate?
    if year_published == None:
        year_published = row.get('publishdate')
    # sometimes it says just 'Published' - take other column
    if year_published == 'Published':
        year_published = row.get('firstpublishdate')

    # it could be in this format: 09/14/08
    try:
        date = datetime.strptime(year_published, '%m/%d/%y')
        year_published = date.year
    except ValueError:
        pass
    # it could also be in this format: July 7th 2013
    if isinstance(year_published, str):
        try:
            date_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', year_published)
            dt = datetime.strptime(date_clean, "%B %d %Y")
            year_published = dt.year
        except Exception:
            pass
        # it could be 'December 2002'
    if isinstance(year_published, str) and len(year_published) > 3:
        match = re.search(r'\b\d{4}\b', year_published)
        if match:
            year_published = match.group(0)
    if year_published == '':
        year_published = None
    # otherwise, disregard the value
    if isinstance(year_published, str) and len(year_published) > 10:
        year_published = None
    return year_published

def extract_genres(genres):
    # genres may be a json-formatted array, like "['Fiction', 'Fantasy']"
    try:
        genres = json.loads(genres.replace('\'','\"'))
    except json.JSONDecodeError as e:
        pass
    if genres:
        # if genres is a list, join it into a string
        if isinstance(genres, list):
            genres = ', '.join(genres)
        else:
            genres = ', '.join([genre.strip() for genre in genres.split(',')])
    # if it's an empty list, set it to None
    if isinstance(genres, list) and len(genres) == 0:
        genres = None
    return genres

def extract_status(bookshelves):
    status = None
    if bookshelves:
        bookshelves = [shelf.strip() for shelf in bookshelves.split(',')]
        # maybe just use the shelf name as status
        for shelf in bookshelves:
            if shelf == 'currently-reading':
                status = CURRENTLY_READING
            elif shelf == 'to-read':
                status = TO_READ
            elif shelf == 'read':
                status = READ
            elif shelf == 'wishlist':
                status = WISHLIST
    return status
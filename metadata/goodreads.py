import re
import requests
from bs4 import BeautifulSoup

def get_headers():
    headers = {
        'accept': 'text/html, application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'device-memory': '8',
        'downlink': '10',
        'dpr': '2',
        'ect': '4g',
        'origin': 'https://www.goodreads.com',
        'priority': 'u=1, i',
        'rtt': '50',
        'sec-ch-device-memory': '8',
        'sec-ch-dpr': '2',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-viewport-width': '1170',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'viewport-width': '1170',
        'x-amz-amabot-click-attributes': 'disable',
        'x-requested-with': 'XMLHttpRequest'
    }
    return headers

def get_goodreads_data(query):
    url = f"https://www.goodreads.com/search?q={query}&search_type=books"
    response = requests.get(url, headers=get_headers())
    html_content = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # get a table of search results
    table = soup.find('table')

    # get each <tr itemscope
    # TODO load more results, it seems we're only getting the first result
    rows = table.find_all('tr', itemscope=True)
    results = []
    for row in rows:
        # Extract book information
        title = row.find('span', {'itemprop': 'name'}).text.strip()
        author = row.find('a', {'class': 'authorName'}).text.strip()
        publication_el = row.find('span', {'class': 'uitext'})
        publication_year = publication_el.text.strip()
        publication_text = publication_year # looks like "published 2011"
        m = re.search(r'\b\d{4}\b', publication_text)
        if m:
            publication_year = m.group(0)  # Extract the year
        else:
            publication_year = None
        average_rating = soup.find('span', {'class': 'minirating'}).text.strip() # looks like  4.05 avg rating — 2,262 ratings
        # get just the rating
        average_rating = average_rating.split('avg rating')[0].strip()
        thumbnail_url = soup.find('img', {'class': 'bookCover'})['src']

        results.append({
            'title': title,
            'author': author,
            'thumbnail': thumbnail_url,
            'rating': average_rating,
            'publication_year': publication_year,
        })
    return results

def get_goodreads_data_list(query, count=1):
    list = get_goodreads_data(query)
    if not list:
        return None
    wanted_results = list[:count]
    results = []
    for item in wanted_results:
        results.append({
            'title': item['title'],
            'author_name': item['author'],
            'cover_image': item['thumbnail'],
            'rating': item['rating'],
            'year_published': item['publication_year'],
        })
    return results
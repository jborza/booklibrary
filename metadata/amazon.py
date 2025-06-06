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
        'origin': 'https://www.amazon.com',
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

def get_amazon_data(query, count=1):
    url = f"https://www.amazon.com/s?k={query}&rh=n%3A154606011&ref=nb_sb_noss"
    # params = {"q": query, "key": api_key, "maxResults": count}
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the page. Status code:", response.status_code)
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    results = []
    # Find all search results; Amazon search results are typically contained in divs with data-component-type="s-search-result"
    items = soup.find_all('div', attrs={'data-component-type': 's-search-result'})

    # Extract the first three results
    for item in items:
        item_div = item.find('div', attrs={"data-csa-c-type":"item"})
        if not item_div:
            continue
        #then class should be widgetId=search-results_*
        classes = item_div['class']
        search_results = [x for x in classes if x.startswith("widgetId=search-results")]
        if len(search_results) == 0:
            continue
        # if we get here, it's a main result
        # Extract the title; it is usually wrapped in an <h2> tag
        title_elem = item.find('h2')
        title = title_elem.get_text(strip=True) if title_elem else "No Title Found"

        # Extract the thumbnail image URL from <img> tag
        thumbnail_elem = item.find('img')
        thumbnail = thumbnail_elem['src'] if thumbnail_elem and thumbnail_elem.has_attr('src') else "No Thumbnail Found"

        # Extract the rating; often found in a <span> with class 'a-icon-alt'
        rating_elem = item.find('span', class_='a-icon-alt')
        rating = rating_elem.get_text(strip=True) if rating_elem else "No Rating Found"
        # rating is sometimes like "4.5 out of 5 stars", so we can just take the first part
        if rating != "No Rating Found":
            rating = rating.split(' ')[0]
        # Extract the author; this can vary based on the layout. Here we search for a link with a common class but you might need to adjust this selector.
        author_link = soup.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style')
        author_name = author_link.get_text(strip=True) if author_link else "Author not found"
        
        # TODO getPageCount, language, series, publication date, publisher, isbn13, description
        results.append({
            'title': title,
            'author': author_name,
            'thumbnail': thumbnail,
            'rating': rating,
        })
    return results

def get_amazon_data_list(query, count=1):
    list = get_amazon_data(query, count)
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
        })
    return results

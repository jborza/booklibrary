from metadata import amazon, goodreads, openlibrary, google_books


PROVIDER_GOOGLE = "google"
PROVIDER_AMAZON = "amazon"
PROVIDER_OPENLIBRARY = "openlibrary"
PROVIDER_GOODREADS = "goodreads"

PROVIDER_LIST = [
    PROVIDER_GOOGLE,
    PROVIDER_AMAZON,
    PROVIDER_OPENLIBRARY,
    PROVIDER_GOODREADS
]

PROVIDER_FUNCTIONS = {
    "goodreads": goodreads.get_goodreads_data_list,
    "amazon": amazon.get_amazon_data_list,
    "google": google_books.get_googlebooks_data_list,
    "openlibrary": openlibrary.get_openlibrary_data_list,
}


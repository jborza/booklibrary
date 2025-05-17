from models import Author


def fill_author_data(author: Author, data):
    author.name = data['author_name'].strip()
    name_parts = author.name.rsplit(' ', 1)
    if len(name_parts) == 2:
        given_names, surname = name_parts
    else:
        # Handle edge cases where there's no surname or only one name part
        given_names = name_parts[0]
        surname = ''
    author.surname_first = f"{surname} {given_names}"
    author.surname = surname
    return author
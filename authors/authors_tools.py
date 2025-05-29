from models import Author, db
import re


def fill_author_data(author: Author, name: str):
    author.name = name #data['author_name'].strip()
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

def get_author_by_name(name):
    author = Author.query.filter_by(name=name).first()
    if author is None:
        # create a new author
        author = Author()
        fill_author_data(author, name)
        db.session.add(author)
        db.session.commit()
    return author

def extract_main_author(author_string):
    # Split by comma, but not inside parentheses
    parts = re.split(r',\s*(?![^()]*\))', author_string)
    first = parts[0].strip()
    # If the string contains only one comma AND no parentheses AND both sides have at least one space,
    # treat as "Surname, Firstname" (possibly with multi-part first names)
    if (
        ',' in author_string
        and len(parts) == 2
        and '(' not in first
        and not re.search(r'\(', parts[1])
        and re.search(r'\w', parts[1])
    ):
        surname, rest = first, parts[1].strip()
        return f"{rest} {surname}".strip()
    # Otherwise, just return the first part, removing any parentheses annotation
    author = re.sub(r'\s*\([^)]*\)', '', first).strip()
    # remove continuous spaces
    author = re.sub(r'\s+', ' ', author)
    return author

def capitalize_name(name):
    parts = [part.strip() for part in name.split('.')]  # Split on periods and strip whitespace
    processed = [part.title() for part in parts]  # Capitalize each word in the part
    return ' '.join(processed)  # Join with spaces for the final result
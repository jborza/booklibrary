from models import Author, db


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
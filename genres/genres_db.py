from models import Genre, db


def get_genres_ids(genres):
    
    """
    Get the genre ids from the genres list.
    :param genres: list of genres
    :return: list of genre ids
    """
    # it's a comma-separated string, convert it to a list
    genre_list = genres.split(',') if isinstance(genres, str) else genres
    genre_list = [genre.strip() for genre in genre_list]
    # remove duplicates
    genre_list = list(set(genre_list))
    # for each genre, get the id
    genre_ids = []
    for genre in genre_list:
        # check if the genre exists in the database
        genre_obj = Genre.query.filter_by(name=genre).first()
        if genre_obj:
            genre_ids.append(genre_obj.id)
        else:
            # if the genre doesn't exist, create it
            new_genre = Genre(name=genre)
            db.session.add(new_genre)
            db.session.commit()
            genre_ids.append(new_genre.id)
    genre_ids.sort()
    return genre_ids
    
def format_title(title):
    parts = [part.strip() for part in title.split(',')]
    processed = [part.title() for part in parts]
    return ', '.join(processed)
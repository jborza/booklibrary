CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    surname_first VARCHAR(255) NOT NULL
);

CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES authors(id),
    title VARCHAR(1024) NOT NULL,
    sortable_title VARCHAR(1024) NOT NULL,
    status VARCHAR(100),
    tags VARCHAR(1024),
    remote_image_url VARCHAR(1024),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE other_books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(1024) NOT NULL,
    author VARCHAR(512) NOT NULL,
    source VARCHAR(255)
);

CREATE TABLE book_collection (
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, collection_id)
);

CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_books_sortable_title ON books(sortable_title);
CREATE INDEX idx_books_remote_image_url ON books(remote_image_url);

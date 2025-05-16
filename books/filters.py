from dataclasses import dataclass

@dataclass
class BookFilter:
    search: str = None
    author: str = None
    genre: str = None
    series: str = None
    book_type: str = None
    book_status: str = None
    pages_min: int = None
    pages_max: int = None
    year_min: int = None
    year_max: int = None
    rating_min: float = None
    rating_max: float = None
    language: str = None
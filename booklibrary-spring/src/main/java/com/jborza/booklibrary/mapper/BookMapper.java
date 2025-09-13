package com.jborza.booklibrary.mapper;

import com.jborza.booklibrary.domain.Book;
import com.jborza.booklibrary.dto.BookResponse;
import org.springframework.stereotype.Component;

@Component
public class BookMapper {
    public BookResponse toResponse(Book book) {
        return new BookResponse(
                book.getId(),
                book.getTitle(),
                book.getSortableTitle(),
                book.getAuthor().getId(),
                book.getAuthor().getName() + " " + book.getAuthor().getSurname(),
                book.getStatus(),
                book.getTags(),
                book.getRemoteImageUrl()
        );
    }
}

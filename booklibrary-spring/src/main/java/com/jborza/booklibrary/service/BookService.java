package com.jborza.booklibrary.service;

import com.jborza.booklibrary.domain.Book;
import com.jborza.booklibrary.dto.BookRequest;
import com.jborza.booklibrary.exception.NotFoundException;
import com.jborza.booklibrary.mapper.BookMapper;
import com.jborza.booklibrary.repository.AuthorRepository;
import com.jborza.booklibrary.repository.BookRepository;
import com.jborza.booklibrary.spec.BookSpecifications;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class BookService {
    private final BookRepository bookRepository;
    private final AuthorRepository authorRepository;
    private final BookMapper mapper;

    public BookService(BookRepository bookRepository, AuthorRepository authorRepository, BookMapper mapper) {
        this.bookRepository = bookRepository;
        this.authorRepository = authorRepository;
        this.mapper = mapper;
    }

    @Transactional
    public Object create(BookRequest req) {
        var author = authorRepository.findById(req.authorId())
                .orElseThrow(() -> new NotFoundException("Author " + req.authorId() + " not found"));
        Book book = new Book(req.title(), author, req.status(), req.tags(), req.remoteImageUrl());
        bookRepository.save(book);
        return mapper.toResponse(book);
    }

    public Object get(Long id) {
        var book = bookRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Book " + id + " not found"));
        return mapper.toResponse(book);
    }

    public List<Object> search(String q, String status, String author) {
        Specification<Book> spec = BookSpecifications.all(List.of(
                BookSpecifications.titleOrTagsLike(q),
                BookSpecifications.statusEquals(status),
                BookSpecifications.authorNameLike(author)
        ));
        return bookRepository.findAll(spec, Sort.by("sortableTitle").ascending())
                .stream()
                .map(mapper::toResponse)
                .map(o -> (Object) o)
                .toList();
    }
}

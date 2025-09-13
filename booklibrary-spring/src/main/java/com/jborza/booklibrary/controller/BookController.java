package com.jborza.booklibrary.controller;

import com.jborza.booklibrary.dto.BookRequest;
import com.jborza.booklibrary.service.BookService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/books/api")
public class BookController {
    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @PostMapping
    public Object create(@Valid @RequestBody BookRequest req) { return bookService.create(req); }

    @GetMapping("/{id}")
    public Object get(@PathVariable Long id) { return bookService.get(id); }

    @GetMapping("/search")
    public Object search(@RequestParam(required = false) String q,
                         @RequestParam(required = false) String status,
                         @RequestParam(required = false) String author) {
        return bookService.search(q, status, author);
    }
}

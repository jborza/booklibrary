package com.jborza.booklibrary.spec;

import com.jborza.booklibrary.domain.Book;
import org.springframework.data.jpa.domain.Specification;
import jakarta.persistence.criteria.Join;

import java.util.ArrayList;
import java.util.List;

public final class BookSpecifications {
    private BookSpecifications() { }

    public static Specification<Book> titleOrTagsLike(String query) {
        return (root, cq, cb) -> {
            if (query == null || query.isBlank()) return null;
            String like = "%" + query.toLowerCase() + "%";
            return cb.or(
                    cb.like(cb.lower(root.get("title")), like),
                    cb.like(cb.lower(root.get("tags")), like)
            );
        };
    }

    public static Specification<Book> statusEquals(String status) {
        return (root, cq, cb) -> {
            if (status == null || status.isBlank()) return null;
            return cb.equal(root.get("status"), status);
        };
    }

    public static Specification<Book> authorNameLike(String author) {
        return (root, cq, cb) -> {
            if (author == null || author.isBlank()) return null;
            String pattern = "%" + author.toLowerCase() + "%";
            Join<Object, Object> joinAuthor = root.join("author");
            return cb.or(
                    cb.like(cb.lower(joinAuthor.get("name")), pattern),
                    cb.like(cb.lower(joinAuthor.get("surname")), pattern)
            );
        };
    }

    public static Specification<Book> all(List<Specification<Book>> specs) {
        List<Specification<Book>> nonNull = new ArrayList<>();
        for (Specification<Book> s : specs) if (s != null) nonNull.add(s);
        if (nonNull.isEmpty()) return Specification.where(null);
        Specification<Book> result = nonNull.get(0);
        for (int i = 1; i < nonNull.size(); i++) {
            result = result.and(nonNull.get(i));
        }
        return result;
    }
}

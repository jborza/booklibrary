package com.jborza.booklibrary.repository;

import com.jborza.booklibrary.domain.Author;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AuthorRepository extends JpaRepository<Author, Long> { }

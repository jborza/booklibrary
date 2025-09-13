package com.jborza.booklibrary.repository;

import com.jborza.booklibrary.domain.Collection;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CollectionRepository extends JpaRepository<Collection, Long> { }

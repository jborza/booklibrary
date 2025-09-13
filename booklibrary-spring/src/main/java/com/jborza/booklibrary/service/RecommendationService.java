package com.jborza.booklibrary.service;

import com.jborza.booklibrary.repository.OtherBookRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RecommendationService {
    private final OtherBookRepository otherBookRepository;

    public RecommendationService(OtherBookRepository otherBookRepository) {
        this.otherBookRepository = otherBookRepository;
    }

    public List<?> recommendationsFor(Long bookId, int limit) {
        return otherBookRepository.findAll().stream().limit(limit).toList();
    }
}

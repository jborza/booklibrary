package com.jborza.booklibrary.controller;

import com.jborza.booklibrary.service.RecommendationService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/recommendations")
public class RecommendationController {
    private final RecommendationService recommendationService;

    public RecommendationController(RecommendationService recommendationService) {
        this.recommendationService = recommendationService;
    }

    @GetMapping("/{bookId}")
    public Object recommend(@PathVariable Long bookId) {
        return recommendationService.recommendationsFor(bookId, 5);
    }
}

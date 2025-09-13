package com.jborza.booklibrary.controller;

import com.jborza.booklibrary.service.DownloaderService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
@RequestMapping("/download_book_covers")
public class DownloaderController {
    private final DownloaderService downloaderService;

    public DownloaderController(DownloaderService downloaderService) {
        this.downloaderService = downloaderService;
    }

    @PostMapping
    public Map<String, Object> trigger() { return Map.of("processed", downloaderService.processOne()); }
}

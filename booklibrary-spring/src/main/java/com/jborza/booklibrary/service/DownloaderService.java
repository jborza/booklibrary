package com.jborza.booklibrary.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class DownloaderService {
    private static final Logger log = LoggerFactory.getLogger(DownloaderService.class);

    public boolean processOne() {
        log.debug("DownloaderService.processOne placeholder invoked");
        return false; // placeholder
    }
}

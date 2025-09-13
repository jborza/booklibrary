package com.jborza.booklibrary.scheduler;

import com.jborza.booklibrary.service.DownloaderService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class CoverDownloadScheduler {
    private static final Logger log = LoggerFactory.getLogger(CoverDownloadScheduler.class);
    private final DownloaderService downloaderService;

    public CoverDownloadScheduler(DownloaderService downloaderService) {
        this.downloaderService = downloaderService;
    }

    @Scheduled(fixedDelayString = "${covers.download.interval-ms:5000}")
    public void run() {
        boolean processed = downloaderService.processOne();
        if (processed) {
            log.debug("Processed one cover download task");
        }
    }
}

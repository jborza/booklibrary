package com.jborza.booklibrary;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class BookLibraryApplication {
    public static void main(String[] args) {
        SpringApplication.run(BookLibraryApplication.class, args);
    }
}

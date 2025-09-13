package com.jborza.booklibrary.dto;

public record BookResponse(
        Long id,
        String title,
        String sortableTitle,
        Long authorId,
        String authorName,
        String status,
        String tags,
        String remoteImageUrl
) { }

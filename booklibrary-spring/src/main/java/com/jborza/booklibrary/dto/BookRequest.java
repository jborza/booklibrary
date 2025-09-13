package com.jborza.booklibrary.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record BookRequest(
        @NotBlank String title,
        @NotNull Long authorId,
        String status,
        String tags,
        String remoteImageUrl
) { }

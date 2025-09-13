package com.jborza.booklibrary.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Entity
@Table(name = "books", indexes = {
        @Index(name = "idx_books_author", columnList = "author_id"),
        @Index(name = "idx_books_sortable_title", columnList = "sortable_title"),
        @Index(name = "idx_books_remote_image_url", columnList = "remote_image_url")
})
public class Book {

    private static final List<String> ARTICLES = List.of("a ", "an ", "the ");

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Author author;

    @Column(name = "status")
    private String status;

    @Column(name = "tags")
    private String tags;

    @Column(name = "remote_image_url")
    private String remoteImageUrl;

    @Column(name = "sortable_title", nullable = false)
    private String sortableTitle;

    @ManyToMany
    @JoinTable(name = "book_collection",
            joinColumns = @JoinColumn(name = "book_id"),
            inverseJoinColumns = @JoinColumn(name = "collection_id"))
    private Set<Collection> collections = new HashSet<>();

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    protected Book() { }

    public Book(String title, Author author, String status, String tags, String remoteImageUrl) {
        this.title = title;
        this.author = author;
        this.status = status;
        this.tags = tags;
        this.remoteImageUrl = remoteImageUrl;
        this.sortableTitle = computeSortableTitle(title);
    }

    @PrePersist
    @PreUpdate
    public void updateSortableTitle() {
        this.sortableTitle = computeSortableTitle(this.title);
    }

    public static String computeSortableTitle(String original) {
        if (original == null || original.isBlank()) return "";
        String lower = original.toLowerCase();
        for (String a : ARTICLES) {
            if (lower.startsWith(a)) {
                return original.substring(a.length()).trim();
            }
        }
        return original.trim();
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public Author getAuthor() { return author; }
    public String getStatus() { return status; }
    public String getTags() { return tags; }
    public String getRemoteImageUrl() { return remoteImageUrl; }
    public String getSortableTitle() { return sortableTitle; }
    public Set<Collection> getCollections() { return collections; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    public void setTitle(String title) { this.title = title; }
    public void setAuthor(Author author) { this.author = author; }
    public void setStatus(String status) { this.status = status; }
    public void setTags(String tags) { this.tags = tags; }
    public void setRemoteImageUrl(String remoteImageUrl) { this.remoteImageUrl = remoteImageUrl; }
    public void setCollections(Set<Collection> collections) { this.collections = collections; }
}

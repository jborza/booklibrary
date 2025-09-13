package com.jborza.booklibrary.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "other_books")
public class OtherBook {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String author;

    @Column
    private String source;

    protected OtherBook() { }

    public OtherBook(String title, String author, String source) {
        this.title = title;
        this.author = author;
        this.source = source;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public String getSource() { return source; }

    public void setTitle(String title) { this.title = title; }
    public void setAuthor(String author) { this.author = author; }
    public void setSource(String source) { this.source = source; }
}

package com.jborza.booklibrary.domain;

import jakarta.persistence.*;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "collections")
public class Collection {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @ManyToMany(mappedBy = "collections")
    private Set<Book> books = new HashSet<>();

    protected Collection() { }

    public Collection(String name) {
        this.name = name;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public Set<Book> getBooks() { return books; }

    public void setName(String name) { this.name = name; }
}

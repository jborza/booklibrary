package com.jborza.booklibrary.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "authors")
public class Author {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String surname;

    @Column(name = "surname_first", nullable = false)
    private String surnameFirst;

    protected Author() { }

    public Author(String name, String surname, String surnameFirst) {
        this.name = name;
        this.surname = surname;
        this.surnameFirst = surnameFirst;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getSurname() { return surname; }
    public String getSurnameFirst() { return surnameFirst; }

    public void setName(String name) { this.name = name; }
    public void setSurname(String surname) { this.surname = surname; }
    public void setSurnameFirst(String surnameFirst) { this.surnameFirst = surnameFirst; }
}

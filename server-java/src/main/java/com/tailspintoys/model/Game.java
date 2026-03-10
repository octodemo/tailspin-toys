package com.tailspintoys.model;

import jakarta.persistence.*;

@Entity
@Table(name = "games")
public class Game {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String title;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String description;

    @Column(name = "star_rating")
    private Double starRating;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "publisher_id", nullable = false)
    private Publisher publisher;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;

    public Game() {}

    public Game(String title, String description, Publisher publisher, Category category, Double starRating) {
        this.title = title;
        this.description = description;
        this.publisher = publisher;
        this.category = category;
        this.starRating = starRating;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Double getStarRating() { return starRating; }
    public void setStarRating(Double starRating) { this.starRating = starRating; }
    public Publisher getPublisher() { return publisher; }
    public void setPublisher(Publisher publisher) { this.publisher = publisher; }
    public Category getCategory() { return category; }
    public void setCategory(Category category) { this.category = category; }
}

package com.tailspintoys.repository;

import com.tailspintoys.model.Game;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameRepository extends JpaRepository<Game, Long> {

    /**
     * Fetch all games with publisher and category eagerly loaded.
     * Filtering is applied in the controller layer for reliability across
     * Hibernate versions.
     */
    @Query("""
            SELECT DISTINCT g FROM Game g
            LEFT JOIN FETCH g.publisher
            LEFT JOIN FETCH g.category
            """)
    List<Game> findAllWithDetails();

    /**
     * Fetch a single game by ID with publisher and category eagerly loaded.
     */
    @Query("""
            SELECT g FROM Game g
            LEFT JOIN FETCH g.publisher
            LEFT JOIN FETCH g.category
            WHERE g.id = :id
            """)
    Optional<Game> findByIdWithDetails(@Param("id") Long id);
}

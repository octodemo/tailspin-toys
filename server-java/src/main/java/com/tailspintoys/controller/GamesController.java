package com.tailspintoys.controller;

import com.tailspintoys.dto.GameDto;
import com.tailspintoys.model.Game;
import com.tailspintoys.repository.GameRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/games")
public class GamesController {

    private static final String DEFAULT_SORT = "rating";

    private final GameRepository gameRepository;

    public GamesController(GameRepository gameRepository) {
        this.gameRepository = gameRepository;
    }

    /**
     * GET /api/games
     * Returns all games, with optional filtering by publisher and category,
     * and sorting by rating (default, descending, nulls last) or title (ascending).
     */
    @GetMapping
    public List<GameDto> getGames(
            @RequestParam(required = false) String publisher,
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = DEFAULT_SORT) String sort) {

        // Normalise filter values: blank strings are treated as absent
        String publisherFilter = (publisher != null && !publisher.isBlank()) ? publisher.strip().toLowerCase() : null;
        String categoryFilter = (category != null && !category.isBlank()) ? category.strip().toLowerCase() : null;

        List<Game> games = new ArrayList<>(gameRepository.findAllWithDetails());

        // Apply filters in-memory (case-insensitive)
        if (publisherFilter != null) {
            final String pf = publisherFilter;
            games = games.stream()
                    .filter(g -> g.getPublisher() != null
                            && g.getPublisher().getName().toLowerCase().equals(pf))
                    .collect(Collectors.toCollection(ArrayList::new));
        }
        if (categoryFilter != null) {
            final String cf = categoryFilter;
            games = games.stream()
                    .filter(g -> g.getCategory() != null
                            && g.getCategory().getName().toLowerCase().equals(cf))
                    .collect(Collectors.toCollection(ArrayList::new));
        }

        // Apply sorting
        String sortKey = (sort != null) ? sort.strip().toLowerCase() : DEFAULT_SORT;
        Comparator<Game> comparator;
        if ("title".equals(sortKey)) {
            comparator = Comparator.comparing(Game::getTitle, String.CASE_INSENSITIVE_ORDER);
        } else {
            // Default: by rating descending with nulls last, then by title ascending
            comparator = Comparator.comparing(Game::getStarRating, Comparator.nullsLast(Comparator.reverseOrder()))
                    .thenComparing(Game::getTitle, String.CASE_INSENSITIVE_ORDER);
        }
        games.sort(comparator);

        return games.stream().map(GameDto::from).toList();
    }

    /**
     * GET /api/games/{id}
     * Returns a single game by ID, or 404 if not found.
     */
    @GetMapping("/{id}")
    public ResponseEntity<Object> getGame(@PathVariable Long id) {
        return gameRepository.findByIdWithDetails(id)
                .<ResponseEntity<Object>>map(game -> ResponseEntity.ok(GameDto.from(game)))
                .orElse(ResponseEntity.status(404).body(Map.of("error", "Game not found")));
    }
}

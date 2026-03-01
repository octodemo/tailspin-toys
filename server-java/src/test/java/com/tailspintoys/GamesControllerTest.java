package com.tailspintoys;

import com.tailspintoys.model.Category;
import com.tailspintoys.model.Game;
import com.tailspintoys.model.Publisher;
import com.tailspintoys.repository.CategoryRepository;
import com.tailspintoys.repository.GameRepository;
import com.tailspintoys.repository.PublisherRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import com.jayway.jsonpath.JsonPath;
import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for the GamesController.
 * Mirrors the scenarios from the Python test_games.py test suite.
 */
@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE",
    "spring.jpa.hibernate.ddl-auto=create-drop",
    "app.data-initialization.enabled=false"
})
class GamesControllerTest {

    private static final String BASE = "/api/games";

    @Autowired MockMvc mvc;
    @Autowired GameRepository gameRepo;
    @Autowired PublisherRepository pubRepo;
    @Autowired CategoryRepository catRepo;

    @BeforeEach
    void prepareDatabase() {
        gameRepo.deleteAll();
        pubRepo.deleteAll();
        catRepo.deleteAll();

        Publisher devGames = pubRepo.save(new Publisher("DevGames Inc", null));
        Publisher scrumMasters = pubRepo.save(new Publisher("Scrum Masters", null));
        Category strategy = catRepo.save(new Category("Strategy", null));
        Category cardGame = catRepo.save(new Category("Card Game", null));

        // Higher rated game (4.5) – DevGames Inc, Strategy
        gameRepo.save(new Game("Pipeline Panic",
            "Build your DevOps pipeline before chaos ensues", devGames, strategy, 4.5));
        // Lower rated game (4.2) – Scrum Masters, Card Game
        gameRepo.save(new Game("Agile Adventures",
            "Navigate your team through sprints and releases", scrumMasters, cardGame, 4.2));
    }

    // ── GET /api/games ──────────────────────────────────────────────────────

    @Test
    void listAll_succeeds() throws Exception {
        mvc.perform(get(BASE))
            .andExpect(status().isOk())
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$", hasSize(2)));
    }

    @Test
    void listAll_hasRequiredFields() throws Exception {
        mvc.perform(get(BASE))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].id").exists())
            .andExpect(jsonPath("$[0].title").exists())
            .andExpect(jsonPath("$[0].description").exists())
            .andExpect(jsonPath("$[0].publisher").exists())
            .andExpect(jsonPath("$[0].category").exists())
            .andExpect(jsonPath("$[0].starRating").exists());
    }

    @Test
    void listAll_defaultSort_ratingDescending() throws Exception {
        mvc.perform(get(BASE))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].title", is("Pipeline Panic")))
            .andExpect(jsonPath("$[1].title", is("Agile Adventures")));
    }

    @Test
    void listAll_sortByTitle_alphabetical() throws Exception {
        mvc.perform(get(BASE + "?sort=title"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].title", is("Agile Adventures")))
            .andExpect(jsonPath("$[1].title", is("Pipeline Panic")));
    }

    @Test
    void listAll_sortByRatingExplicit_highestFirst() throws Exception {
        mvc.perform(get(BASE + "?sort=rating"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].starRating", is(4.5)))
            .andExpect(jsonPath("$[1].starRating", is(4.2)));
    }

    @Test
    void listAll_unknownSort_fallsBackToRating() throws Exception {
        mvc.perform(get(BASE + "?sort=bogus"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].title", is("Pipeline Panic")));
    }

    @Test
    void listAll_publisherFilter_returnsSubset() throws Exception {
        mvc.perform(get(BASE).param("publisher", "DevGames Inc"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(1)))
            .andExpect(jsonPath("$[0].publisher.name", is("DevGames Inc")))
            .andExpect(jsonPath("$[0].title", is("Pipeline Panic")));
    }

    @Test
    void listAll_categoryFilter_returnsSubset() throws Exception {
        mvc.perform(get(BASE).param("category", "Card Game"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(1)))
            .andExpect(jsonPath("$[0].category.name", is("Card Game")))
            .andExpect(jsonPath("$[0].title", is("Agile Adventures")));
    }

    @Test
    void listAll_publisherAndCategoryFilter() throws Exception {
        mvc.perform(get(BASE).param("publisher", "DevGames Inc").param("category", "Strategy"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(1)))
            .andExpect(jsonPath("$[0].title", is("Pipeline Panic")));
    }

    @Test
    void listAll_noMatchingFilter_emptyArray() throws Exception {
        mvc.perform(get(BASE).param("publisher", "NoSuchPublisher").param("category", "NoSuchCategory"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void listAll_emptyDatabase_emptyArray() throws Exception {
        gameRepo.deleteAll();
        mvc.perform(get(BASE))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(0)));
    }

    // ── GET /api/games/{id} ─────────────────────────────────────────────────

    @Test
    void getById_found_returnsGame() throws Exception {
        MvcResult listing = mvc.perform(get(BASE)).andReturn();
        long firstId = ((Number) JsonPath.read(
            listing.getResponse().getContentAsString(), "$[0].id")).longValue();

        mvc.perform(get(BASE + "/" + firstId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.title", is("Pipeline Panic")))
            .andExpect(jsonPath("$.publisher.name", is("DevGames Inc")));
    }

    @Test
    void getById_missing_returns404() throws Exception {
        mvc.perform(get(BASE + "/99999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.error", is("Game not found")));
    }

    @Test
    void getById_nonNumericId_returns400() throws Exception {
        // Spring type-mismatch → 400; differs from Flask which returns 404
        mvc.perform(get(BASE + "/not-a-number"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.error").exists());
    }
}

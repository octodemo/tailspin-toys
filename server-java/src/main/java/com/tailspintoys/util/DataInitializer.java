package com.tailspintoys.util;

import com.opencsv.CSVReaderHeaderAware;
import com.tailspintoys.model.Category;
import com.tailspintoys.model.Game;
import com.tailspintoys.model.Publisher;
import com.tailspintoys.repository.CategoryRepository;
import com.tailspintoys.repository.GameRepository;
import com.tailspintoys.repository.PublisherRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Random;

/**
 * Seeds the database with game data from the bundled CSV file on first startup.
 * Disabled when {@code app.data-initialization.enabled=false} (e.g. in tests).
 */
@Component
@ConditionalOnProperty(name = "app.data-initialization.enabled", havingValue = "true", matchIfMissing = true)
public class DataInitializer implements CommandLineRunner {

    private final GameRepository gameRepository;
    private final PublisherRepository publisherRepository;
    private final CategoryRepository categoryRepository;

    public DataInitializer(GameRepository gameRepository,
                           PublisherRepository publisherRepository,
                           CategoryRepository categoryRepository) {
        this.gameRepository = gameRepository;
        this.publisherRepository = publisherRepository;
        this.categoryRepository = categoryRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        if (gameRepository.count() > 0) {
            return; // Database already seeded
        }

        Map<String, Publisher> publishers = new HashMap<>();
        Map<String, Category> categories = new HashMap<>();
        Random random = new Random(42); // Fixed seed for reproducibility

        try (var is = getClass().getResourceAsStream("/seed_data/games.csv");
             var reader = new CSVReaderHeaderAware(new InputStreamReader(Objects.requireNonNull(is)))) {

            Map<String, String> row;
            while ((row = reader.readMap()) != null) {
                String publisherName = row.get("Publisher");
                String categoryName = row.get("Category");
                String title = row.get("Title");
                String description = row.get("Description") + " Support this game through our crowdfunding platform!";

                // Find or create publisher
                Publisher publisher = publishers.computeIfAbsent(publisherName, name -> {
                    String desc = name + " is a game publisher seeking funding for exciting new titles";
                    return publisherRepository.save(new Publisher(name, desc));
                });

                // Find or create category
                Category category = categories.computeIfAbsent(categoryName, name -> {
                    String desc = "Collection of " + name + " games available for crowdfunding";
                    return categoryRepository.save(new Category(name, desc));
                });

                // Assign random star rating between 3.0 and 5.0 (one decimal place)
                double starRating = Math.round((3.0 + random.nextDouble() * 2.0) * 10.0) / 10.0;

                gameRepository.save(new Game(title, description, publisher, category, starRating));
            }
        }
    }
}

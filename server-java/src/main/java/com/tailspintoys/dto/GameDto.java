package com.tailspintoys.dto;

import com.tailspintoys.model.Game;

public record GameDto(
        Long id,
        String title,
        String description,
        PublisherSummaryDto publisher,
        CategorySummaryDto category,
        Double starRating) {

    public static GameDto from(Game game) {
        return new GameDto(
                game.getId(),
                game.getTitle(),
                game.getDescription(),
                PublisherSummaryDto.from(game.getPublisher()),
                CategorySummaryDto.from(game.getCategory()),
                game.getStarRating());
    }
}

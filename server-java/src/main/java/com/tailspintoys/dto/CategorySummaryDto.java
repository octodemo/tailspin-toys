package com.tailspintoys.dto;

public record CategorySummaryDto(Long id, String name) {

    public static CategorySummaryDto from(com.tailspintoys.model.Category category) {
        if (category == null) return null;
        return new CategorySummaryDto(category.getId(), category.getName());
    }
}

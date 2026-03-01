package com.tailspintoys.dto;

public record PublisherSummaryDto(Long id, String name) {

    public static PublisherSummaryDto from(com.tailspintoys.model.Publisher publisher) {
        if (publisher == null) return null;
        return new PublisherSummaryDto(publisher.getId(), publisher.getName());
    }
}

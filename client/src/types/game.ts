/**
 * Centralized type definitions for game-related data structures.
 * These interfaces match the API response format from the Flask backend.
 */

/**
 * Represents a game publisher
 */
export interface Publisher {
    id: number;
    name: string;
    description?: string | null;
    game_count?: number;
}

/**
 * Represents a game category
 */
export interface Category {
    id: number;
    name: string;
    description?: string | null;
    game_count?: number;
}

/**
 * Represents a game as returned by the API
 */
export interface Game {
    id: number;
    title: string;
    description: string;
    publisher: Publisher | null;
    category: Category | null;
    starRating: number | null;
    isArchived: boolean;
}

/**
 * Payload sent to the API when creating or updating a game
 */
export interface GameInput {
    title: string;
    description: string;
    publisherId: number;
    categoryId: number;
    starRating: number | null;
}

/**
 * Admin authentication state reported by the API
 */
export interface AdminSession {
    authenticated: boolean;
}

/**
 * Response wrapper for the publisher lookup endpoint
 */
export interface PublishersResponse {
    publishers: Publisher[];
}

/**
 * Response wrapper for the category lookup endpoint
 */
export interface CategoriesResponse {
    categories: Category[];
}

/**
 * Pagination metadata returned by the API
 */
export interface Pagination {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
}

/**
 * Paginated response wrapper for game listings
 */
export interface PaginatedGamesResponse {
    games: Game[];
    pagination: Pagination;
}

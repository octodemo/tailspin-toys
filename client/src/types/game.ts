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
}

/**
 * Represents a game category
 */
export interface Category {
    id: number;
    name: string;
}

/**
 * Represents a stretch goal for a game
 */
export interface StretchGoal {
    id: number;
    title: string;
    description: string;
    goalType: 'pledge_total' | 'pledge_count';
    targetAmount: number;
    currentAmount: number;
    progressPercentage: number;
    isAchieved: boolean;
    gameId: number;
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
    stretchGoals?: StretchGoal[];
}

/**
 * Utility for managing "supported" game state via localStorage.
 * Supported game IDs are persisted locally without requiring any backend changes.
 */

const STORAGE_KEY = 'supported_games';

function getSupportedIds(): Set<number> {
    if (typeof localStorage === 'undefined') return new Set();
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (!stored) return new Set();
        return new Set(JSON.parse(stored) as number[]);
    } catch {
        return new Set();
    }
}

function saveSupportedIds(ids: Set<number>): void {
    if (typeof localStorage === 'undefined') return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]));
}

/**
 * Returns true if the given game ID is marked as supported.
 */
export function isSupported(gameId: number): boolean {
    return getSupportedIds().has(gameId);
}

/**
 * Toggles the support state for a game.
 * Returns the new supported state (true = now supported, false = no longer supported).
 */
export function toggleSupport(gameId: number): boolean {
    const ids = getSupportedIds();
    if (ids.has(gameId)) {
        ids.delete(gameId);
        saveSupportedIds(ids);
        return false;
    } else {
        ids.add(gameId);
        saveSupportedIds(ids);
        return true;
    }
}

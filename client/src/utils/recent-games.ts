import type { Game } from '../types/game';

export interface RecentPerusedGame {
    id: number;
    title: string;
}

const RECENT_PERUSED_GAMES_STORAGE_KEY = 'tailspin-recent-perused-games';
const RECENT_PERUSED_GAMES_LIMIT = 5;
const RECENT_PERUSED_GAMES_UPDATED_EVENT = 'tailspin:recent-perused-games-updated';

function isRecentPerusedGame(value: unknown): value is RecentPerusedGame {
    if (typeof value !== 'object' || value === null) {
        return false;
    }

    const maybeGame = value as { id?: unknown; title?: unknown };
    return typeof maybeGame.id === 'number' && typeof maybeGame.title === 'string';
}

export function getRecentPerusedGames(): RecentPerusedGame[] {
    if (typeof window === 'undefined') {
        return [];
    }

    const storedValue = window.localStorage.getItem(RECENT_PERUSED_GAMES_STORAGE_KEY);
    if (!storedValue) {
        return [];
    }

    try {
        const parsedValue: unknown = JSON.parse(storedValue);
        if (!Array.isArray(parsedValue)) {
            return [];
        }

        return parsedValue.filter(isRecentPerusedGame).slice(0, RECENT_PERUSED_GAMES_LIMIT);
    } catch (error) {
        console.error('Unable to parse recent perused games from localStorage', error);
        return [];
    }
}

export function addRecentPerusedGame(game: Pick<Game, 'id' | 'title'>): void {
    if (typeof window === 'undefined') {
        return;
    }

    const dedupedRecentGames = getRecentPerusedGames().filter((recentGame) => recentGame.id !== game.id);
    const nextRecentGames: RecentPerusedGame[] = [{ id: game.id, title: game.title }, ...dedupedRecentGames]
        .slice(0, RECENT_PERUSED_GAMES_LIMIT);

    window.localStorage.setItem(RECENT_PERUSED_GAMES_STORAGE_KEY, JSON.stringify(nextRecentGames));
    window.dispatchEvent(new CustomEvent<RecentPerusedGame[]>(RECENT_PERUSED_GAMES_UPDATED_EVENT, {
        detail: nextRecentGames
    }));
}

export function subscribeToRecentPerusedGames(
    onRecentGamesChange: (recentGames: RecentPerusedGame[]) => void
): () => void {
    if (typeof window === 'undefined') {
        return () => {};
    }

    const handleRecentGamesUpdate = (event: Event): void => {
        if (event instanceof CustomEvent && Array.isArray(event.detail)) {
            onRecentGamesChange(event.detail.filter(isRecentPerusedGame).slice(0, RECENT_PERUSED_GAMES_LIMIT));
            return;
        }

        onRecentGamesChange(getRecentPerusedGames());
    };

    const handleStorageUpdate = (event: StorageEvent): void => {
        if (event.key !== RECENT_PERUSED_GAMES_STORAGE_KEY) {
            return;
        }

        onRecentGamesChange(getRecentPerusedGames());
    };

    window.addEventListener(RECENT_PERUSED_GAMES_UPDATED_EVENT, handleRecentGamesUpdate);
    window.addEventListener('storage', handleStorageUpdate);

    return () => {
        window.removeEventListener(RECENT_PERUSED_GAMES_UPDATED_EVENT, handleRecentGamesUpdate);
        window.removeEventListener('storage', handleStorageUpdate);
    };
}

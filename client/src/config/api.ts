/** Base path for client-side API requests (goes through Astro proxy) */
export const API_BASE = '/api';

/** API endpoint paths */
export const API_ENDPOINTS = {
  games: `${API_BASE}/games`,
  gameById: (id: number | string) => `${API_BASE}/games/${id}`,
} as const;

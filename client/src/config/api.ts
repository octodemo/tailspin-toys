/** Base path for client-side API requests (goes through Astro proxy) */
export const API_BASE = '/api';

/** API endpoint paths */
export const API_ENDPOINTS = {
  games: `${API_BASE}/games`,
  gameById: (id: number | string) => `${API_BASE}/games/${id}`,
  gameRestore: (id: number | string) => `${API_BASE}/games/${id}/restore`,
  publishers: `${API_BASE}/publishers`,
  categories: `${API_BASE}/categories`,
  login: `${API_BASE}/login`,
  logout: `${API_BASE}/logout`,
  session: `${API_BASE}/session`,
} as const;

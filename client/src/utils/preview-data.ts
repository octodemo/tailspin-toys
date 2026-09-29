import type { Game, PaginatedGamesResponse } from '../types/game';

/**
 * Server-side API base. Preview pages render on the server, so they talk to
 * Flask directly rather than going through the browser-facing /api proxy.
 */
const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';

/** Fetch the published catalog for server-rendered pages. Returns [] on failure. */
export async function fetchGames(pageSize = 100): Promise<Game[]> {
  try {
    const response = await fetch(`${API_SERVER_URL}/api/games?pageSize=${pageSize}`);
    if (!response.ok) return [];

    const data: PaginatedGamesResponse = await response.json();
    return data.games;
  } catch {
    return [];
  }
}

/**
 * Illustrative funding figures for the design previews.
 *
 * The catalog has no funding columns yet, but a crowdfunding layout cannot be
 * evaluated without them. These are derived deterministically from the game id
 * so the previews are stable across reloads — they are placeholders for layout,
 * not real pledges.
 */
export interface FundingSnapshot {
  backers: number;
  pledged: number;
  goal: number;
  percent: number;
  daysLeft: number;
  stage: 'Concept' | 'Prototype' | 'Production';
}

export function fundingFor(game: Game): FundingSnapshot {
  // Integer avalanche hash so the derived values spread evenly across the
  // catalog instead of clustering, which a simple shift-and-mod does.
  const hash = (input: number): number => {
    let h = (input * 2654435761) >>> 0;
    h ^= h >>> 15;
    h = Math.imul(h, 2246822519) >>> 0;
    h ^= h >>> 13;
    h = Math.imul(h, 3266489917) >>> 0;
    h ^= h >>> 16;
    return h >>> 0;
  };

  const percent = 18 + (hash(game.id) % 135);
  const goal = 15000 + (hash(game.id + 101) % 8) * 5000;
  const pledged = Math.round((goal * percent) / 100);
  const backers = 40 + (hash(game.id + 202) % 900);
  const daysLeft = 2 + (hash(game.id + 303) % 40);

  const stage: FundingSnapshot['stage'] =
    percent >= 100 ? 'Production' : percent >= 60 ? 'Prototype' : 'Concept';

  return { backers, pledged, goal, percent, daysLeft, stage };
}

export const formatCurrency = (value: number): string =>
  `$${value.toLocaleString('en-US')}`;

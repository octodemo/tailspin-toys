import type { Game, PaginatedGamesResponse } from '../types/game';

export type FundingStage = 'Concept' | 'Prototype' | 'Production';

export interface PreviewGame extends Game {
  funding: {
    backers: number;
    goal: number;
    pledged: number;
    progress: number;
    stage: FundingStage;
  };
  previewRating: number;
}

const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';
const STAGES: FundingStage[] = ['Concept', 'Prototype', 'Production'];

export async function getPreviewGames(): Promise<PreviewGame[]> {
  const response = await fetch(`${API_SERVER_URL}/api/games?pageSize=100`);

  if (!response.ok) {
    throw new Error(`Unable to load preview catalog: ${response.status} ${response.statusText}`);
  }

  const data: PaginatedGamesResponse = await response.json();
  return data.games.map(toPreviewGame);
}

function toPreviewGame(game: Game): PreviewGame {
  const goal = 18000 + ((game.id * 7919) % 32000);
  const progress = 34 + ((game.id * 47) % 128);
  const pledged = Math.round((goal * progress) / 100);

  return {
    ...game,
    funding: {
      backers: 120 + ((game.id * 613) % 4200),
      goal,
      pledged,
      progress,
      stage: STAGES[game.id % STAGES.length],
    },
    previewRating: game.starRating ?? 3.5 + ((game.id * 17) % 15) / 10,
  };
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

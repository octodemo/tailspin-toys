import type { Game } from '../types/game';

/**
 * Display-face candidates for the Tabletop direction.
 *
 * Anton is the original pick. It is a single-weight condensed face with no true
 * bold, so it cannot be pushed heavier and its spacing tightens up badly at
 * display sizes. Every alternative below ships real weights (or, for Alfa Slab
 * One, is already a heavy display face by design) and holds up large.
 *
 * Each face needs its own size and tracking correction: swapping families at a
 * fixed size would compare the faces unfairly, since a condensed face sets much
 * smaller on the page than an expanded one at the same point size.
 */
export interface TypeOption {
  id: string;
  name: string;
  stack: string;
  weight: number;
  /** Multiplier applied to display sizes so each face occupies similar space. */
  scale: number;
  tracking: string;
  /** Optional variation settings, used for the variable width and optical axes. */
  variation?: string;
  note: string;
  weightsAvailable: string;
}

export const TYPE_OPTIONS: TypeOption[] = [
  {
    id: 'anton',
    name: 'Anton',
    stack: "'Anton', sans-serif",
    weight: 400,
    scale: 1,
    tracking: '0.005em',
    note: 'The original. One weight only, so there is no heavier option, and the sidebearings get tight at large sizes.',
    weightsAvailable: 'Regular only',
  },
  {
    id: 'big-shoulders',
    name: 'Big Shoulders Display',
    stack: "'Big Shoulders Display', sans-serif",
    weight: 800,
    scale: 1.06,
    tracking: '0.012em',
    note: 'Closest to Anton in silhouette but drawn for posters, with a full weight range. Crisp corners hold up at 80px and beyond.',
    weightsAvailable: 'Thin to Black (variable)',
  },
  {
    id: 'barlow-condensed',
    name: 'Barlow Condensed',
    stack: "'Barlow Condensed', sans-serif",
    weight: 800,
    scale: 0.97,
    tracking: '0.005em',
    note: 'Condensed and slightly rounded, so long titles fit without feeling brittle. Reads warmer than Anton at the same width.',
    weightsAvailable: 'Thin to Black',
  },
  {
    id: 'archivo',
    name: 'Archivo (semi-expanded)',
    stack: "'Archivo', sans-serif",
    weight: 700,
    scale: 0.72,
    tracking: '-0.015em',
    variation: "'wdth' 112",
    note: 'Sturdy and wide rather than condensed. The most confident of the set at large sizes, but long titles wrap onto more lines.',
    weightsAvailable: 'Regular to Bold, plus a width axis',
  },
  {
    id: 'alfa-slab',
    name: 'Alfa Slab One',
    stack: "'Alfa Slab One', serif",
    weight: 400,
    scale: 0.72,
    tracking: '-0.005em',
    note: 'Heavy slab serif with real vintage game-box character. Already very bold by design, which suits the cardboard palette. Wide, so long titles run to two lines.',
    weightsAvailable: 'Regular only, but heavy by design',
  },
  {
    id: 'bricolage',
    name: 'Bricolage Grotesque',
    stack: "'Bricolage Grotesque', sans-serif",
    weight: 800,
    scale: 0.79,
    tracking: '-0.025em',
    variation: "'opsz' 96",
    note: 'Has an optical-size axis, so the large setting is a genuinely different drawing rather than a scaled-up small one. The most characterful option.',
    weightsAvailable: 'Light to ExtraBold (variable, with optical size)',
  },
];

export const DEFAULT_TYPE_ID = 'big-shoulders';

/** One stylesheet request covering every candidate, so switching is instant. */
export const TYPE_FONTS_HREF =
  'https://fonts.googleapis.com/css2' +
  '?family=Anton' +
  '&family=Alfa+Slab+One' +
  '&family=Archivo:wdth,wght@62..125,400..700' +
  '&family=Barlow+Condensed:wght@600;700;800' +
  '&family=Big+Shoulders+Display:wght@400..900' +
  '&family=Bricolage+Grotesque:opsz,wght@12..96,400..800' +
  '&family=Karla:wght@400;500;700' +
  '&family=Space+Mono:wght@400;700' +
  '&display=swap';

export function resolveTypeId(requested: string | null): string {
  return TYPE_OPTIONS.some((option) => option.id === requested)
    ? (requested as string)
    : DEFAULT_TYPE_ID;
}

/**
 * Emit the per-face custom properties.
 *
 * The selector is attribute-only, not `html[data-type]`, so the same rules work
 * whether the attribute sits on `<html>` (the layout page, switching the whole
 * design) or on individual sections (the specimen page, showing all faces at once).
 */
export function typeOptionCss(): string {
  return TYPE_OPTIONS.map(
    (option) => `
[data-type='${option.id}'] {
  --display: ${option.stack};
  --display-weight: ${option.weight};
  --display-scale: ${option.scale};
  --display-tracking: ${option.tracking};
  --display-variation: ${option.variation ?? 'normal'};
}`,
  ).join('\n');
}

/** Long and short titles from the real catalog, for testing how each face sets. */
export function specimenTitles(games: Game[]): { long: string; short: string } {
  const sorted = [...games].sort((a, b) => a.title.length - b.title.length);

  return {
    short: sorted[0]?.title ?? 'Repo Rulers',
    long: sorted[sorted.length - 1]?.title ?? 'Digital Debugger\u2019s Dream',
  };
}

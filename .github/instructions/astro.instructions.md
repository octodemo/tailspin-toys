---
description: 'Astro component patterns for pages, layouts, and routing'
applyTo: '**/*.astro'
---

# Astro Component Instructions

## Astro Component Patterns

Astro is used for page routing, layouts, and static content. Svelte components handle interactivity.

### Component Structure

```astro
---
// Frontmatter: Server-side code (runs at request time in SSR mode)
import Layout from '../layouts/Layout.astro';
import Component from '../components/Component.svelte';

interface Props {
  title: string;
  description?: string;
}

const { title, description } = Astro.props;
---

<Layout title={title}>
  <!-- HTML content -->
  <Component client:load />
</Layout>
```

## Layouts

- Create reusable layout components in `src/layouts/`
- Use `<slot />` for content injection
- Include common elements: `<head>`, navigation, footer
- Import global styles in layouts

### Layout Example

```astro
---
interface Props {
  title: string;
}
const { title } = Astro.props;
---

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>{title}</title>
  </head>
  <body>
    <slot />
  </body>
</html>
```

## Pages

- Create pages in `src/pages/`
- File-based routing: `src/pages/about.astro` → `/about`
- Dynamic routes: `src/pages/game/[id].astro`

### Dynamic Routes

With `output: 'server'` (SSR mode), dynamic routes use request-time parameters instead of `getStaticPaths()`:

```astro
---
const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';
const { id } = Astro.params;
const response = await fetch(`${API_SERVER_URL}/api/games/${id}`);
const game = await response.json();
---

<Layout title={game.title}>
  <!-- Game details -->
</Layout>
```

## Svelte Integration

Use client directives to control hydration:

- `client:load` - Hydrates immediately on page load (preferred for SSR components)
- `client:only="svelte"` - Only runs on client, no server rendering
- `client:visible` - Hydrates when component becomes visible
- `client:idle` - Hydrates when browser is idle

### Example

```astro
---
import GameList from '../components/GameList.svelte';
const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';
const response = await fetch(`${API_SERVER_URL}/api/games`);
const games = await response.json();
---

<Layout>
  <GameList client:load {games} />
</Layout>
```

## Server Endpoints

Server endpoints handle API proxying. The catch-all endpoint at `src/pages/api/[...path].ts` streams requests to the Flask backend, keeping API calls internal to the server.

## TypeScript

- Use TypeScript for type-safe props
- Define `Props` interface in frontmatter
- Type component imports

## Best Practices

- Keep Astro components for static content and routing
- Use Svelte for interactivity and client-side state
- Minimize client-side JavaScript by leveraging SSR data fetching in Astro frontmatter
- Import and use global CSS styles from layouts

<script lang="ts">
    import { onMount } from 'svelte';
    import { getRecentPerusedGames, type RecentPerusedGame } from '../utils/recent-games';

    let recentGames = $state<RecentPerusedGame[]>([]);

    onMount(() => {
        recentGames = getRecentPerusedGames();
    });
</script>

<div class="rounded-xl border border-slate-700 bg-slate-800/60 p-5 shadow-lg" data-testid="recent-games-breadcrumb">
    <h2 class="text-lg font-semibold text-slate-100">Recently Perused</h2>

    {#if recentGames.length === 0}
        <p class="mt-3 text-sm text-slate-400" data-testid="recent-games-empty">
            Peruse a few games and they&apos;ll show up here.
        </p>
    {:else}
        <nav class="mt-4" aria-label="Recently perused games breadcrumb">
            <ol class="space-y-2" data-testid="recent-games-list">
                {#each recentGames as recentGame, index (recentGame.id)}
                    <li class="flex items-center gap-2 text-sm text-slate-300">
                        {#if index > 0}
                            <span aria-hidden="true" class="text-slate-500">›</span>
                        {/if}
                        <a
                            href={`/game/${recentGame.id}`}
                            class="truncate font-semibold text-blue-300 transition-colors duration-200 hover:text-blue-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            data-testid={`recent-game-link-${recentGame.id}`}
                        >
                            {recentGame.title}
                        </a>
                    </li>
                {/each}
            </ol>
        </nav>
    {/if}
</div>

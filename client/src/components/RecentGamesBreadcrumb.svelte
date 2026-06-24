<script lang="ts">
    import { onMount } from 'svelte';
    import {
        getRecentPerusedGames,
        subscribeToRecentPerusedGames,
        type RecentPerusedGame
    } from '../utils/recent-games';

    let {
        currentGameId = undefined,
        heading = 'Recently visited',
        showCard = true,
        showHomeLink = false
    }: {
        currentGameId?: number;
        heading?: string;
        showCard?: boolean;
        showHomeLink?: boolean;
    } = $props();

    let recentGames = $state<RecentPerusedGame[]>([]);

    let containerClasses = $derived(
        showCard
            ? 'rounded-xl border border-slate-700 bg-slate-800/60 p-5 shadow-lg'
            : 'rounded-xl border border-slate-700/80 bg-slate-900/70 p-4 shadow-md'
    );

    function loadRecentGames(): void {
        recentGames = getRecentPerusedGames();
    }

    onMount(() => {
        loadRecentGames();
        return subscribeToRecentPerusedGames((nextRecentGames) => {
            recentGames = nextRecentGames;
        });
    });
</script>

<div class={containerClasses} data-testid="recent-games-breadcrumb">
    <h2 class="text-lg font-semibold text-slate-100">{heading}</h2>

    {#if recentGames.length === 0}
        <p class="mt-3 text-sm text-slate-400" data-testid="recent-games-empty">
            Visit a few games and they&apos;ll show up here.
        </p>
    {:else}
        <nav class="mt-4" aria-label={`${heading} breadcrumb`}>
            <ol class="flex flex-wrap items-center gap-x-2 gap-y-3 text-sm text-slate-300" data-testid="recent-games-list">
                {#if showHomeLink}
                    <li class="flex items-center gap-2">
                        <a
                            href="/"
                            class="font-semibold text-blue-200 transition-colors duration-200 hover:text-blue-100 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            data-testid="recent-games-home-link"
                        >
                            Home
                        </a>
                        <span aria-hidden="true" class="text-slate-500">›</span>
                    </li>
                {/if}

                {#each recentGames as recentGame, index (recentGame.id)}
                    <li class="flex items-center gap-2" data-testid={`recent-game-item-${recentGame.id}`}>
                        {#if index > 0}
                            <span aria-hidden="true" class="text-slate-500">›</span>
                        {/if}
                        <a
                            href={`/game/${recentGame.id}`}
                            class={`truncate font-semibold transition-colors duration-200 focus:ring-2 focus:ring-blue-500 focus:outline-none ${
                                currentGameId === recentGame.id
                                    ? 'text-slate-100 underline decoration-blue-400 underline-offset-4'
                                    : 'text-blue-200 hover:text-blue-100'
                            }`}
                            data-testid={`recent-game-link-${recentGame.id}`}
                            aria-current={currentGameId === recentGame.id ? 'page' : undefined}
                        >
                            {recentGame.title}
                        </a>
                    </li>
                {/each}
            </ol>
        </nav>
    {/if}
</div>

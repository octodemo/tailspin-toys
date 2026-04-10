<script lang="ts">
    import { onMount } from "svelte";
    import type { Game, PaginatedGamesResponse } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';
    import GameCard from "./GameCard.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";

    let loading = $state(true);
    let error = $state<string | null>(null);
    let games = $state<Game[]>([]);

    let currentPage = $state(1);
    let totalPages = $state(1);
    let totalGames = $state(0);

    const fetchGames = async (page: number = 1) => {
        loading = true;
        error = null;
        try {
            // eslint-disable-next-line svelte/prefer-svelte-reactivity -- local variable, not reactive state
            const queryParams = new URLSearchParams();
            queryParams.set('page', String(page));

            const endpoint = `${API_ENDPOINTS.games}?${queryParams.toString()}`;

            const response = await fetch(endpoint);
            if(response.ok) {
                const data: PaginatedGamesResponse = await response.json();
                games = data.games;
                currentPage = data.pagination.page;
                totalPages = data.pagination.totalPages;
                totalGames = data.pagination.total;
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const goToPage = async (page: number) => {
        await fetchGames(page);
    };

    onMount(() => {
        fetchGames();
    });
</script>

<div>
    <h2 class="text-2xl font-medium mb-6 text-slate-100">Featured Games</h2>
    
    {#if loading}
        <LoadingSkeleton count={6} />
    {:else if error}
        <ErrorMessage error={error} />
    {:else if games.length === 0}
        <EmptyState message="No games available at the moment." />
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each games as game (game.id)}
                <GameCard {game} />
            {/each}
        </div>

        {#if totalPages > 1}
            <nav class="flex items-center justify-center gap-4 mt-8" aria-label="Pagination" data-testid="pagination">
                <button
                    class="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200
                        {currentPage <= 1
                            ? 'bg-slate-800 text-slate-400 cursor-not-allowed'
                            : 'bg-slate-700 text-slate-100 hover:bg-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none'}"
                    disabled={currentPage <= 1}
                    onclick={() => goToPage(currentPage - 1)}
                    data-testid="pagination-prev"
                    aria-label="Go to previous page"
                >
                    ← Previous
                </button>

                <span class="text-sm text-slate-300" data-testid="pagination-info">
                    Page {currentPage} of {totalPages}
                    <span class="text-slate-400">({totalGames} games)</span>
                </span>

                <button
                    class="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200
                        {currentPage >= totalPages
                            ? 'bg-slate-800 text-slate-400 cursor-not-allowed'
                            : 'bg-slate-700 text-slate-100 hover:bg-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none'}"
                    disabled={currentPage >= totalPages}
                    onclick={() => goToPage(currentPage + 1)}
                    data-testid="pagination-next"
                    aria-label="Go to next page"
                >
                    Next →
                </button>
            </nav>
        {/if}
    {/if}
</div>
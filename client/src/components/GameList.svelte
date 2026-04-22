<script lang="ts">
    import { onMount } from "svelte";
    import type { Game, PaginatedGamesResponse } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';
    import GameCard from "./GameCard.svelte";
    import FilterBar from "./FilterBar.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";

    let loading = $state(true);
    let error = $state<string | null>(null);
    let games = $state<Game[]>([]);

    let currentPage = $state(1);
    let totalPages = $state(1);
    let totalGames = $state(0);

    let selectedCategory = $state('');
    let selectedPublisher = $state('');
    let abortController = $state<AbortController | null>(null);

    let hasActiveFilters = $derived(selectedCategory !== '' || selectedPublisher !== '');

    const fetchGames = async (page: number = 1) => {
        // Cancel any in-flight request
        if (abortController) {
            abortController.abort();
        }
        const controller = new AbortController();
        abortController = controller;

        loading = true;
        error = null;
        try {
            // eslint-disable-next-line svelte/prefer-svelte-reactivity -- local variable, not reactive state
            const queryParams = new URLSearchParams();
            queryParams.set('page', String(page));
            if (selectedCategory) queryParams.set('category', selectedCategory);
            if (selectedPublisher) queryParams.set('publisher', selectedPublisher);

            const endpoint = `${API_ENDPOINTS.games}?${queryParams.toString()}`;

            const response = await fetch(endpoint, { signal: controller.signal });
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
            if (err instanceof DOMException && err.name === 'AbortError') return;
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            if (!controller.signal.aborted) {
                loading = false;
            }
        }
    };

    const goToPage = async (page: number) => {
        await fetchGames(page);
    };

    const handleFilterChange = async (filters: { category: string; publisher: string }) => {
        selectedCategory = filters.category;
        selectedPublisher = filters.publisher;
        await fetchGames(1);
    };

    const clearFilters = async () => {
        selectedCategory = '';
        selectedPublisher = '';
        await fetchGames(1);
    };

    onMount(() => {
        fetchGames();
    });
</script>

<div>
    <h2 class="text-2xl font-medium mb-6 text-slate-100">Featured Games</h2>

    <FilterBar onFilterChange={handleFilterChange} />
    
    {#if loading}
        <LoadingSkeleton count={6} />
    {:else if error}
        <ErrorMessage error={error} />
    {:else if games.length === 0 && hasActiveFilters}
        <div class="text-center py-12" data-testid="filtered-empty-state">
            <p class="text-slate-300 text-lg mb-4">No games match your current filters.</p>
            <button
                class="px-4 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-500 transition-colors duration-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                onclick={clearFilters}
                data-testid="clear-filters-button"
            >
                Clear Filters
            </button>
        </div>
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
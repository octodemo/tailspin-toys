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
    let filteredGames = $state<Game[]>([]);
    let selectedPublisher = $state('all');
    let selectedCategory = $state('all');
    let selectedSort = $state('rating');

    let publisherOptions = $state<string[]>([]);
    let categoryOptions = $state<string[]>([]);

    let currentPage = $state(1);
    let totalPages = $state(1);
    let totalGames = $state(0);

    const fetchGames = async (publisher: string = 'all', category: string = 'all', sort: string = 'rating', page: number = 1) => {
        loading = true;
        error = null;
        try {
            // eslint-disable-next-line svelte/prefer-svelte-reactivity -- local variable, not reactive state
            const queryParams = new URLSearchParams();
            if (publisher !== 'all') {
                queryParams.set('publisher', publisher);
            }
            if (category !== 'all') {
                queryParams.set('category', category);
            }
            queryParams.set('sort', sort);
            queryParams.set('page', String(page));

            const endpoint = `${API_ENDPOINTS.games}?${queryParams.toString()}`;

            const response = await fetch(endpoint);
            if(response.ok) {
                const data: PaginatedGamesResponse = await response.json();
                filteredGames = data.games;
                currentPage = data.pagination.page;
                totalPages = data.pagination.totalPages;
                totalGames = data.pagination.total;
                publisherOptions = data.filters.publishers;
                categoryOptions = data.filters.categories;
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const syncFromUrl = () => {
        const params = new URLSearchParams(window.location.search);
        selectedPublisher = params.get('publisher') || 'all';
        selectedCategory = params.get('category') || 'all';
        selectedSort = params.get('sort') || 'rating';
        currentPage = Math.max(1, parseInt(params.get('page') || '1', 10));
    };

    const syncToUrl = (publisher: string, category: string, sort: string, page: number) => {
        // eslint-disable-next-line svelte/prefer-svelte-reactivity -- local variable, not reactive state
        const params = new URLSearchParams();
        if (publisher !== 'all') params.set('publisher', publisher);
        if (category !== 'all') params.set('category', category);
        if (sort !== 'rating') params.set('sort', sort);
        if (page > 1) params.set('page', String(page));
        const newUrl = params.toString() ? `?${params.toString()}` : window.location.pathname;
        history.pushState(null, '', newUrl);
    };

    const onFilterChange = async () => {
        currentPage = 1;
        syncToUrl(selectedPublisher, selectedCategory, selectedSort, 1);
        await fetchGames(selectedPublisher, selectedCategory, selectedSort, 1);
    };

    const goToPage = async (page: number) => {
        syncToUrl(selectedPublisher, selectedCategory, selectedSort, page);
        await fetchGames(selectedPublisher, selectedCategory, selectedSort, page);
    };

    onMount(() => {
        syncFromUrl();
        fetchGames(selectedPublisher, selectedCategory, selectedSort, currentPage);
    });
</script>

<div>
    <h2 class="text-2xl font-medium mb-6 text-slate-100">Featured Games</h2>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6" data-testid="games-filters">
        <div>
            <label class="block text-sm font-medium text-slate-300 mb-2" for="publisher-filter">Publisher</label>
            <select
                id="publisher-filter"
                class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="publisher-filter"
                bind:value={selectedPublisher}
                onchange={onFilterChange}
            >
                <option value="all">All Publishers</option>
                {#each publisherOptions as publisher (publisher)}
                    <option value={publisher}>{publisher}</option>
                {/each}
            </select>
        </div>

        <div>
            <label class="block text-sm font-medium text-slate-300 mb-2" for="category-filter">Category</label>
            <select
                id="category-filter"
                class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="category-filter"
                bind:value={selectedCategory}
                onchange={onFilterChange}
            >
                <option value="all">All Categories</option>
                {#each categoryOptions as category (category)}
                    <option value={category}>{category}</option>
                {/each}
            </select>
        </div>

        <div>
            <label class="block text-sm font-medium text-slate-300 mb-2" for="sort-select">Sort By</label>
            <select
                id="sort-select"
                class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="sort-select"
                bind:value={selectedSort}
                onchange={onFilterChange}
            >
                <option value="rating">Top Rated</option>
                <option value="title">Title (A-Z)</option>
            </select>
        </div>
    </div>
    
    {#if loading}
        <LoadingSkeleton count={6} />
    {:else if error}
        <ErrorMessage error={error} />
    {:else if filteredGames.length === 0}
        <EmptyState message="No games available at the moment." />
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each filteredGames as game (game.id)}
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
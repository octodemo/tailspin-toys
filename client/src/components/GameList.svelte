<script lang="ts">
    import { onMount } from "svelte";
    import type { Game } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';
    import GameCard from "./GameCard.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";

    let { games = $bindable([]) }: { games?: Game[] } = $props();
    let loading = $state(true);
    let error = $state<string | null>(null);
    let allGames = $state<Game[]>([]);
    let filteredGames = $state<Game[]>([]);
    let selectedPublisher = $state('all');
    let selectedCategory = $state('all');
    let selectedSort = $state('rating');

    let publisherOptions = $derived(
        [...new Set(allGames.map((game) => game.publisher?.name).filter(Boolean))] as string[]
    );

    let categoryOptions = $derived(
        [...new Set(allGames.map((game) => game.category?.name).filter(Boolean))] as string[]
    );

    const fetchGames = async (publisher: string = 'all', category: string = 'all', sort: string = 'rating') => {
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

            const endpoint = queryParams.toString()
                ? `${API_ENDPOINTS.games}?${queryParams.toString()}`
                : API_ENDPOINTS.games;

            const response = await fetch(endpoint);
            if(response.ok) {
                const data = await response.json();
                filteredGames = data;

                if (publisher === 'all' && category === 'all') {
                    allGames = data;
                    games = data;
                }
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const onFilterChange = async () => {
        await fetchGames(selectedPublisher, selectedCategory, selectedSort);
    };

    onMount(() => {
        if (games.length === 0) {
            fetchGames();
        } else {
            allGames = games;
            filteredGames = games;
            loading = false;
        }
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
    {/if}
</div>
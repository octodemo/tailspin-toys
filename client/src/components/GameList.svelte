<script lang="ts">
    import { onMount } from "svelte";
    import GameCard from "./GameCard.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher_name?: string;
        category_name?: string;
    }

    interface PaginationInfo {
        page: number;
        pageSize: number;
        totalCount: number;
        totalPages: number;
    }

    let { games = $bindable([]) }: { games?: Game[] } = $props();
    let loading = $state(true);
    let error = $state<string | null>(null);
    let currentPage = $state(1);
    let pageSize = $state(10);
    let pagination = $state<PaginationInfo | null>(null);

    const fetchGames = async () => {
        loading = true;
        try {
            const response = await fetch(`/api/games?page=${currentPage}&pageSize=${pageSize}`);
            if(response.ok) {
                const data = await response.json();
                games = data.games;
                pagination = data.pagination;
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const goToPage = (page: number) => {
        if (page >= 1 && pagination && page <= pagination.totalPages) {
            currentPage = page;
            fetchGames();
        }
    };

    const changePageSize = (newSize: number) => {
        pageSize = newSize;
        currentPage = 1; // Reset to first page when changing page size
        fetchGames();
    };

    onMount(() => {
        fetchGames();
    });
</script>

<div>
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-medium text-slate-100">Featured Games</h2>
        
        {#if !loading && !error && pagination}
            <div class="flex items-center gap-4">
                <label class="text-slate-300 text-sm">
                    Show:
                    <select 
                        class="ml-2 bg-slate-800 text-slate-100 border border-slate-700 rounded px-3 py-1 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        onchange={(e) => changePageSize(Number(e.currentTarget.value))}
                        data-testid="page-size-selector"
                    >
                        <option value="5">5 per page</option>
                        <option value="10" selected>10 per page</option>
                        <option value="20">20 per page</option>
                        <option value="50">50 per page</option>
                    </select>
                </label>
            </div>
        {/if}
    </div>
    
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
        
        {#if pagination && pagination.totalPages > 1}
            <div class="mt-8 flex justify-between items-center" data-testid="pagination-controls">
                <button
                    class="px-4 py-2 bg-slate-800 text-slate-100 border border-slate-700 rounded hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    onclick={() => goToPage(currentPage - 1)}
                    disabled={currentPage === 1}
                    data-testid="prev-page-button"
                >
                    Previous
                </button>
                
                <div class="flex items-center gap-2">
                    <span class="text-slate-300" data-testid="pagination-info">
                        Page {pagination.page} of {pagination.totalPages}
                    </span>
                    <span class="text-slate-400 text-sm">
                        ({pagination.totalCount} total games)
                    </span>
                </div>
                
                <button
                    class="px-4 py-2 bg-slate-800 text-slate-100 border border-slate-700 rounded hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    onclick={() => goToPage(currentPage + 1)}
                    disabled={currentPage === pagination.totalPages}
                    data-testid="next-page-button"
                >
                    Next
                </button>
            </div>
        {/if}
    {/if}
</div>
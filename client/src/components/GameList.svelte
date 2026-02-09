<script lang="ts">
    import GameCard from "./GameCard.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";

    interface Publisher {
        id: number;
        name: string;
    }
    
    interface Category {
        id: number;
        name: string;
    }

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher?: Publisher | null;
        category?: Category | null;
    }

    let { 
        games = $bindable([]),
        publisherId = null,
        categoryId = null
    }: { 
        games?: Game[];
        publisherId?: number | null;
        categoryId?: number | null;
    } = $props();
    
    let loading = $state(true);
    let error = $state<string | null>(null);
    let requestCounter = 0;

    const fetchGames = async (pubId: number | null, catId: number | null) => {
        const thisRequest = ++requestCounter;
        loading = true;
        error = null;
        try {
            // Build URL with filter params
            const params = new URLSearchParams();
            if (pubId) params.append('publisher_id', pubId.toString());
            if (catId) params.append('category_id', catId.toString());
            
            const url = `/api/games${params.toString() ? '?' + params.toString() : ''}`;
            const response = await fetch(url);
            
            // Ignore stale responses from earlier requests
            if (thisRequest !== requestCounter) return;
            
            if(response.ok) {
                games = await response.json();
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            // Ignore errors from stale requests
            if (thisRequest !== requestCounter) return;
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            if (thisRequest === requestCounter) {
                loading = false;
            }
        }
    };

    // Refetch when filters change
    $effect(() => {
        fetchGames(publisherId, categoryId);
    });
</script>

<div aria-busy={loading}>
    <h2 class="text-2xl font-medium mb-6 text-slate-100">Featured Games</h2>
    
    {#if loading}
        <div role="status" aria-live="polite" class="sr-only">Loading games...</div>
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
    {/if}
    
    <!-- Live region to announce filter results to screen readers -->
    <div role="status" aria-live="polite" aria-atomic="true" class="sr-only">
        {#if !loading && !error}
            {games.length} {games.length === 1 ? 'game' : 'games'} found
        {/if}
    </div>
</div>
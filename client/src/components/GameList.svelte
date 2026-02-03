<script lang="ts">
    import GameCard from "./GameCard.svelte";
    import LoadingSkeleton from "./LoadingSkeleton.svelte";
    import ErrorMessage from "./ErrorMessage.svelte";
    import EmptyState from "./EmptyState.svelte";
    import CategoryFilter from "./CategoryFilter.svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher_name?: string;
        category_name?: string;
    }

    let { games = $bindable([]) }: { games?: Game[] } = $props();
    let loading = $state(true);
    let error = $state<string | null>(null);
    let selectedCategory = $state<number | null>(null);

    const fetchGames = async (categoryId: number | null = null) => {
        loading = true;
        try {
            let url = '/api/games';
            if (categoryId !== null) {
                url += `?category=${categoryId}`;
            }
            const response = await fetch(url);
            if(response.ok) {
                games = await response.json();
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    // Re-fetch games when category changes (Svelte 5 $effect auto-tracks selectedCategory)
    $effect(() => {
        fetchGames(selectedCategory);
    });
</script>

<div>
    <CategoryFilter bind:selectedCategory />
    
    <h2 class="text-2xl font-medium mb-6 text-slate-100">
        {selectedCategory === null ? 'Featured Games' : 'Filtered Games'}
    </h2>
    
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
    {/if}
</div>
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

    const fetchGames = async () => {
        loading = true;
        try {
            const response = await fetch(API_ENDPOINTS.games);
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

    onMount(() => {
        if (games.length === 0) {
            fetchGames();
        } else {
            loading = false;
        }
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
    {/if}
</div>
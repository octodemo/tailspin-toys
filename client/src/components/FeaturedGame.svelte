<script lang="ts">
    import { onMount } from "svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher?: { id: number; name: string } | null;
        category?: { id: number; name: string } | null;
        starRating?: number | null;
        isFeatured: boolean;
        featuredPriority: number | null;
    }

    let featuredGame = $state<Game | null>(null);
    let loading = $state(true);
    let error = $state<string | null>(null);

    const fetchFeaturedGame = async () => {
        loading = true;
        error = null;
        try {
            const response = await fetch('/api/games/featured');
            if(response.ok) {
                featuredGame = await response.json();
            } else if (response.status === 404) {
                // No featured game available, don't show error
                featuredGame = null;
            } else {
                error = `Failed to fetch featured game: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    onMount(() => {
        fetchFeaturedGame();
    });
</script>

{#if !loading && featuredGame && !error}
    <div class="bg-gradient-to-r from-blue-600 to-purple-600 py-8 px-4 shadow-lg" data-testid="featured-game-banner">
        <div class="container mx-auto">
            <div class="flex flex-col md:flex-row items-center justify-between gap-4">
                <div class="flex-1">
                    <div class="inline-block bg-yellow-400 text-slate-900 text-xs font-bold px-3 py-1 rounded-full mb-2">
                        ⭐ FEATURED GAME
                    </div>
                    <h2 class="text-2xl md:text-3xl font-bold text-white mb-2" data-testid="featured-game-title">
                        {featuredGame.title}
                    </h2>
                    <p class="text-blue-100 text-sm md:text-base line-clamp-2 mb-2" data-testid="featured-game-description">
                        {featuredGame.description}
                    </p>
                    <div class="flex flex-wrap gap-3 text-sm text-blue-100">
                        {#if featuredGame.publisher}
                            <span data-testid="featured-game-publisher">
                                Publisher: <strong>{featuredGame.publisher.name}</strong>
                            </span>
                        {/if}
                        {#if featuredGame.category}
                            <span data-testid="featured-game-category">
                                Category: <strong>{featuredGame.category.name}</strong>
                            </span>
                        {/if}
                        {#if featuredGame.starRating}
                            <span data-testid="featured-game-rating">
                                Rating: <strong>{featuredGame.starRating}⭐</strong>
                            </span>
                        {/if}
                    </div>
                </div>
                <div class="flex-shrink-0">
                    <a 
                        href={`/game/${featuredGame.id}`}
                        class="inline-block bg-white text-blue-600 font-bold px-6 py-3 rounded-lg hover:bg-blue-50 transition-colors duration-200 shadow-md focus:ring-2 focus:ring-white focus:outline-none"
                        data-testid="featured-game-link"
                    >
                        Learn More →
                    </a>
                </div>
            </div>
        </div>
    </div>
{/if}

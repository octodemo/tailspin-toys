<script lang="ts">
    interface Game {
        id: number;
        title: string;
        description: string;
        publisher?: {
            id: number;
            name: string;
        };
        category?: {
            id: number;
            name: string;
        };
        starRating?: number;
        isFeatured: boolean;
    }

    let game = $state<Game | null>(null);
    let loading = $state(true);
    let error = $state<string | null>(null);

    // Fetch featured game on component mount
    $effect(() => {
        const fetchFeaturedGame = async () => {
            try {
                loading = true;
                error = null;
                const response = await fetch('http://localhost:5100/api/games/featured');
                
                if (!response.ok) {
                    if (response.status === 404) {
                        // No featured game available - this is ok, just don't display anything
                        game = null;
                        return;
                    }
                    throw new Error('Failed to fetch featured game');
                }
                
                game = await response.json();
            } catch (err) {
                error = err instanceof Error ? err.message : 'Failed to load featured game';
                console.error('Error fetching featured game:', err);
            } finally {
                loading = false;
            }
        };

        fetchFeaturedGame();
    });
</script>

{#if loading}
    <div 
        class="bg-gradient-to-r from-blue-900/40 to-purple-900/40 rounded-lg p-4 border border-slate-700/50 animate-pulse"
        role="status"
        aria-label="Loading featured game"
    >
        <div class="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
        <div class="h-3 bg-slate-700 rounded w-1/2"></div>
    </div>
{:else if error}
    <!-- Error state - silently fail, no need to show error to user -->
{:else if game}
    <section 
        class="bg-gradient-to-r from-blue-900/40 to-purple-900/40 rounded-lg p-4 border border-blue-500/30 hover:border-blue-500/50 transition-all duration-300"
        aria-labelledby="featured-game-title"
    >
        <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                    <span class="text-xs font-semibold text-blue-400 uppercase tracking-wider" aria-label="Featured game badge">
                        ⭐ Featured
                    </span>
                    {#if game.category}
                        <span 
                            class="text-xs font-medium px-2 py-0.5 rounded bg-blue-900/60 text-blue-300"
                            data-testid="featured-game-category"
                        >
                            {game.category.name}
                        </span>
                    {/if}
                </div>
                <h2 
                    id="featured-game-title"
                    class="text-lg font-bold text-slate-100 mb-1 truncate"
                    data-testid="featured-game-title"
                >
                    {game.title}
                </h2>
                <p 
                    class="text-sm text-slate-300 line-clamp-2 mb-2"
                    data-testid="featured-game-description"
                >
                    {game.description}
                </p>
                {#if game.publisher}
                    <p class="text-xs text-slate-400" data-testid="featured-game-publisher">
                        By {game.publisher.name}
                    </p>
                {/if}
            </div>
            <a 
                href={`/game/${game.id}`}
                class="flex-shrink-0 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900"
                data-testid="featured-game-link"
                aria-label={`View details for ${game.title}`}
            >
                View Details
            </a>
        </div>
    </section>
{/if}

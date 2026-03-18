<script lang="ts">
    import { onMount } from "svelte";
    import type { Game } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';
    import { isSupported, toggleSupport } from '../utils/supportState';
    import ErrorMessage from "./ErrorMessage.svelte";

    let { game = undefined, gameId = 0 }: { game?: Game, gameId?: number } = $props();
    
    let loading = $state(true);
    let error = $state<string | null>(null);
    let gameData = $state<Game | null>(null);
    let supported = $state(false);
    
    onMount(async () => {
        // If game object is provided directly, use it
        if (game) {
            gameData = game;
            supported = isSupported(game.id);
            loading = false;
            return;
        }
        
        // Otherwise fetch data using gameId
        if (gameId) {
            try {
                const response = await fetch(API_ENDPOINTS.gameById(gameId));
                if (response.ok) {
                    gameData = await response.json();
                    if (gameData) {
                        supported = isSupported(gameData.id);
                    }
                } else {
                    error = `Failed to fetch game: ${response.status} ${response.statusText}`;
                }
            } catch (err) {
                error = `Error: ${err instanceof Error ? err.message : String(err)}`;
            } finally {
                loading = false;
            }
        } else {
            error = "No game ID provided";
            loading = false;
        }
    });

    function handleSupportClick(): void {
        if (!gameData) return;
        supported = toggleSupport(gameData.id);
    }

    function renderStarRating(rating: number | null): string {
        if (rating === null) return "Not yet rated";
        
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        return '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(emptyStars);
    }
</script>

{#if loading}
    <div class="animate-pulse bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden p-6">
        <div class="h-8 bg-slate-700 rounded w-1/2 mb-6"></div>
        <div class="h-4 bg-slate-700 rounded w-3/4 mb-3"></div>
        <div class="h-4 bg-slate-700 rounded w-1/2 mb-3"></div>
        <div class="h-4 bg-slate-700 rounded w-full mb-3"></div>
    </div>
{:else if error}
    <ErrorMessage {error} />
{:else if gameData}
    <div class="bg-slate-800/70 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden" data-testid="game-details">
        <div class="p-6">
            <div class="flex justify-between items-start flex-wrap gap-3">
                <h1 class="text-3xl font-bold text-slate-100 mb-2" data-testid="game-details-title">{gameData.title}</h1>
                
                {#if gameData.starRating !== null}
                <div class="flex items-center">
                    <span class="bg-blue-500/20 text-blue-400 text-sm px-3 py-1 rounded-full" data-testid="game-rating">
                        <span class="text-yellow-400">{renderStarRating(gameData.starRating)}</span> 
                        {gameData.starRating.toFixed(1)}
                    </span>
                </div>
                {/if}
            </div>
            
            <div class="flex flex-wrap gap-2 mt-4 mb-6">
                {#if gameData.category}
                    <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-details-category">
                        {gameData.category.name}
                    </span>
                {/if}
                {#if gameData.publisher}
                    <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-details-publisher">
                        {gameData.publisher.name}
                    </span>
                {/if}
            </div>
            
            <div class="space-y-4 mt-6">
                <h2 class="text-lg font-semibold text-slate-200 mb-2">About this game</h2>
                <div class="text-slate-400 space-y-4">
                    <p data-testid="game-details-description">{gameData.description}</p>
                </div>
            </div>
            
            <div class="mt-8">
                {#if supported}
                    <button
                        class="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 flex justify-center items-center"
                        data-testid="support-game-button"
                        onclick={handleSupportClick}
                        aria-pressed="true"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                        Supported
                    </button>
                {:else}
                    <button
                        class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 flex justify-center items-center"
                        data-testid="support-game-button"
                        onclick={handleSupportClick}
                        aria-pressed="false"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                        </svg>
                        Support This Game
                    </button>
                {/if}
            </div>
        </div>
    </div>
{:else}
    <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6">
        <p class="text-slate-400">No game information available</p>
    </div>
{/if}
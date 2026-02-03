<script lang="ts">
    import { onMount } from "svelte";
    
    import type { Subscription } from "../types/game";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher: {
            id: number;
            name: string;
        } | null;
        category: {
            id: number;
            name: string;
        } | null;
        starRating: number | null;
    }

    let { game = undefined, gameId = 0 }: { game?: Game, gameId?: number } = $props();
    
    let loading = $state(true);
    let error = $state<string | null>(null);
    let gameData = $state<Game | null>(null);
    let subscription = $state<Subscription | null>(null);
    let email = $state("");
    let frequency = $state<Subscription["frequency"]>("weekly");
    let submitting = $state(false);
    let successMessage = $state<string | null>(null);
    
    onMount(async () => {
        // If game object is provided directly, use it
        if (game) {
            gameData = game;
            loading = false;
            return;
        }
        
        // Otherwise fetch data using gameId
        if (gameId) {
            try {
                const response = await fetch(`/api/games/${gameId}`);
                if (response.ok) {
                    gameData = await response.json();
                    await loadExistingSubscription();
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

    const loadExistingSubscription = async (): Promise<void> => {
        if (!gameId) return;
        try {
            const resp = await fetch(`/api/games/${gameId}/subscriptions`, { method: "GET" });
            if (resp.ok) {
                const subs: Subscription[] = await resp.json();
                if (subs.length > 0) {
                    subscription = subs[0];
                    email = subscription.email;
                    frequency = subscription.frequency;
                }
            }
        } catch (err) {
            // Swallow errors to avoid blocking main flow
            console.error("Failed to load subscription", err);
        }
    };

    const handleSubscribe = async (): Promise<void> => {
        if (!gameId) return;
        submitting = true;
        successMessage = null;
        error = null;
        try {
            const resp = await fetch(`/api/games/${gameId}/subscriptions`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, frequency })
            });
            const data = await resp.json();
            if (!resp.ok) {
                error = data.error ?? "Failed to subscribe";
                return;
            }
            subscription = data;
            successMessage = "Subscription saved";
        } catch (err) {
            error = err instanceof Error ? err.message : String(err);
        } finally {
            submitting = false;
        }
    };

    const handleUpdate = async (): Promise<void> => {
        if (!subscription) return handleSubscribe();
        submitting = true;
        successMessage = null;
        error = null;
        try {
            const resp = await fetch(`/api/subscriptions/${subscription.id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ frequency })
            });
            const data = await resp.json();
            if (!resp.ok) {
                error = data.error ?? "Failed to update subscription";
                return;
            }
            subscription = data;
            successMessage = "Frequency updated";
        } catch (err) {
            error = err instanceof Error ? err.message : String(err);
        } finally {
            submitting = false;
        }
    };

    const handleUnsubscribe = async (): Promise<void> => {
        if (!subscription) return;
        submitting = true;
        successMessage = null;
        error = null;
        try {
            const resp = await fetch(`/api/subscriptions/${subscription.id}`, {
                method: "DELETE"
            });
            const data = await resp.json();
            if (!resp.ok) {
                error = data.error ?? "Failed to unsubscribe";
                return;
            }
            subscription = { ...subscription, isActive: false };
            successMessage = "Unsubscribed";
        } catch (err) {
            error = err instanceof Error ? err.message : String(err);
        } finally {
            submitting = false;
        }
    };

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
    <div class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-xl p-6">
        {error}
    </div>
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
            
            <div class="mt-8 space-y-4">
                <div class="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-3">
                        <div>
                            <h3 class="text-lg font-semibold text-slate-100">Get updates</h3>
                            <p class="text-sm text-slate-400">Subscribe to product updates for this game.</p>
                        </div>
                        {#if subscription && subscription.isActive}
                            <span class="text-xs px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300">Subscribed</span>
                        {/if}
                    </div>
                    <div class="grid gap-3 md:grid-cols-2">
                        <label class="flex flex-col gap-2 text-slate-200 text-sm">
                            Email
                            <input
                                class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                type="email"
                                value={email}
                                oninput={(event) => email = (event.target as HTMLInputElement).value}
                                placeholder="you@example.com"
                                data-testid="subscription-email-input"
                            />
                        </label>
                        <label class="flex flex-col gap-2 text-slate-200 text-sm">
                            Frequency
                            <select
                                class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={frequency}
                                oninput={(event) => frequency = (event.target as HTMLSelectElement).value as Subscription['frequency']}
                                data-testid="subscription-frequency-select"
                            >
                                <option value="immediate">Immediate</option>
                                <option value="daily">Daily</option>
                                <option value="weekly">Weekly</option>
                            </select>
                        </label>
                    </div>
                    {#if error}
                        <p class="text-red-400 text-sm mt-2" data-testid="subscription-error">{error}</p>
                    {/if}
                    {#if successMessage}
                        <p class="text-emerald-300 text-sm mt-2" data-testid="subscription-success">{successMessage}</p>
                    {/if}
                    <div class="mt-4 flex flex-wrap gap-3">
                        <button
                            class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-medium py-2 px-4 rounded-lg transition-all duration-200 disabled:opacity-60"
                            onclick={subscription && subscription.isActive ? handleUpdate : handleSubscribe}
                            disabled={submitting}
                            data-testid="subscription-submit-button"
                        >
                            {subscription && subscription.isActive ? 'Update preferences' : 'Subscribe'}
                        </button>
                        {#if subscription && subscription.isActive}
                            <button
                                class="py-2 px-4 rounded-lg border border-slate-700 text-slate-200 hover:border-red-500 hover:text-red-300 transition-colors disabled:opacity-60"
                                onclick={handleUnsubscribe}
                                disabled={submitting}
                                data-testid="subscription-unsubscribe-button"
                            >
                                Unsubscribe
                            </button>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
{:else}
    <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6">
        <p class="text-slate-400">No game information available</p>
    </div>
{/if}

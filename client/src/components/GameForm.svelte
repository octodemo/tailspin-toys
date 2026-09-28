<script lang="ts">
    import type { Category, Game, Publisher } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';

    let {
        game = null,
        publishers,
        categories,
        onSaved,
        onCancel,
    }: {
        game?: Game | null;
        publishers: Publisher[];
        categories: Category[];
        onSaved: (game: Game) => void;
        onCancel: () => void;
    } = $props();

    const isEditing = $derived(game !== null);

    // Seeded from the incoming game so the same form handles create and edit.
    let title = $state(game?.title ?? '');
    let description = $state(game?.description ?? '');
    let publisherId = $state<string>(game?.publisher ? String(game.publisher.id) : '');
    let categoryId = $state<string>(game?.category ? String(game.category.id) : '');
    let starRating = $state<string>(game?.starRating != null ? String(game.starRating) : '');

    let submitting = $state(false);
    let error = $state<string | null>(null);

    // Mirrors the server-side model validation so problems surface before a request.
    const validationError = $derived.by(() => {
        if (title.trim().length < 2) return 'Title must be at least 2 characters.';
        if (description.trim().length < 10) return 'Description must be at least 10 characters.';
        if (!publisherId) return 'Select a publisher.';
        if (!categoryId) return 'Select a category.';

        if (starRating !== '') {
            const rating = Number(starRating);
            if (Number.isNaN(rating)) return 'Star rating must be a number.';
            if (rating < 0 || rating > 5) return 'Star rating must be between 0 and 5.';
        }

        return null;
    });

    const handleSubmit = async (event: SubmitEvent) => {
        event.preventDefault();

        if (validationError) {
            error = validationError;
            return;
        }

        submitting = true;
        error = null;

        const payload = {
            title: title.trim(),
            description: description.trim(),
            publisherId: Number(publisherId),
            categoryId: Number(categoryId),
            starRating: starRating === '' ? null : Number(starRating),
        };

        try {
            const response = await fetch(
                isEditing ? API_ENDPOINTS.gameById(game!.id) : API_ENDPOINTS.games,
                {
                    method: isEditing ? 'PUT' : 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                },
            );

            if (response.ok) {
                onSaved(await response.json());
            } else {
                const data = await response.json().catch(() => null);
                error = data?.error ?? `Save failed: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            submitting = false;
        }
    };

    const handleKeydown = (event: KeyboardEvent) => {
        if (event.key === 'Escape') {
            onCancel();
        }
    };
</script>

<svelte:window onkeydown={handleKeydown} />

<section
    class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-slate-700 mb-8"
    aria-labelledby="game-form-heading"
    data-testid="game-form"
>
    <h3 id="game-form-heading" class="text-xl font-medium mb-6 text-slate-100">
        {isEditing ? `Edit ${game!.title}` : 'Add a new game'}
    </h3>

    <form onsubmit={handleSubmit} novalidate>
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div class="md:col-span-2">
                <label class="block text-sm font-medium text-slate-200 mb-2" for="game-title">
                    Title
                </label>
                <input
                    id="game-title"
                    type="text"
                    bind:value={title}
                    class="w-full px-4 py-2 rounded-lg bg-slate-900 text-slate-100 border border-slate-600
                        placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    placeholder="Pipeline Panic"
                    data-testid="game-form-title"
                />
            </div>

            <div class="md:col-span-2">
                <label class="block text-sm font-medium text-slate-200 mb-2" for="game-description">
                    Description
                </label>
                <textarea
                    id="game-description"
                    rows="4"
                    bind:value={description}
                    class="w-full px-4 py-2 rounded-lg bg-slate-900 text-slate-100 border border-slate-600
                        placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    placeholder="Build your DevOps pipeline before chaos ensues"
                    data-testid="game-form-description"
                ></textarea>
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-200 mb-2" for="game-publisher">
                    Publisher
                </label>
                <select
                    id="game-publisher"
                    bind:value={publisherId}
                    class="w-full px-4 py-2 rounded-lg bg-slate-900 text-slate-100 border border-slate-600
                        focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    data-testid="game-form-publisher"
                >
                    <option value="">Select a publisher</option>
                    {#each publishers as publisher (publisher.id)}
                        <option value={String(publisher.id)}>{publisher.name}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-200 mb-2" for="game-category">
                    Category
                </label>
                <select
                    id="game-category"
                    bind:value={categoryId}
                    class="w-full px-4 py-2 rounded-lg bg-slate-900 text-slate-100 border border-slate-600
                        focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    data-testid="game-form-category"
                >
                    <option value="">Select a category</option>
                    {#each categories as category (category.id)}
                        <option value={String(category.id)}>{category.name}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-200 mb-2" for="game-rating">
                    Star rating <span class="text-slate-400">(optional, 0–5)</span>
                </label>
                <input
                    id="game-rating"
                    type="number"
                    min="0"
                    max="5"
                    step="0.1"
                    bind:value={starRating}
                    class="w-full px-4 py-2 rounded-lg bg-slate-900 text-slate-100 border border-slate-600
                        placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    placeholder="4.5"
                    data-testid="game-form-rating"
                />
            </div>
        </div>

        {#if error}
            <p class="mt-6 text-sm text-red-400" role="alert" data-testid="game-form-error">
                {error}
            </p>
        {/if}

        <div class="flex flex-wrap gap-4 mt-6">
            <button
                type="submit"
                disabled={submitting}
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200
                    {submitting
                        ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                        : 'bg-blue-700 text-white hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:outline-none'}"
                data-testid="game-form-submit"
            >
                {submitting ? 'Saving…' : isEditing ? 'Save changes' : 'Create game'}
            </button>

            <button
                type="button"
                onclick={onCancel}
                class="px-4 py-2 rounded-lg text-sm font-medium bg-slate-700 text-slate-100
                    hover:bg-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none
                    transition-colors duration-200"
                data-testid="game-form-cancel"
            >
                Cancel
            </button>
        </div>
    </form>
</section>

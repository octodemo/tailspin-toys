<script lang="ts">
    import { onMount } from 'svelte';
    import type { CategoryOption, PublisherOption } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';

    let {
        categoryId = $bindable<number | null>(null),
        publisherId = $bindable<number | null>(null),
        onchange,
    }: {
        categoryId?: number | null;
        publisherId?: number | null;
        onchange?: () => void;
    } = $props();

    let categories = $state<CategoryOption[]>([]);
    let publishers = $state<PublisherOption[]>([]);
    let loadError = $state<string | null>(null);

    const handleCategoryChange = (e: Event) => {
        const value = (e.target as HTMLSelectElement).value;
        categoryId = value ? Number(value) : null;
        onchange?.();
    };

    const handlePublisherChange = (e: Event) => {
        const value = (e.target as HTMLSelectElement).value;
        publisherId = value ? Number(value) : null;
        onchange?.();
    };

    const clearFilters = () => {
        categoryId = null;
        publisherId = null;
        onchange?.();
    };

    const hasActiveFilters = $derived(categoryId !== null || publisherId !== null);

    onMount(async () => {
        try {
            const [catRes, pubRes] = await Promise.all([
                fetch(API_ENDPOINTS.categories),
                fetch(API_ENDPOINTS.publishers),
            ]);
            if (catRes.ok) categories = await catRes.json();
            if (pubRes.ok) publishers = await pubRes.json();
        } catch {
            loadError = 'Failed to load filter options.';
        }
    });
</script>

<div class="flex flex-wrap items-end gap-4 mb-6" data-testid="game-filters">
    {#if loadError}
        <p class="text-red-400 text-sm" data-testid="filter-error">{loadError}</p>
    {:else}
        <div class="flex flex-col gap-1">
            <label for="category-filter" class="text-sm text-slate-400">Category</label>
            <select
                id="category-filter"
                class="bg-slate-700 text-slate-100 rounded-lg px-3 py-2 text-sm
                       border border-slate-600 hover:border-slate-500
                       focus:ring-2 focus:ring-blue-500 focus:outline-none"
                value={categoryId ?? ''}
                onchange={handleCategoryChange}
                data-testid="category-filter"
            >
                <option value="">All Categories</option>
                {#each categories as category (category.id)}
                    <option value={category.id}>{category.name}</option>
                {/each}
            </select>
        </div>

        <div class="flex flex-col gap-1">
            <label for="publisher-filter" class="text-sm text-slate-400">Publisher</label>
            <select
                id="publisher-filter"
                class="bg-slate-700 text-slate-100 rounded-lg px-3 py-2 text-sm
                       border border-slate-600 hover:border-slate-500
                       focus:ring-2 focus:ring-blue-500 focus:outline-none"
                value={publisherId ?? ''}
                onchange={handlePublisherChange}
                data-testid="publisher-filter"
            >
                <option value="">All Publishers</option>
                {#each publishers as publisher (publisher.id)}
                    <option value={publisher.id}>{publisher.name}</option>
                {/each}
            </select>
        </div>

        {#if hasActiveFilters}
            <button
                class="px-3 py-2 rounded-lg text-sm font-medium bg-slate-700 text-slate-300
                       hover:bg-slate-600 hover:text-slate-100 transition-colors duration-200
                       focus:ring-2 focus:ring-blue-500 focus:outline-none"
                onclick={clearFilters}
                data-testid="clear-filters-button"
                aria-label="Clear all filters"
            >
                Clear Filters
            </button>
        {/if}
    {/if}
</div>

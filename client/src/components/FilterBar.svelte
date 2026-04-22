<script lang="ts">
    import { onMount } from "svelte";
    import type { FilterOption } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';

    let {
        onFilterChange,
    }: {
        onFilterChange: (filters: { category: string; publisher: string }) => void;
    } = $props();

    let categories = $state<FilterOption[]>([]);
    let publishers = $state<FilterOption[]>([]);
    let categoriesError = $state(false);
    let publishersError = $state(false);

    let selectedCategory = $state('');
    let selectedPublisher = $state('');

    const fetchFilterOptions = async () => {
        try {
            const res = await fetch(API_ENDPOINTS.categories);
            if (res.ok) {
                categories = await res.json();
            } else {
                categoriesError = true;
            }
        } catch {
            categoriesError = true;
        }

        try {
            const res = await fetch(API_ENDPOINTS.publishers);
            if (res.ok) {
                publishers = await res.json();
            } else {
                publishersError = true;
            }
        } catch {
            publishersError = true;
        }
    };

    const handleCategoryChange = (e: Event) => {
        const target = e.target as HTMLSelectElement;
        selectedCategory = target.value;
        onFilterChange({ category: selectedCategory, publisher: selectedPublisher });
    };

    const handlePublisherChange = (e: Event) => {
        const target = e.target as HTMLSelectElement;
        selectedPublisher = target.value;
        onFilterChange({ category: selectedCategory, publisher: selectedPublisher });
    };

    onMount(() => {
        fetchFilterOptions();
    });
</script>

<div class="flex flex-wrap items-center gap-4 mb-6" data-testid="filter-bar">
    <label class="flex items-center gap-2 text-sm text-slate-300">
        <span>Category:</span>
        <select
            class="bg-slate-700 text-slate-100 rounded-lg px-3 py-2 text-sm border border-slate-600
                   focus:ring-2 focus:ring-blue-500 focus:outline-none
                   disabled:opacity-50 disabled:cursor-not-allowed"
            value={selectedCategory}
            onchange={handleCategoryChange}
            disabled={categoriesError}
            data-testid="filter-category"
            aria-label="Filter by category"
        >
            <option value="">All Categories</option>
            {#each categories as cat (cat.id)}
                <option value={String(cat.id)}>{cat.name} ({cat.gameCount})</option>
            {/each}
        </select>
        {#if categoriesError}
            <span class="text-red-400 text-xs" data-testid="filter-category-error">Failed to load</span>
        {/if}
    </label>

    <label class="flex items-center gap-2 text-sm text-slate-300">
        <span>Publisher:</span>
        <select
            class="bg-slate-700 text-slate-100 rounded-lg px-3 py-2 text-sm border border-slate-600
                   focus:ring-2 focus:ring-blue-500 focus:outline-none
                   disabled:opacity-50 disabled:cursor-not-allowed"
            value={selectedPublisher}
            onchange={handlePublisherChange}
            disabled={publishersError}
            data-testid="filter-publisher"
            aria-label="Filter by publisher"
        >
            <option value="">All Publishers</option>
            {#each publishers as pub (pub.id)}
                <option value={String(pub.id)}>{pub.name} ({pub.gameCount})</option>
            {/each}
        </select>
        {#if publishersError}
            <span class="text-red-400 text-xs" data-testid="filter-publisher-error">Failed to load</span>
        {/if}
    </label>
</div>

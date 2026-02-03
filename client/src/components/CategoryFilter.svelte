<script lang="ts">
    import { onMount } from "svelte";

    interface Category {
        id: number;
        name: string;
        description: string;
        game_count: number;
    }

    let { selectedCategory = $bindable<number | null>(null) }: { selectedCategory?: number | null } = $props();
    let categories = $state<Category[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);

    const fetchCategories = async () => {
        loading = true;
        try {
            const response = await fetch('/api/categories');
            if (response.ok) {
                categories = await response.json();
            } else {
                error = `Failed to fetch categories: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const handleCategoryChange = (categoryId: number | null) => {
        selectedCategory = categoryId;
    };

    onMount(() => {
        fetchCategories();
    });
</script>

<div class="mb-6" data-testid="category-filter">
    <label class="block text-sm font-medium text-slate-300 mb-2">Filter by Category</label>
    {#if loading}
        <div class="animate-pulse h-10 bg-slate-700 rounded-lg w-48"></div>
    {:else if error}
        <p class="text-red-400 text-sm">{error}</p>
    {:else}
        <div class="flex flex-wrap gap-2">
            <button
                type="button"
                onclick={() => handleCategoryChange(null)}
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 {selectedCategory === null 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
                data-testid="category-filter-all"
            >
                All Games
            </button>
            {#each categories as category (category.id)}
                <button
                    type="button"
                    onclick={() => handleCategoryChange(category.id)}
                    class="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 {selectedCategory === category.id 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
                    data-testid="category-filter-{category.id}"
                >
                    {category.name}
                </button>
            {/each}
        </div>
    {/if}
</div>

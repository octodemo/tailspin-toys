<script lang="ts">
    interface FilterOption {
        id: number;
        name: string;
    }

    let { 
        selectedPublisherId = $bindable<number | null>(null),
        selectedCategoryId = $bindable<number | null>(null)
    }: { 
        selectedPublisherId?: number | null;
        selectedCategoryId?: number | null;
    } = $props();

    let publishers = $state<FilterOption[]>([]);
    let categories = $state<FilterOption[]>([]);
    let loading = $state(true);

    const fetchFilters = async () => {
        loading = true;
        try {
            const [publishersRes, categoriesRes] = await Promise.all([
                fetch('/api/publishers'),
                fetch('/api/categories')
            ]);
            
            if (publishersRes.ok && categoriesRes.ok) {
                publishers = await publishersRes.json();
                categories = await categoriesRes.json();
            }
        } catch (err) {
            console.error('Error fetching filters:', err);
        } finally {
            loading = false;
        }
    };

    $effect(() => {
        fetchFilters();
    });

    const handlePublisherChange = (event: Event) => {
        const target = event.target as HTMLSelectElement;
        selectedPublisherId = target.value ? parseInt(target.value, 10) : null;
    };

    const handleCategoryChange = (event: Event) => {
        const target = event.target as HTMLSelectElement;
        selectedCategoryId = target.value ? parseInt(target.value, 10) : null;
    };

    const clearFilters = () => {
        selectedPublisherId = null;
        selectedCategoryId = null;
    };

    let hasActiveFilters = $derived(selectedPublisherId !== null || selectedCategoryId !== null);
</script>

<div class="bg-slate-800 rounded-xl p-4 mb-6 border border-slate-700" data-testid="game-filters">
    <div class="flex flex-wrap items-center gap-4">
        <div class="flex items-center gap-2">
            <label for="publisher-filter" class="text-slate-300 text-sm font-medium">
                Publisher:
            </label>
            <select
                id="publisher-filter"
                class="bg-slate-700 text-slate-100 rounded-lg px-3 py-2 border border-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none min-w-[160px]"
                onchange={handlePublisherChange}
                value={selectedPublisherId ?? ''}
                disabled={loading}
                data-testid="publisher-filter"
            >
                <option value="">All Publishers</option>
                {#each publishers as publisher (publisher.id)}
                    <option value={publisher.id}>{publisher.name}</option>
                {/each}
            </select>
        </div>

        <div class="flex items-center gap-2">
            <label for="category-filter" class="text-slate-300 text-sm font-medium">
                Category:
            </label>
            <select
                id="category-filter"
                class="bg-slate-700 text-slate-100 rounded-lg px-3 py-2 border border-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none min-w-[160px]"
                onchange={handleCategoryChange}
                value={selectedCategoryId ?? ''}
                disabled={loading}
                data-testid="category-filter"
            >
                <option value="">All Categories</option>
                {#each categories as category (category.id)}
                    <option value={category.id}>{category.name}</option>
                {/each}
            </select>
        </div>

        {#if hasActiveFilters}
            <button
                onclick={clearFilters}
                class="text-slate-400 hover:text-slate-100 text-sm underline transition-colors duration-200 focus:ring-2 focus:ring-blue-500 focus:outline-none rounded px-2 py-1"
                data-testid="clear-filters-button"
            >
                Clear filters
            </button>
        {/if}
    </div>
</div>

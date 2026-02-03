<script lang="ts">
    interface Category {
        id: number;
        name: string;
        description: string;
        game_count: number;
    }

    let { 
        categories = $bindable([]),
        selectedCategory = $bindable<number | null>(null),
        onCategoryChange
    }: { 
        categories?: Category[];
        selectedCategory?: number | null;
        onCategoryChange?: (categoryId: number | null) => void;
    } = $props();

    const handleCategoryChange = (categoryId: number | null) => {
        selectedCategory = categoryId;
        if (onCategoryChange) {
            onCategoryChange(categoryId);
        }
    };
</script>

<div class="mb-6">
    <label for="category-filter" class="block text-sm font-medium text-slate-300 mb-2">
        Filter by Category
    </label>
    <select
        id="category-filter"
        data-testid="category-filter"
        class="w-full md:w-64 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:ring-2 focus:ring-blue-500 focus:outline-none"
        value={selectedCategory ?? ''}
        onchange={(e) => {
            const value = e.currentTarget.value;
            handleCategoryChange(value === '' ? null : parseInt(value, 10));
        }}
    >
        <option value="">All Categories</option>
        {#each categories as category (category.id)}
            <option value={category.id}>
                {category.name} ({category.game_count})
            </option>
        {/each}
    </select>
</div>

<script lang="ts">
    import GameFilters from "./GameFilters.svelte";
    import GameList from "./GameList.svelte";

    let selectedPublisherId = $state<number | null>(null);
    let selectedCategoryId = $state<number | null>(null);
</script>

<div>
    <GameFilters 
        bind:selectedPublisherId 
        bind:selectedCategoryId 
    />
    <GameList 
        publisherId={selectedPublisherId} 
        categoryId={selectedCategoryId} 
    />
</div>

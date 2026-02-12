<script lang="ts">
    let { error }: { error: string } = $props();
</script>

<div data-testid="error-message" class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
    <p data-testid="error-text" class="text-red-400">{error}</p>
</div>

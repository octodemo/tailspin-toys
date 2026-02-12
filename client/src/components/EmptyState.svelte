<script lang="ts">
    let { message }: { message: string } = $props();
</script>

<div data-testid="empty-state" class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
    <p data-testid="empty-state-text" class="text-slate-300">{message}</p>
</div>

<script lang="ts">
    import { onMount } from "svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher_name?: string;
        category_name?: string;
    }

    let { game }: { game: Game } = $props();
    let showHeartBadge = $state(false);
    
    const PATRONAGE_STORAGE_LOCATION = 'tailspin-supported-games';
    const PATRONAGE_UPDATE_SIGNAL = 'tailspin-patronage-update';
    
    function checkPatronageStatus(): void {
        if (typeof window === 'undefined') return;
        
        const stored = localStorage.getItem(PATRONAGE_STORAGE_LOCATION);
        if (!stored) {
            showHeartBadge = false;
            return;
        }
        
        try {
            const parsed = JSON.parse(stored);
            const patronList = Array.isArray(parsed) ? parsed : [];
            showHeartBadge = patronList.some(id => id === game.id);
        } catch {
            showHeartBadge = false;
        }
    }
    
    onMount(() => {
        checkPatronageStatus();
        
        const handleUpdate = () => checkPatronageStatus();
        window.addEventListener(PATRONAGE_UPDATE_SIGNAL, handleUpdate);
        
        return () => {
            window.removeEventListener(PATRONAGE_UPDATE_SIGNAL, handleUpdate);
        };
    });
</script>

<a 
    href={`/game/${game.id}`} 
    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
    data-testid="game-card"
    data-game-id={game.id}
    data-game-title={game.title}
>
    <div class="p-6 relative">
        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        {#if showHeartBadge}
            <div class="absolute top-3 right-3 bg-red-500 rounded-full p-2" data-testid="heart-badge" role="img" aria-label="You are supporting this game">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                </svg>
            </div>
        {/if}
        <div class="relative z-10">
            <h3 class="text-xl font-semibold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors" data-testid="game-title">{game.title}</h3>
            
            {#if game.category_name || game.publisher_name}
                <div class="flex gap-2 mb-3">
                    {#if game.category_name}
                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-category">
                            {game.category_name}
                        </span>
                    {/if}
                    {#if game.publisher_name}
                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-publisher">
                            {game.publisher_name}
                        </span>
                    {/if}
                </div>
            {/if}
            
            <p class="text-slate-400 mb-4 text-sm line-clamp-2" data-testid="game-description">{game.description}</p>
            
            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                <span>View details</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </div>
        </div>
    </div>
</a>

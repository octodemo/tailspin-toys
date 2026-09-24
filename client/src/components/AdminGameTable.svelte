<script lang="ts">
    import type { Game } from '../types/game';

    let {
        games,
        busyId = null,
        onEdit,
        onArchive,
        onRestore,
    }: {
        games: Game[];
        busyId?: number | null;
        onEdit: (game: Game) => void;
        onArchive: (game: Game) => void;
        onRestore: (game: Game) => void;
    } = $props();

    const actionClasses =
        'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors duration-200 ' +
        'focus:ring-2 focus:ring-blue-500 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60';
</script>

<div class="overflow-x-auto bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700 shadow-lg">
    <table class="w-full text-left" data-testid="admin-games-table">
        <caption class="sr-only">Games in the catalog with management actions</caption>
        <thead class="border-b border-slate-700">
            <tr class="text-xs uppercase tracking-wide text-slate-400">
                <th scope="col" class="px-4 py-3">Title</th>
                <th scope="col" class="px-4 py-3">Publisher</th>
                <th scope="col" class="px-4 py-3">Category</th>
                <th scope="col" class="px-4 py-3">Rating</th>
                <th scope="col" class="px-4 py-3">Status</th>
                <th scope="col" class="px-4 py-3">Actions</th>
            </tr>
        </thead>
        <tbody>
            {#each games as game (game.id)}
                <tr
                    class="border-b border-slate-700/50 last:border-0 hover:bg-slate-700/30 transition-colors duration-200"
                    data-testid="admin-game-row-{game.id}"
                >
                    <td class="px-4 py-3 text-slate-100 font-medium">{game.title}</td>
                    <td class="px-4 py-3 text-slate-300">{game.publisher?.name ?? '—'}</td>
                    <td class="px-4 py-3 text-slate-300">{game.category?.name ?? '—'}</td>
                    <td class="px-4 py-3 text-slate-300">{game.starRating ?? '—'}</td>
                    <td class="px-4 py-3">
                        {#if game.isArchived}
                            <span
                                class="inline-block px-2 py-1 rounded-full text-xs font-medium bg-amber-900/60 text-amber-200"
                                data-testid="admin-game-status-{game.id}"
                            >
                                Archived
                            </span>
                        {:else}
                            <span
                                class="inline-block px-2 py-1 rounded-full text-xs font-medium bg-emerald-900/60 text-emerald-200"
                                data-testid="admin-game-status-{game.id}"
                            >
                                Live
                            </span>
                        {/if}
                    </td>
                    <td class="px-4 py-3">
                        <div class="flex flex-wrap gap-2">
                            <button
                                type="button"
                                onclick={() => onEdit(game)}
                                disabled={busyId === game.id}
                                class="{actionClasses} bg-slate-700 text-slate-100 hover:bg-slate-600"
                                data-testid="admin-edit-{game.id}"
                                aria-label="Edit {game.title}"
                            >
                                Edit
                            </button>

                            {#if game.isArchived}
                                <button
                                    type="button"
                                    onclick={() => onRestore(game)}
                                    disabled={busyId === game.id}
                                    class="{actionClasses} bg-emerald-700 text-white hover:bg-emerald-600"
                                    data-testid="admin-restore-{game.id}"
                                    aria-label="Restore {game.title} to the catalog"
                                >
                                    Restore
                                </button>
                            {:else}
                                <button
                                    type="button"
                                    onclick={() => onArchive(game)}
                                    disabled={busyId === game.id}
                                    class="{actionClasses} bg-red-800 text-white hover:bg-red-700"
                                    data-testid="admin-archive-{game.id}"
                                    aria-label="Archive {game.title}"
                                >
                                    Archive
                                </button>
                            {/if}
                        </div>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>

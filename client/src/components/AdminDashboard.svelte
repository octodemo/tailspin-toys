<script lang="ts">
    import { onMount } from 'svelte';
    import type {
        AdminSession,
        CategoriesResponse,
        Category,
        Game,
        PaginatedGamesResponse,
        Publisher,
        PublishersResponse,
    } from '../types/game';
    import { API_ENDPOINTS } from '../config/api';
    import AdminLogin from './AdminLogin.svelte';
    import AdminGameTable from './AdminGameTable.svelte';
    import GameForm from './GameForm.svelte';
    import ErrorMessage from './ErrorMessage.svelte';
    import EmptyState from './EmptyState.svelte';

    let checkingSession = $state(true);
    let authenticated = $state(false);

    let loading = $state(false);
    let error = $state<string | null>(null);
    let status = $state<string | null>(null);

    let games = $state<Game[]>([]);
    let publishers = $state<Publisher[]>([]);
    let categories = $state<Category[]>([]);

    let showArchived = $state(false);
    let formOpen = $state(false);
    let editingGame = $state<Game | null>(null);
    let busyId = $state<number | null>(null);
    let pendingArchive = $state<Game | null>(null);

    const visibleGames = $derived(
        showArchived ? games : games.filter((game) => !game.isArchived),
    );

    const archivedCount = $derived(games.filter((game) => game.isArchived).length);

    const loadLookups = async () => {
        const [publishersResponse, categoriesResponse] = await Promise.all([
            fetch(API_ENDPOINTS.publishers),
            fetch(API_ENDPOINTS.categories),
        ]);

        if (publishersResponse.ok) {
            const data: PublishersResponse = await publishersResponse.json();
            publishers = data.publishers;
        }

        if (categoriesResponse.ok) {
            const data: CategoriesResponse = await categoriesResponse.json();
            categories = data.categories;
        }
    };

    const loadGames = async () => {
        loading = true;
        error = null;

        try {
            // Pull archived rows too so the toggle works without another request.
            const response = await fetch(
                `${API_ENDPOINTS.games}?includeArchived=true&pageSize=100`,
            );

            if (response.ok) {
                const data: PaginatedGamesResponse = await response.json();
                games = data.games;
            } else if (response.status === 401) {
                authenticated = false;
            } else {
                error = `Failed to load games: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const loadAdminData = async () => {
        await Promise.all([loadGames(), loadLookups()]);
    };

    const handleAuthenticated = async () => {
        authenticated = true;
        status = 'Signed in as administrator.';
        await loadAdminData();
    };

    const handleLogout = async () => {
        try {
            await fetch(API_ENDPOINTS.logout, { method: 'POST' });
        } finally {
            authenticated = false;
            games = [];
            formOpen = false;
            editingGame = null;
            status = null;
        }
    };

    const openCreateForm = () => {
        editingGame = null;
        formOpen = true;
        status = null;
    };

    const openEditForm = (game: Game) => {
        editingGame = game;
        formOpen = true;
        status = null;
    };

    const closeForm = () => {
        formOpen = false;
        editingGame = null;
    };

    const handleSaved = async (saved: Game) => {
        status = editingGame ? `Updated “${saved.title}”.` : `Created “${saved.title}”.`;
        closeForm();
        await loadGames();
    };

    const runGameAction = async (game: Game, endpoint: string, method: string, message: string) => {
        busyId = game.id;
        error = null;

        try {
            const response = await fetch(endpoint, { method });

            if (response.ok) {
                status = message;
                await loadGames();
            } else if (response.status === 401) {
                authenticated = false;
            } else {
                const data = await response.json().catch(() => null);
                error = data?.error ?? `Action failed: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            busyId = null;
            pendingArchive = null;
        }
    };

    const confirmArchive = async () => {
        const game = pendingArchive;
        if (!game) return;

        await runGameAction(
            game,
            API_ENDPOINTS.gameById(game.id),
            'DELETE',
            `Archived “${game.title}”. It is hidden from the public catalog.`,
        );
    };

    const handleRestore = async (game: Game) => {
        await runGameAction(
            game,
            API_ENDPOINTS.gameRestore(game.id),
            'POST',
            `Restored “${game.title}” to the catalog.`,
        );
    };

    const handleKeydown = (event: KeyboardEvent) => {
        if (event.key === 'Escape' && pendingArchive) {
            pendingArchive = null;
        }
    };

    onMount(async () => {
        try {
            const response = await fetch(API_ENDPOINTS.session);
            if (response.ok) {
                const data: AdminSession = await response.json();
                authenticated = data.authenticated;
            }
        } catch {
            authenticated = false;
        } finally {
            checkingSession = false;
        }

        if (authenticated) {
            await loadAdminData();
        }
    });
</script>

<svelte:window onkeydown={handleKeydown} />

{#if checkingSession}
    <div
        class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700"
        role="status"
        aria-live="polite"
        data-testid="admin-session-loading"
    >
        <p class="text-slate-300">Checking your session…</p>
    </div>
{:else if !authenticated}
    <AdminLogin onAuthenticated={handleAuthenticated} />
{:else}
    <div data-testid="admin-dashboard">
        <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div>
                <h2 class="text-2xl font-medium text-slate-100">Manage games</h2>
                <p class="text-sm text-slate-300 mt-1">
                    {games.length} total · {archivedCount} archived
                </p>
            </div>

            <div class="flex flex-wrap gap-3">
                <button
                    type="button"
                    onclick={openCreateForm}
                    class="px-4 py-2 rounded-lg text-sm font-medium bg-blue-700 text-white
                        hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:outline-none
                        transition-colors duration-200"
                    data-testid="admin-add-game"
                >
                    Add game
                </button>

                <button
                    type="button"
                    onclick={handleLogout}
                    class="px-4 py-2 rounded-lg text-sm font-medium bg-slate-700 text-slate-100
                        hover:bg-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none
                        transition-colors duration-200"
                    data-testid="admin-logout"
                >
                    Sign out
                </button>
            </div>
        </div>

        <label class="inline-flex items-center gap-3 mb-6 text-sm text-slate-200">
            <input
                type="checkbox"
                bind:checked={showArchived}
                class="h-4 w-4 rounded border-slate-600 bg-slate-900 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                data-testid="admin-show-archived"
            />
            Show archived games
        </label>

        {#if status}
            <p
                class="mb-6 text-sm text-emerald-300"
                role="status"
                aria-live="polite"
                data-testid="admin-status"
            >
                {status}
            </p>
        {/if}

        {#if formOpen}
            <!-- Keyed so switching edit targets (or edit → add) remounts the form
                 with fresh field values instead of reusing the previous game's. -->
            {#key editingGame?.id ?? 'new'}
                <GameForm
                    game={editingGame}
                    {publishers}
                    {categories}
                    onSaved={handleSaved}
                    onCancel={closeForm}
                />
            {/key}
        {/if}

        {#if pendingArchive}
            <div
                class="mb-6 p-4 rounded-xl bg-slate-800 border border-amber-700/60"
                role="alertdialog"
                aria-labelledby="archive-confirm-text"
                data-testid="admin-archive-confirm"
            >
                <p id="archive-confirm-text" class="text-slate-100 mb-4">
                    Archive “{pendingArchive.title}”? It will be hidden from the public catalog but
                    can be restored later.
                </p>
                <div class="flex flex-wrap gap-3">
                    <button
                        type="button"
                        onclick={confirmArchive}
                        class="px-4 py-2 rounded-lg text-sm font-medium bg-red-800 text-white
                            hover:bg-red-700 focus:ring-2 focus:ring-blue-500 focus:outline-none
                            transition-colors duration-200"
                        data-testid="admin-archive-confirm-yes"
                    >
                        Yes, archive it
                    </button>
                    <button
                        type="button"
                        onclick={() => (pendingArchive = null)}
                        class="px-4 py-2 rounded-lg text-sm font-medium bg-slate-700 text-slate-100
                            hover:bg-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none
                            transition-colors duration-200"
                        data-testid="admin-archive-confirm-no"
                    >
                        Keep it
                    </button>
                </div>
            </div>
        {/if}

        {#if error}
            <div class="mb-6">
                <ErrorMessage {error} />
            </div>
        {/if}

        {#if loading}
            <div
                class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700"
                role="status"
                aria-live="polite"
                data-testid="admin-games-loading"
            >
                <p class="text-slate-300">Loading games…</p>
            </div>
        {:else if visibleGames.length === 0}
            <EmptyState message="No games to show. Add one to get started." />
        {:else}
            <AdminGameTable
                games={visibleGames}
                {busyId}
                onEdit={openEditForm}
                onArchive={(game) => (pendingArchive = game)}
                onRestore={handleRestore}
            />
        {/if}
    </div>
{/if}

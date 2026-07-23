<script lang="ts">
    import { API_ENDPOINTS } from '../config/api';

    let { onAuthenticated }: { onAuthenticated: () => void } = $props();

    let password = $state('');
    let submitting = $state(false);
    let error = $state<string | null>(null);

    const handleSubmit = async (event: SubmitEvent) => {
        event.preventDefault();

        if (!password) {
            error = 'Enter the admin password to continue.';
            return;
        }

        submitting = true;
        error = null;

        try {
            const response = await fetch(API_ENDPOINTS.login, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password }),
            });

            if (response.ok) {
                password = '';
                onAuthenticated();
            } else if (response.status === 401) {
                error = 'Incorrect password. Please try again.';
            } else {
                error = `Sign in failed: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            submitting = false;
        }
    };
</script>

<div class="max-w-md mx-auto bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-slate-700">
    <h2 class="text-2xl font-medium mb-2 text-slate-100">Admin sign in</h2>
    <p class="text-sm text-slate-300 mb-6">
        Manage the game catalog. This area is restricted to Tailspin Toys administrators.
    </p>

    <form onsubmit={handleSubmit} data-testid="admin-login-form">
        <label class="block text-sm font-medium text-slate-200 mb-2" for="admin-password">
            Admin password
        </label>
        <input
            id="admin-password"
            type="password"
            bind:value={password}
            autocomplete="current-password"
            aria-describedby={error ? 'admin-login-error' : undefined}
            aria-invalid={error ? 'true' : undefined}
            class="w-full px-4 py-2 rounded-lg bg-slate-900 text-slate-100 border border-slate-600
                placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Enter admin password"
            data-testid="admin-password-input"
        />

        {#if error}
            <p
                id="admin-login-error"
                class="mt-3 text-sm text-red-400"
                role="alert"
                data-testid="admin-login-error"
            >
                {error}
            </p>
        {/if}

        <button
            type="submit"
            disabled={submitting}
            class="mt-6 w-full px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200
                {submitting
                    ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                    : 'bg-blue-700 text-white hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:outline-none'}"
            data-testid="admin-login-submit"
        >
            {submitting ? 'Signing in…' : 'Sign in'}
        </button>
    </form>
</div>

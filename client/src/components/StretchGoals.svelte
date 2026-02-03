<script lang="ts">
    import type { StretchGoal } from '../types/game';

    let { stretchGoals = [] }: { stretchGoals: StretchGoal[] } = $props();

    function formatAmount(amount: number, goalType: string): string {
        if (goalType === 'pledge_total') {
            return `$${amount.toLocaleString()}`;
        }
        return `${amount.toLocaleString()} backers`;
    }

    function getGoalTypeLabel(goalType: string): string {
        return goalType === 'pledge_total' ? 'Funding Goal' : 'Backer Goal';
    }
</script>

{#if stretchGoals && stretchGoals.length > 0}
    <div class="space-y-4" data-testid="stretch-goals-container">
        <h2 class="text-2xl font-bold text-slate-100 mb-4">Stretch Goals</h2>

        <div class="grid gap-4">
            {#each stretchGoals as goal (goal.id)}
                <div
                    class="bg-slate-800/70 backdrop-blur-sm border border-slate-700 rounded-lg p-4 transition-all duration-200 hover:border-slate-600"
                    data-testid="stretch-goal-{goal.id}"
                >
                    <!-- Header -->
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex-1">
                            <h3 class="text-lg font-semibold text-slate-100 mb-1" data-testid="stretch-goal-title">
                                {goal.title}
                            </h3>
                            <span class="text-xs font-medium px-2 py-1 rounded bg-blue-900/60 text-blue-300">
                                {getGoalTypeLabel(goal.goalType)}
                            </span>
                        </div>

                        {#if goal.isAchieved}
                            <div class="flex items-center gap-1 bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm font-medium" data-testid="stretch-goal-achieved">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                </svg>
                                Achieved!
                            </div>
                        {/if}
                    </div>

                    <!-- Description -->
                    <p class="text-slate-400 text-sm mb-4" data-testid="stretch-goal-description">
                        {goal.description}
                    </p>

                    <!-- Progress Bar -->
                    <div class="space-y-2">
                        <div class="flex justify-between text-sm">
                            <span class="text-slate-300" data-testid="stretch-goal-current">
                                {formatAmount(goal.currentAmount, goal.goalType)}
                            </span>
                            <span class="text-slate-400" data-testid="stretch-goal-target">
                                {formatAmount(goal.targetAmount, goal.goalType)}
                            </span>
                        </div>

                        <div class="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                            <div
                                class="h-full rounded-full transition-all duration-500 {goal.isAchieved ? 'bg-green-500' : 'bg-gradient-to-r from-blue-500 to-purple-500'}"
                                style="width: {Math.min(goal.progressPercentage, 100)}%"
                                data-testid="stretch-goal-progress-bar"
                            ></div>
                        </div>

                        <div class="text-right">
                            <span class="text-sm font-medium {goal.isAchieved ? 'text-green-400' : 'text-slate-300'}" data-testid="stretch-goal-percentage">
                                {goal.progressPercentage.toFixed(1)}% funded
                            </span>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    </div>
{/if}

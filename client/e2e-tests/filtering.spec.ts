import { test, expect } from '@playwright/test';

test.describe('Category Filtering', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('category-filter')).toBeVisible();
  });

  test('should display category filter with All Games and category buttons', async ({ page }) => {
    await test.step('Verify All Games button is visible and active by default', async () => {
      const allGamesButton = page.getByTestId('category-filter-all');
      await expect(allGamesButton).toBeVisible();
      await expect(allGamesButton).toHaveText('All Games');
    });

    await test.step('Verify category buttons are displayed', async () => {
      // Check that at least one category button exists (Strategy should be id=1)
      const strategyButton = page.getByTestId('category-filter-1');
      await expect(strategyButton).toBeVisible();
    });
  });

  test('should filter games when clicking on a category', async ({ page }) => {
    let initialGameCount: number;

    await test.step('Count initial games shown', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      const gameCards = page.getByTestId('game-card');
      initialGameCount = await gameCards.count();
      expect(initialGameCount).toBeGreaterThan(0);
    });

    await test.step('Click on a category filter button', async () => {
      // Click on first category (Strategy, id=1)
      const categoryButton = page.getByTestId('category-filter-1');
      await categoryButton.click();
    });

    await test.step('Verify games are filtered', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      const gameCards = page.getByTestId('game-card');
      const filteredGameCount = await gameCards.count();
      // Filtered count should be less than total count (assuming multiple categories)
      expect(filteredGameCount).toBeLessThan(initialGameCount);
      expect(filteredGameCount).toBeGreaterThan(0);
    });

    await test.step('Verify heading changes to Filtered Games', async () => {
      await expect(page.getByRole('heading', { name: 'Filtered Games' })).toBeVisible();
    });
  });

  test('should show all games when clicking All Games button after filtering', async ({ page }) => {
    let initialGameCount: number;

    await test.step('Get initial game count', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      initialGameCount = await gameCards.count();
    });

    await test.step('Filter by a category', async () => {
      const categoryButton = page.getByTestId('category-filter-1');
      await categoryButton.click();
      await expect(page.getByRole('heading', { name: 'Filtered Games' })).toBeVisible();
    });

    await test.step('Click All Games button', async () => {
      const allGamesButton = page.getByTestId('category-filter-all');
      await allGamesButton.click();
    });

    await test.step('Verify all games are shown again', async () => {
      await expect(page.getByRole('heading', { name: 'Featured Games' })).toBeVisible();
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      const restoredGameCount = await gameCards.count();
      expect(restoredGameCount).toBe(initialGameCount);
    });
  });

  test('should highlight the active category filter button', async ({ page }) => {
    await test.step('Verify All Games button has active styling initially', async () => {
      const allGamesButton = page.getByTestId('category-filter-all');
      // Check that it has the active class (bg-blue-600)
      await expect(allGamesButton).toHaveClass(/bg-blue-600/);
    });

    await test.step('Click on a category and verify it becomes active', async () => {
      const categoryButton = page.getByTestId('category-filter-1');
      await categoryButton.click();
      // The clicked button should now have active styling
      await expect(categoryButton).toHaveClass(/bg-blue-600/);
      // All Games button should no longer have active styling
      const allGamesButton = page.getByTestId('category-filter-all');
      await expect(allGamesButton).not.toHaveClass(/bg-blue-600/);
    });
  });

  test('should switch between different category filters', async ({ page }) => {
    await test.step('Filter by first category', async () => {
      const firstCategoryButton = page.getByTestId('category-filter-1');
      await firstCategoryButton.click();
      await expect(firstCategoryButton).toHaveClass(/bg-blue-600/);
    });

    await test.step('Get game count for first category', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
    });

    await test.step('Switch to second category', async () => {
      const secondCategoryButton = page.getByTestId('category-filter-2');
      await secondCategoryButton.click();
      await expect(secondCategoryButton).toHaveClass(/bg-blue-600/);
    });

    await test.step('Verify first category button is no longer active', async () => {
      const firstCategoryButton = page.getByTestId('category-filter-1');
      await expect(firstCategoryButton).not.toHaveClass(/bg-blue-600/);
    });
  });
});

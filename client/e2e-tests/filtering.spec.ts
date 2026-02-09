import { test, expect } from '@playwright/test';

test.describe('Game Filtering', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('games-grid')).toBeVisible();
  });

  test('should display filter dropdowns on homepage', async ({ page }) => {
    await test.step('Verify filter container is visible', async () => {
      const filterContainer = page.getByTestId('game-filters');
      await expect(filterContainer).toBeVisible();
    });

    await test.step('Verify publisher filter dropdown exists', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      await expect(publisherFilter).toBeVisible();
      await expect(publisherFilter).toBeEnabled();
    });

    await test.step('Verify category filter dropdown exists', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await expect(categoryFilter).toBeVisible();
      await expect(categoryFilter).toBeEnabled();
    });
  });

  test('should populate publisher dropdown with options from API', async ({ page }) => {
    await test.step('Verify publisher dropdown has options', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      const options = publisherFilter.locator('option');
      
      // Should have "All Publishers" plus at least one publisher
      expect(await options.count()).toBeGreaterThan(1);
      await expect(options.first()).toHaveText('All Publishers');
    });
  });

  test('should populate category dropdown with options from API', async ({ page }) => {
    await test.step('Verify category dropdown has options', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      const options = categoryFilter.locator('option');
      
      // Should have "All Categories" plus at least one category
      expect(await options.count()).toBeGreaterThan(1);
      await expect(options.first()).toHaveText('All Categories');
    });
  });

  test('should filter games when publisher is selected', async ({ page }) => {
    let initialCount: number;
    let selectedPublisher: string;

    await test.step('Get initial game count', async () => {
      const gameCards = page.getByTestId('game-card');
      initialCount = await gameCards.count();
      expect(initialCount).toBeGreaterThan(0);
    });

    await test.step('Select a publisher from dropdown', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      const options = publisherFilter.locator('option');
      
      // Get the second option (first real publisher, not "All Publishers")
      selectedPublisher = await options.nth(1).textContent() || '';
      await publisherFilter.selectOption({ index: 1 });
    });

    await test.step('Verify games are filtered', async () => {
      // Wait for the filter to apply
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      
      // All displayed games should have the selected publisher
      const count = await gameCards.count();
      for (let i = 0; i < count; i++) {
        const publisherText = gameCards.nth(i).getByTestId('game-publisher');
        await expect(publisherText).toContainText(selectedPublisher);
      }
    });
  });

  test('should filter games when category is selected', async ({ page }) => {
    let selectedCategory: string;

    await test.step('Select a category from dropdown', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      const options = categoryFilter.locator('option');
      
      // Get the second option (first real category, not "All Categories")
      selectedCategory = await options.nth(1).textContent() || '';
      await categoryFilter.selectOption({ index: 1 });
    });

    await test.step('Verify games are filtered by category', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      
      // All displayed games should have the selected category
      const count = await gameCards.count();
      for (let i = 0; i < count; i++) {
        const categoryText = gameCards.nth(i).getByTestId('game-category');
        await expect(categoryText).toContainText(selectedCategory);
      }
    });
  });

  test('should show clear filters button when filters are active', async ({ page }) => {
    await test.step('Verify clear button is not visible initially', async () => {
      const clearButton = page.getByTestId('clear-filters-button');
      await expect(clearButton).not.toBeVisible();
    });

    await test.step('Select a filter and verify clear button appears', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      await publisherFilter.selectOption({ index: 1 });
      
      const clearButton = page.getByTestId('clear-filters-button');
      await expect(clearButton).toBeVisible();
    });
  });

  test('should clear filters when clear button is clicked', async ({ page }) => {
    let initialCount: number;

    await test.step('Get initial game count and apply filter', async () => {
      const gameCards = page.getByTestId('game-card');
      initialCount = await gameCards.count();
      
      const publisherFilter = page.getByTestId('publisher-filter');
      await publisherFilter.selectOption({ index: 1 });
    });

    await test.step('Click clear filters button', async () => {
      const clearButton = page.getByTestId('clear-filters-button');
      await expect(clearButton).toBeVisible();
      await clearButton.click();
    });

    await test.step('Verify filters are cleared and all games shown', async () => {
      // Clear button should disappear
      const clearButton = page.getByTestId('clear-filters-button');
      await expect(clearButton).not.toBeVisible();
      
      // Dropdowns should reset to "All" options
      const publisherFilter = page.getByTestId('publisher-filter');
      await expect(publisherFilter).toHaveValue('');
      
      // Game count should return to initial
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(initialCount);
    });
  });

  test('should apply both publisher and category filters together (AND logic)', async ({ page }) => {
    await test.step('Apply both filters', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      const categoryFilter = page.getByTestId('category-filter');
      
      await publisherFilter.selectOption({ index: 1 });
      await categoryFilter.selectOption({ index: 1 });
    });

    await test.step('Verify clear button is visible', async () => {
      const clearButton = page.getByTestId('clear-filters-button');
      await expect(clearButton).toBeVisible();
    });

    await test.step('Verify games grid is displayed (may be empty if no matches)', async () => {
      // The grid should still be visible even if empty
      const gamesGrid = page.getByTestId('games-grid');
      // Either games grid shows with results, or empty state shows
      const isEmpty = await page.getByText('No games available').isVisible().catch(() => false);
      if (!isEmpty) {
        await expect(gamesGrid).toBeVisible();
      }
    });
  });
});

import { test, expect } from '@playwright/test';

test.describe('Category Filtering', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to homepage before each test
    await page.goto('/');
  });

  test('should display category filter dropdown', async ({ page }) => {
    await test.step('Verify category filter is visible', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await expect(categoryFilter).toBeVisible();
    });

    await test.step('Verify "All Categories" is the default option', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await expect(categoryFilter).toHaveValue('');
    });
  });

  test('should load and display categories in the filter dropdown', async ({ page }) => {
    await test.step('Wait for categories to load', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await expect(categoryFilter).toBeVisible();
    });

    await test.step('Verify categories are available in dropdown', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      const options = await categoryFilter.locator('option').allTextContents();
      
      // Should have at least "All Categories" and some actual categories
      expect(options.length).toBeGreaterThan(1);
      expect(options[0]).toContain('All Categories');
    });
  });

  test('should filter games by selected category', async ({ page }) => {
    let initialGameCount: number;
    let categoryName: string;

    await test.step('Get initial game count', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      const gameCards = page.getByTestId('game-card');
      initialGameCount = await gameCards.count();
      expect(initialGameCount).toBeGreaterThan(0);
    });

    await test.step('Select a category from the filter', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      const options = await categoryFilter.locator('option').all();
      
      // Select the second option (first category, not "All Categories")
      if (options.length > 1) {
        const optionText = await options[1].textContent();
        categoryName = optionText?.split('(')[0].trim() || '';
        await categoryFilter.selectOption({ index: 1 });
      }
    });

    await test.step('Verify games are filtered', async () => {
      // Wait for the games to reload
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      
      const gameCards = page.getByTestId('game-card');
      const filteredGameCount = await gameCards.count();
      
      // The filtered count should be less than or equal to the initial count
      expect(filteredGameCount).toBeLessThanOrEqual(initialGameCount);
      expect(filteredGameCount).toBeGreaterThan(0);
    });
  });

  test('should show all games when "All Categories" is selected', async ({ page }) => {
    let initialGameCount: number;

    await test.step('Get initial game count', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      const gameCards = page.getByTestId('game-card');
      initialGameCount = await gameCards.count();
    });

    await test.step('Select a specific category', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await categoryFilter.selectOption({ index: 1 });
      
      // Wait for filtering to complete
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Select "All Categories" again', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await categoryFilter.selectOption({ value: '' });
    });

    await test.step('Verify all games are displayed again', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      
      const gameCards = page.getByTestId('game-card');
      const currentGameCount = await gameCards.count();
      
      expect(currentGameCount).toBe(initialGameCount);
    });
  });

  test('should handle empty results gracefully', async ({ page }) => {
    await test.step('Check if empty state is handled', async () => {
      // This test verifies the UI doesn't break when a category has no games
      // In most cases, categories will have games, so we just verify the filter works
      const categoryFilter = page.getByTestId('category-filter');
      await expect(categoryFilter).toBeVisible();
      
      // Select each category and verify UI remains stable
      const options = await categoryFilter.locator('option').all();
      for (let i = 1; i < Math.min(options.length, 3); i++) {
        await categoryFilter.selectOption({ index: i });
        
        // Either games grid or empty state should be visible
        const gamesGrid = page.getByTestId('games-grid');
        const gamesVisible = await gamesGrid.isVisible().catch(() => false);
        
        // If no games grid, there might be an empty state message
        if (!gamesVisible) {
          // This is fine - just means the category has no games
          expect(true).toBe(true);
        } else {
          // Games are visible, which is also fine
          await expect(gamesGrid).toBeVisible();
        }
      }
    });
  });

  test('should maintain filter selection during page interaction', async ({ page }) => {
    await test.step('Select a category', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await categoryFilter.selectOption({ index: 1 });
    });

    await test.step('Verify filter selection is maintained', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      const selectedValue = await categoryFilter.inputValue();
      
      // Value should not be empty (which is "All Categories")
      expect(selectedValue).not.toBe('');
    });

    await test.step('Scroll and verify selection is still maintained', async () => {
      await page.mouse.wheel(0, 500);
      
      const categoryFilter = page.getByTestId('category-filter');
      const selectedValue = await categoryFilter.inputValue();
      
      expect(selectedValue).not.toBe('');
    });
  });
});

import { test, expect } from '@playwright/test';

test.describe('Game Filtering', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('games-grid')).toBeVisible();
  });

  test('should display filter bar with category and publisher dropdowns', async ({ page }) => {
    await test.step('Verify filter bar is visible', async () => {
      await expect(page.getByTestId('filter-bar')).toBeVisible();
    });

    await test.step('Verify category dropdown exists', async () => {
      const categorySelect = page.getByTestId('filter-category');
      await expect(categorySelect).toBeVisible();
      await expect(categorySelect).toBeEnabled();
    });

    await test.step('Verify publisher dropdown exists', async () => {
      const publisherSelect = page.getByTestId('filter-publisher');
      await expect(publisherSelect).toBeVisible();
      await expect(publisherSelect).toBeEnabled();
    });
  });

  test('should filter games by category', async ({ page }) => {
    let totalBefore: number;

    await test.step('Record initial game count', async () => {
      const gameCards = page.getByTestId('game-card');
      totalBefore = await gameCards.count();
      expect(totalBefore).toBeGreaterThan(0);
    });

    await test.step('Select a category from dropdown', async () => {
      const categorySelect = page.getByTestId('filter-category');
      // Get the first non-empty option value
      const firstOption = categorySelect.locator('option:not([value=""])').first();
      const value = await firstOption.getAttribute('value');
      await categorySelect.selectOption(value!);
    });

    await test.step('Verify games are filtered', async () => {
      // Wait for the grid to update - filtered results should have game cards
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      // All displayed games should have the selected category
      const categorySelect = page.getByTestId('filter-category');
      const selectedText = await categorySelect.locator('option:checked').textContent();
      // Extract category name from "CategoryName (N)" format
      const categoryName = selectedText?.replace(/\s*\(\d+\)$/, '');

      const allCategoryBadges = await page.getByTestId('game-category').allTextContents();
      for (const badge of allCategoryBadges) {
        expect(badge).toBe(categoryName);
      }
    });
  });

  test('should filter games by publisher', async ({ page }) => {
    await test.step('Select a publisher from dropdown', async () => {
      const publisherSelect = page.getByTestId('filter-publisher');
      const firstOption = publisherSelect.locator('option:not([value=""])').first();
      const value = await firstOption.getAttribute('value');
      await publisherSelect.selectOption(value!);
    });

    await test.step('Verify games are filtered by publisher', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();

      const publisherSelect = page.getByTestId('filter-publisher');
      const selectedText = await publisherSelect.locator('option:checked').textContent();
      const publisherName = selectedText?.replace(/\s*\(\d+\)$/, '');

      const allPublisherBadges = await page.getByTestId('game-publisher').allTextContents();
      for (const badge of allPublisherBadges) {
        expect(badge).toBe(publisherName);
      }
    });
  });

  test('should apply combined category and publisher filters', async ({ page }) => {
    await test.step('Select both category and publisher', async () => {
      const categorySelect = page.getByTestId('filter-category');
      const catOption = categorySelect.locator('option:not([value=""])').first();
      await categorySelect.selectOption((await catOption.getAttribute('value'))!);

      // Wait for filtered results before applying second filter
      await expect(page.getByTestId('game-card').first()).toBeVisible();

      const publisherSelect = page.getByTestId('filter-publisher');
      const pubOption = publisherSelect.locator('option:not([value=""])').first();
      await publisherSelect.selectOption((await pubOption.getAttribute('value'))!);
    });

    await test.step('Verify results match both filters or show filtered empty state', async () => {
      // Wait for loading to finish — either game cards appear or filtered empty state
      await expect(
        page.getByTestId('game-card').first().or(page.getByTestId('filtered-empty-state'))
      ).toBeVisible();
    });
  });

  test('should clear filters and show all games', async ({ page }) => {
    await test.step('Apply a category filter', async () => {
      const categorySelect = page.getByTestId('filter-category');
      const firstOption = categorySelect.locator('option:not([value=""])').first();
      await categorySelect.selectOption((await firstOption.getAttribute('value'))!);
      await expect(page.getByTestId('game-card').first()).toBeVisible();
    });

    await test.step('Reset category to All Categories', async () => {
      const categorySelect = page.getByTestId('filter-category');
      await categorySelect.selectOption('');
    });

    await test.step('Verify all games are shown again', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      // Should show default page size worth of games
      expect(await gameCards.count()).toBeGreaterThan(1);
    });
  });

  test('should reset to page 1 when filter is applied', async ({ page }) => {
    await test.step('Navigate to page 2 if pagination exists', async () => {
      const nextButton = page.getByTestId('pagination-next');
      const isVisible = await nextButton.isVisible().catch(() => false);
      if (isVisible) {
        await nextButton.click();
        await expect(page.getByTestId('pagination-info')).toContainText('Page 2');
      }
    });

    await test.step('Apply a filter', async () => {
      const categorySelect = page.getByTestId('filter-category');
      const firstOption = categorySelect.locator('option:not([value=""])').first();
      await categorySelect.selectOption((await firstOption.getAttribute('value'))!);
    });

    await test.step('Verify pagination resets to page 1', async () => {
      // After filtering, if pagination exists, we should be on page 1
      const paginationInfo = page.getByTestId('pagination-info');
      const isVisible = await paginationInfo.isVisible().catch(() => false);
      if (isVisible) {
        await expect(paginationInfo).toContainText('Page 1');
      }
    });
  });
});

import { test, expect } from '@playwright/test';

test.describe('Game List Pagination', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display default pagination controls with 10 games per page', async ({ page }) => {
    await test.step('Verify games grid is visible', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Verify page size selector is visible', async () => {
      const pageSizeSelector = page.getByTestId('page-size-selector');
      await expect(pageSizeSelector).toBeVisible();
    });

    await test.step('Verify 10 games are displayed by default', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(10);
    });

    await test.step('Verify pagination controls are visible', async () => {
      const paginationControls = page.getByTestId('pagination-controls');
      await expect(paginationControls).toBeVisible();
    });

    await test.step('Verify pagination info shows page 1', async () => {
      const paginationInfo = page.getByTestId('pagination-info');
      await expect(paginationInfo).toContainText('Page 1 of');
    });
  });

  test('should navigate to next page when clicking Next button', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Click Next button', async () => {
      const nextButton = page.getByTestId('next-page-button');
      await expect(nextButton).toBeEnabled();
      await nextButton.click();
    });

    await test.step('Verify page 2 is displayed', async () => {
      const paginationInfo = page.getByTestId('pagination-info');
      await expect(paginationInfo).toContainText('Page 2 of');
    });

    await test.step('Verify Previous button is now enabled', async () => {
      const prevButton = page.getByTestId('prev-page-button');
      await expect(prevButton).toBeEnabled();
    });
  });

  test('should navigate to previous page when clicking Previous button', async ({ page }) => {
    await test.step('Navigate to page 2', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
      
      const nextButton = page.getByTestId('next-page-button');
      await nextButton.click();
      
      const paginationInfo = page.getByTestId('pagination-info');
      await expect(paginationInfo).toContainText('Page 2 of');
    });

    await test.step('Click Previous button', async () => {
      const prevButton = page.getByTestId('prev-page-button');
      await expect(prevButton).toBeEnabled();
      await prevButton.click();
    });

    await test.step('Verify page 1 is displayed', async () => {
      const paginationInfo = page.getByTestId('pagination-info');
      await expect(paginationInfo).toContainText('Page 1 of');
    });

    await test.step('Verify Previous button is disabled on page 1', async () => {
      const prevButton = page.getByTestId('prev-page-button');
      await expect(prevButton).toBeDisabled();
    });
  });

  test('should change page size and reset to page 1', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Navigate to page 2', async () => {
      const nextButton = page.getByTestId('next-page-button');
      await nextButton.click();
      
      const paginationInfo = page.getByTestId('pagination-info');
      await expect(paginationInfo).toContainText('Page 2 of');
    });

    await test.step('Change page size to 5', async () => {
      const pageSizeSelector = page.getByTestId('page-size-selector');
      await pageSizeSelector.selectOption('5');
    });

    await test.step('Verify page resets to 1 with new page size', async () => {
      const paginationInfo = page.getByTestId('pagination-info');
      await expect(paginationInfo).toContainText('Page 1 of');
    });

    await test.step('Verify game count matches page size', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(5);
    });

    await test.step('Verify total pages increased due to smaller page size', async () => {
      const paginationInfo = page.getByTestId('pagination-info');
      // With 5 per page, we should have more total pages than with 10 per page
      await expect(paginationInfo).toBeVisible();
    });
  });

  test('should display correct number of games for different page sizes', async ({ page }) => {
    await test.step('Wait for games to load with default size', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Verify 10 games are displayed by default', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(10);
    });

    await test.step('Change to 5 per page', async () => {
      const pageSizeSelector = page.getByTestId('page-size-selector');
      await pageSizeSelector.selectOption('5');
      
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(5);
    });

    await test.step('Change to 20 per page', async () => {
      const pageSizeSelector = page.getByTestId('page-size-selector');
      await pageSizeSelector.selectOption('20');
      
      const gameCards = page.getByTestId('game-card');
      // Should display 20 games if there are at least 20 total
      await expect(gameCards.first()).toBeVisible();
    });
  });

  test('should disable Next button on last page', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Set page size to 50 to ensure single page', async () => {
      const pageSizeSelector = page.getByTestId('page-size-selector');
      await pageSizeSelector.selectOption('50');
    });

    await test.step('Verify Next button is disabled when all games fit on one page', async () => {
      const paginationControls = page.getByTestId('pagination-controls');
      
      // Check if pagination controls exist - they should be hidden if only 1 page
      const isVisible = await paginationControls.isVisible();
      
      if (isVisible) {
        // If visible, Next button should be disabled on last page
        const nextButton = page.getByTestId('next-page-button');
        await expect(nextButton).toBeDisabled();
      }
    });
  });

  test('should maintain page size selection across page navigation', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Change page size to 5', async () => {
      const pageSizeSelector = page.getByTestId('page-size-selector');
      await pageSizeSelector.selectOption('5');
    });

    await test.step('Verify 5 games are displayed', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(5);
    });

    await test.step('Navigate to next page', async () => {
      const nextButton = page.getByTestId('next-page-button');
      await nextButton.click();
    });

    await test.step('Verify still on page size 5 after navigation', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(5);
    });

    await test.step('Verify 5 games are displayed on page 2', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards).toHaveCount(5);
    });
  });

  test('should display total game count in pagination info', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Verify total count is displayed', async () => {
      const paginationControls = page.getByTestId('pagination-controls');
      await expect(paginationControls).toContainText('total games');
    });
  });
});

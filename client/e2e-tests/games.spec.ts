import { test, expect, type Response } from '@playwright/test';

test.describe('Game Listing and Navigation', () => {
  test('should display games with titles on index page', async ({ page }) => {
    await test.step('Navigate to homepage', async () => {
      await page.goto('/');
    });

    await test.step('Verify games grid is visible', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Verify game cards are displayed', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      expect(await gameCards.count()).toBeGreaterThan(0);
    });

    await test.step('Verify game cards have titles with content', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first().getByTestId('game-title')).toBeVisible();
      await expect(gameCards.first().getByTestId('game-title')).not.toBeEmpty();
    });
  });

  test('should navigate to correct game details page when clicking on a game', async ({ page }) => {
    let gameId: string | null;
    let gameTitle: string | null;

    await test.step('Navigate to homepage and wait for games to load', async () => {
      await page.goto('/');
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Get first game information and click it', async () => {
      const firstGameCard = page.getByTestId('game-card').first();
      gameId = await firstGameCard.getAttribute('data-game-id');
      gameTitle = await firstGameCard.getAttribute('data-game-title');
      await firstGameCard.click();
    });

    await test.step('Verify navigation to game details page', async () => {
      await expect(page).toHaveURL(`/game/${gameId}`);
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Verify game title matches clicked game', async () => {
      if (gameTitle) {
        await expect(page.getByTestId('game-details-title')).toHaveText(gameTitle);
      }
    });
  });

  test('should display game details with all required information', async ({ page }) => {
    await test.step('Navigate to specific game details page', async () => {
      await page.goto('/game/1');
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Verify game title is displayed', async () => {
      const gameTitle = page.getByTestId('game-details-title');
      await expect(gameTitle).toBeVisible();
      await expect(gameTitle).not.toBeEmpty();
    });

    await test.step('Verify game description is displayed', async () => {
      const gameDescription = page.getByTestId('game-details-description');
      await expect(gameDescription).toBeVisible();
      await expect(gameDescription).not.toBeEmpty();
    });

    await test.step('Verify publisher or category information is present', async () => {
      const publisherExists = await page.getByTestId('game-details-publisher').isVisible();
      const categoryExists = await page.getByTestId('game-details-category').isVisible();
      expect(publisherExists || categoryExists).toBeTruthy();

      if (publisherExists) {
        await expect(page.getByTestId('game-details-publisher')).not.toBeEmpty();
      }

      if (categoryExists) {
        await expect(page.getByTestId('game-details-category')).not.toBeEmpty();
      }
    });
  });

  test('should filter games by publisher and category', async ({ page }) => {
    await test.step('Navigate to homepage and wait for filter controls', async () => {
      await page.goto('/');
      await expect(page.getByTestId('publisher-filter')).toBeVisible();
      await expect(page.getByTestId('category-filter')).toBeVisible();
    });

    await test.step('Filter by a publisher and verify visible game publishers match', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      const publisherOptions = await publisherFilter.locator('option').allTextContents();
      expect(publisherOptions.length).toBeGreaterThan(1);

      const chosenPublisher = publisherOptions[1];
      await publisherFilter.selectOption({ label: chosenPublisher });

      const gamePublishers = page.getByTestId('game-publisher');
      await expect(gamePublishers.first()).toBeVisible();

      const publisherCount = await gamePublishers.count();
      expect(publisherCount).toBeGreaterThan(0);

      for (let index = 0; index < publisherCount; index++) {
        await expect(gamePublishers.nth(index)).toHaveText(chosenPublisher);
      }
    });

    await test.step('Filter by a category and verify visible game categories match', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      const categoryOptions = await categoryFilter.locator('option').allTextContents();
      expect(categoryOptions.length).toBeGreaterThan(1);

      const chosenCategory = categoryOptions[1];
      await categoryFilter.selectOption({ label: chosenCategory });

      const gameCategories = page.getByTestId('game-category');
      await expect(gameCategories.first()).toBeVisible();

      const categoryCount = await gameCategories.count();
      expect(categoryCount).toBeGreaterThan(0);

      for (let index = 0; index < categoryCount; index++) {
        await expect(gameCategories.nth(index)).toHaveText(chosenCategory);
      }
    });
  });

  test('should display a button to back the game', async ({ page }) => {
    await test.step('Navigate to game details page', async () => {
      await page.goto('/game/1');
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Verify back game button is visible and enabled', async () => {
      const backButton = page.getByTestId('support-game-button');
      await expect(backButton).toBeVisible();
      await expect(backButton).toContainText('Support This Game');
      await expect(backButton).toBeEnabled();
    });
  });

  test('should be able to navigate back to home from game details', async ({ page }) => {
    await test.step('Navigate to game details page', async () => {
      await page.goto('/game/1');
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Click back to all games link', async () => {
      const backLink = page.getByRole('link', { name: /back to all games/i });
      await expect(backLink).toBeVisible();
      await backLink.click();
    });

    await test.step('Verify navigation back to homepage', async () => {
      await expect(page).toHaveURL('/');
      await expect(page.getByTestId('games-grid')).toBeVisible();
    });
  });

  test('should handle navigation to non-existent game gracefully', async ({ page }) => {
    let response: Response | null;

    await test.step('Navigate to non-existent game', async () => {
      response = await page.goto('/game/99999');
    });

    await test.step('Verify page handles error gracefully', async () => {
      expect(response?.status()).toBeLessThan(500);
      await expect(page).toHaveTitle(/Game Details - Tailspin Toys/);
    });
  });

  test('should display error message for non-existent game', async ({ page }) => {
    await test.step('Navigate to non-existent game', async () => {
      await page.goto('/game/99999');
    });

    await test.step('Verify error message is displayed to the user', async () => {
      const errorContainer = page.getByTestId('error-message');
      await expect(errorContainer).toBeVisible();

      const errorText = page.getByTestId('error-text');
      await expect(errorText).toBeVisible();
      await expect(errorText).not.toBeEmpty();
    });
  });

  test('should toggle support status when clicking the support button', async ({ page }) => {
    await test.step('Navigate to game details page', async () => {
      await page.goto('/game/1');
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Verify button initially shows "Support This Game"', async () => {
      const supportButton = page.getByTestId('support-game-button');
      await expect(supportButton).toContainText('Support This Game');
      await expect(supportButton).toHaveAttribute('aria-pressed', 'false');
    });

    await test.step('Click support button and verify status changes to "Supported"', async () => {
      await page.getByTestId('support-game-button').click();
      const supportButton = page.getByTestId('support-game-button');
      await expect(supportButton).toContainText('Supported');
      await expect(supportButton).toHaveAttribute('aria-pressed', 'true');
    });

    await test.step('Click again to toggle off and verify status reverts', async () => {
      await page.getByTestId('support-game-button').click();
      const supportButton = page.getByTestId('support-game-button');
      await expect(supportButton).toContainText('Support This Game');
      await expect(supportButton).toHaveAttribute('aria-pressed', 'false');
    });
  });

  test('should display heart icon on game card after supporting a game', async ({ page }) => {
    let gameId: string | null = null;

    await test.step('Navigate to homepage and get the first game ID', async () => {
      await page.goto('/');
      await expect(page.getByTestId('games-grid')).toBeVisible();
      const firstCard = page.getByTestId('game-card').first();
      gameId = await firstCard.getAttribute('data-game-id');
    });

    await test.step('Navigate to the game details page and support the game', async () => {
      await page.goto(`/game/${gameId}`);
      await expect(page.getByTestId('game-details')).toBeVisible();
      await page.getByTestId('support-game-button').click();
      await expect(page.getByTestId('support-game-button')).toContainText('Supported');
    });

    await test.step('Navigate to homepage and verify heart icon appears on the supported game card', async () => {
      await page.goto('/');
      await expect(page.getByTestId('games-grid')).toBeVisible();
      const supportedCard = page.locator(`[data-testid="game-card"][data-game-id="${gameId}"]`);
      await expect(supportedCard.getByTestId('supported-badge')).toBeVisible();
    });

    await test.step('Verify unsupported cards do not show the heart icon', async () => {
      const allCards = page.getByTestId('game-card');
      const cardCount = await allCards.count();
      if (cardCount > 1) {
        const secondCard = allCards.nth(1);
        const secondGameId = await secondCard.getAttribute('data-game-id');
        if (secondGameId !== gameId) {
          await expect(secondCard.getByTestId('supported-badge')).toHaveCount(0);
        }
      }
    });
  });
});
import { test, expect } from '@playwright/test';

test.describe('Play Page - Space Invaders', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/play');
  });

  test('should display the page title and heading', async ({ page }) => {
    await test.step('Verify page title', async () => {
      await expect(page).toHaveTitle('Play Space Invaders - Tailspin Toys');
    });

    await test.step('Verify heading', async () => {
      await expect(page.getByRole('heading', { name: 'Space Invaders', level: 1 })).toHaveText('Space Invaders');
    });
  });

  test('should display the game component with canvas and controls', async ({ page }) => {
    await test.step('Verify game container exists', async () => {
      await expect(page.getByTestId('space-invaders-game')).toHaveCount(1);
    });

    await test.step('Verify game canvas exists', async () => {
      await expect(page.getByTestId('game-canvas')).toHaveCount(1);
    });

    await test.step('Verify start button is shown', async () => {
      await expect(page.getByTestId('start-button')).toHaveText('Start Game');
    });

    await test.step('Verify instructions are shown', async () => {
      await expect(page.getByTestId('game-instructions')).toContainText('to move');
      await expect(page.getByTestId('game-instructions')).toContainText('to shoot');
    });
  });

  test('should display score and lives indicators', async ({ page }) => {
    await test.step('Verify score display', async () => {
      await expect(page.getByTestId('score-display')).toHaveText('0');
    });

    await test.step('Verify high score display', async () => {
      await expect(page.getByTestId('high-score-display')).toHaveText('0');
    });
  });

  test('should start the game when start button is clicked', async ({ page }) => {
    await test.step('Click start button', async () => {
      await page.getByTestId('start-button').click();
    });

    await test.step('Verify start button is hidden during gameplay', async () => {
      await expect(page.getByTestId('start-button')).toHaveCount(0);
    });

    await test.step('Verify instructions are hidden during gameplay', async () => {
      await expect(page.getByTestId('game-instructions')).toHaveCount(0);
    });
  });

  test('should have a back to games link', async ({ page }) => {
    await test.step('Verify back link exists', async () => {
      await expect(page.getByTestId('back-to-games-link')).toHaveText('Back to Games');
    });

    await test.step('Navigate back to home', async () => {
      await page.getByTestId('back-to-games-link').click();
      await expect(page).toHaveURL('/');
    });
  });

  test('should be accessible from navigation menu', async ({ page }) => {
    await test.step('Navigate to home page', async () => {
      await page.goto('/');
    });

    await test.step('Open menu and click Play link', async () => {
      await page.getByRole('button', { name: 'Toggle menu' }).click();
      await page.getByRole('link', { name: 'Play' }).click();
    });

    await test.step('Verify navigation to play page', async () => {
      await expect(page).toHaveURL('/play');
      await expect(page.getByRole('heading', { name: 'Space Invaders', level: 1 })).toHaveText('Space Invaders');
    });
  });
});

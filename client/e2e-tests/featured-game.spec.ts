import { test, expect } from '@playwright/test';

test.describe('Featured Game', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display featured game in header', async ({ page }) => {
    await test.step('Wait for featured game to load', async () => {
      // Wait for the featured game section to appear
      await expect(page.getByRole('region', { name: /DevOps Dominion/i })).toBeVisible();
    });

    await test.step('Verify featured game content', async () => {
      // Check for featured badge
      await expect(page.getByText('⭐ Featured')).toBeVisible();
      
      // Check for game title
      await expect(page.getByRole('heading', { name: 'DevOps Dominion', level: 2 })).toBeVisible();
      
      // Check for category tag
      await expect(page.getByTestId('featured-game-category')).toHaveText('Strategy');
      
      // Check for publisher info
      await expect(page.getByTestId('featured-game-publisher')).toContainText('CodeForge Studios');
    });

    await test.step('Verify featured game description is present', async () => {
      // Check that description is visible
      const description = page.getByTestId('featured-game-description');
      await expect(description).toBeVisible();
      await expect(description).toContainText('DevOps Dominion');
    });

    await test.step('Verify View Details button is present and accessible', async () => {
      const viewDetailsLink = page.getByTestId('featured-game-link');
      await expect(viewDetailsLink).toBeVisible();
      await expect(viewDetailsLink).toHaveText('View Details');
      await expect(viewDetailsLink).toHaveAttribute('href', '/game/1');
      await expect(viewDetailsLink).toHaveAttribute('aria-label', 'View details for DevOps Dominion');
    });
  });

  test('should navigate to game details when clicking View Details', async ({ page }) => {
    await test.step('Wait for featured game to load', async () => {
      await expect(page.getByRole('region', { name: /DevOps Dominion/i })).toBeVisible();
    });

    await test.step('Click View Details button', async () => {
      await page.getByTestId('featured-game-link').click();
    });

    await test.step('Verify navigation to game details page', async () => {
      // Wait for navigation to complete
      await expect(page).toHaveURL(/\/game\/1/);
      
      // Verify we're on the game details page
      await expect(page.getByRole('heading', { name: 'DevOps Dominion', level: 1 })).toBeVisible();
    });
  });

  test('should have proper accessibility structure', async ({ page }) => {
    await test.step('Wait for featured game to load', async () => {
      await expect(page.getByRole('region', { name: /DevOps Dominion/i })).toBeVisible();
    });

    await test.step('Verify semantic HTML structure', async () => {
      // The featured game should be in a section with proper heading
      const featuredSection = page.getByRole('region', { name: /DevOps Dominion/i });
      await expect(featuredSection).toBeVisible();
      
      // Should have a heading level 2 for the game title
      const heading = featuredSection.getByRole('heading', { level: 2 });
      await expect(heading).toBeVisible();
      
      // Link should have descriptive aria-label
      const link = featuredSection.getByRole('link', { name: /View details for/i });
      await expect(link).toBeVisible();
    });
  });

  test('should display loading state initially', async ({ page }) => {
    // Navigate to page but intercept the API call to delay it
    await page.route('**/api/games/featured', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });
    
    await page.goto('/');
    
    await test.step('Verify loading state is shown', async () => {
      // Check for loading indicator
      await expect(page.getByRole('status', { name: 'Loading featured game' })).toBeVisible();
    });
  });
});

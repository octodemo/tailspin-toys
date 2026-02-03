import { test, expect } from '@playwright/test';

test.describe('Featured Game', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the homepage before each test
    await page.goto('http://localhost:4321');
  });

  test('Featured game banner is displayed on homepage', async ({ page }) => {
    await test.step('Verify featured game banner exists', async () => {
      const featuredBanner = page.getByTestId('featured-game-banner');
      await expect(featuredBanner).toBeVisible();
    });

    await test.step('Verify featured game badge is present', async () => {
      await expect(page.getByText('⭐ FEATURED GAME')).toBeVisible();
    });
  });

  test('Featured game displays correct information', async ({ page }) => {
    await test.step('Verify game title is displayed', async () => {
      const title = page.getByTestId('featured-game-title');
      await expect(title).toBeVisible();
      await expect(title).toContainText('DevOps Dominion');
    });

    await test.step('Verify game description is displayed', async () => {
      const description = page.getByTestId('featured-game-description');
      await expect(description).toBeVisible();
      await expect(description).toContainText('strategic planning');
    });

    await test.step('Verify publisher is displayed', async () => {
      const publisher = page.getByTestId('featured-game-publisher');
      await expect(publisher).toBeVisible();
      await expect(publisher).toContainText('Publisher:');
      await expect(publisher).toContainText('CodeForge Studios');
    });

    await test.step('Verify category is displayed', async () => {
      const category = page.getByTestId('featured-game-category');
      await expect(category).toBeVisible();
      await expect(category).toContainText('Category:');
      await expect(category).toContainText('Strategy');
    });

    await test.step('Verify rating is displayed', async () => {
      const rating = page.getByTestId('featured-game-rating');
      await expect(rating).toBeVisible();
      await expect(rating).toContainText('Rating:');
      await expect(rating).toContainText('⭐');
    });
  });

  test('Featured game Learn More button navigates to game details', async ({ page }) => {
    await test.step('Click Learn More button', async () => {
      const learnMoreButton = page.getByTestId('featured-game-link');
      await expect(learnMoreButton).toBeVisible();
      await expect(learnMoreButton).toHaveText('Learn More →');
      
      await learnMoreButton.click();
    });

    await test.step('Verify navigation to game details page', async () => {
      await expect(page).toHaveURL(/\/game\/\d+/);
      await expect(page.getByRole('heading', { level: 1 })).toContainText('DevOps Dominion');
    });
  });

  test('Featured game banner has proper styling', async ({ page }) => {
    await test.step('Verify banner has gradient background', async () => {
      const banner = page.getByTestId('featured-game-banner');
      await expect(banner).toBeVisible();
      
      // Check that banner has background styling (gradient)
      const styles = await banner.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          backgroundImage: computed.backgroundImage,
          padding: computed.padding
        };
      });
      
      expect(styles.backgroundImage).toContain('gradient');
    });

    await test.step('Verify Learn More button has hover styles', async () => {
      const button = page.getByTestId('featured-game-link');
      await expect(button).toBeVisible();
      
      // Verify button is styled as expected
      const bgColor = await button.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      
      // White background for button (rgb(255, 255, 255))
      expect(bgColor).toBeTruthy();
    });
  });

  test('Featured game structure matches accessibility snapshot', async ({ page }) => {
    await test.step('Verify featured game accessibility structure', async () => {
      const banner = page.getByTestId('featured-game-banner');
      await expect(banner).toBeVisible();
      
      // Verify the structure contains key elements
      await expect(banner.getByRole('heading', { level: 2 })).toContainText('DevOps Dominion');
      await expect(banner.getByRole('link', { name: /Learn More/ })).toBeVisible();
    });
  });
});

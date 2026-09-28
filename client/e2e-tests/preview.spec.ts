import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const previewRoutes = ['/preview', '/preview/tabletop', '/preview/pipeline', '/preview/arcade', '/preview/type'];

test.describe('Design preview routes', () => {
  for (const route of previewRoutes) {
    test(`${route} renders the live catalog accessibly`, async ({ page }) => {
      const response = await page.goto(route);

      await test.step('Verify the route and catalog content', async () => {
        expect(response?.status()).toBe(200);
        await expect(page.getByRole('main')).toBeVisible();
        await expect(page.getByText(/illustrative/i).first()).toBeVisible();

        if (route === '/preview') {
          await expect(page.getByTestId('preview-chooser')).toBeVisible();
        } else {
          await expect(page.getByTestId('preview-catalog')).toBeVisible();
          expect(await page.getByTestId('preview-game-card').count()).toBeGreaterThan(0);
        }
      });

      await test.step('Verify WCAG 2.1 AA accessibility', async () => {
        const results = await new AxeBuilder({ page })
          .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
          .analyze();

        expect(results.violations).toEqual([]);
      });
    });
  }

  test('chooser links to every visual direction', async ({ page }) => {
    await page.goto('/preview');

    for (const direction of ['tabletop', 'pipeline', 'arcade', 'type']) {
      await expect(page.getByTestId(`preview-direction-${direction}`)).toHaveAttribute(
        'href',
        `/preview/${direction}`,
      );
    }
  });

  test('tabletop direction remains usable on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/preview/tabletop');

    await expect(page.getByTestId('preview-catalog')).toBeVisible();
    await expect(page.getByTestId('preview-game-card').first()).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
  });
});

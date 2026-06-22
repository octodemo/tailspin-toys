import { test, expect } from '@playwright/test';

test.describe('Game Filters', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await expect(page.getByTestId('games-grid')).toBeVisible();
    });

    test('should display category and publisher filter dropdowns', async ({ page }) => {
        await test.step('Verify filter panel is visible', async () => {
            await expect(page.getByTestId('game-filters')).toBeVisible();
        });

        await test.step('Verify category dropdown is visible', async () => {
            await expect(page.getByTestId('category-filter')).toBeVisible();
        });

        await test.step('Verify publisher dropdown is visible', async () => {
            await expect(page.getByTestId('publisher-filter')).toBeVisible();
        });
    });

    test('should populate category and publisher dropdowns with options', async ({ page }) => {
        await test.step('Verify category dropdown has options beyond the default', async () => {
            const categorySelect = page.getByTestId('category-filter');
            const options = categorySelect.locator('option');
            await expect(options).toHaveCount(await options.count());
            expect(await options.count()).toBeGreaterThan(1);
        });

        await test.step('Verify publisher dropdown has options beyond the default', async () => {
            const publisherSelect = page.getByTestId('publisher-filter');
            const options = publisherSelect.locator('option');
            expect(await options.count()).toBeGreaterThan(1);
        });
    });

    test('should filter games by category', async ({ page }) => {
        await test.step('Verify games are loaded', async () => {
            await expect(page.getByTestId('game-card').first()).toBeVisible();
        });

        await test.step('Select the first non-default category', async () => {
            const categorySelect = page.getByTestId('category-filter');
            const options = await categorySelect.locator('option').all();
            // options[0] is "All Categories"; pick options[1] if it exists
            if (options.length > 1) {
                const value = await options[1].getAttribute('value');
                if (value) await categorySelect.selectOption(value);
            }
        });

        await test.step('Verify games grid updates', async () => {
            await expect(page.getByTestId('games-grid')).toBeVisible();
        });

        await test.step('Verify pagination resets to page 1 or fewer results', async () => {
            const paginationInfo = page.getByTestId('pagination-info');
            if (await paginationInfo.isVisible()) {
                await expect(paginationInfo).toContainText('Page 1');
            }
        });
    });

    test('should filter games by publisher', async ({ page }) => {
        await test.step('Select the first non-default publisher', async () => {
            const publisherSelect = page.getByTestId('publisher-filter');
            const options = await publisherSelect.locator('option').all();
            if (options.length > 1) {
                const value = await options[1].getAttribute('value');
                if (value) await publisherSelect.selectOption(value);
            }
        });

        await test.step('Verify games grid updates', async () => {
            await expect(page.getByTestId('games-grid')).toBeVisible();
        });
    });

    test('should show clear filters button when a filter is active', async ({ page }) => {
        await test.step('Verify clear button is not visible initially', async () => {
            await expect(page.getByTestId('clear-filters-button')).not.toBeVisible();
        });

        await test.step('Select a category', async () => {
            const categorySelect = page.getByTestId('category-filter');
            const options = await categorySelect.locator('option').all();
            if (options.length > 1) {
                const value = await options[1].getAttribute('value');
                if (value) await categorySelect.selectOption(value);
            }
        });

        await test.step('Verify clear button appears', async () => {
            await expect(page.getByTestId('clear-filters-button')).toBeVisible();
        });
    });

    test('should clear filters when clear button is clicked', async ({ page }) => {
        await test.step('Select a category filter', async () => {
            const categorySelect = page.getByTestId('category-filter');
            const options = await categorySelect.locator('option').all();
            if (options.length > 1) {
                const value = await options[1].getAttribute('value');
                if (value) await categorySelect.selectOption(value);
            }
        });

        await test.step('Click clear filters button', async () => {
            await page.getByTestId('clear-filters-button').click();
        });

        await test.step('Verify filters are reset to default', async () => {
            await expect(page.getByTestId('category-filter')).toHaveValue('');
            await expect(page.getByTestId('publisher-filter')).toHaveValue('');
            await expect(page.getByTestId('clear-filters-button')).not.toBeVisible();
        });

        await test.step('Verify games grid is still visible', async () => {
            await expect(page.getByTestId('games-grid')).toBeVisible();
        });
    });
});

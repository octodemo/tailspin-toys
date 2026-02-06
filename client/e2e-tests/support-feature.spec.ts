import { test, expect } from '@playwright/test';

test.describe('Game Support Feature', () => {
    test.beforeEach(async ({ page }) => {
        // Clear localStorage before each test
        await page.goto('http://localhost:4321');
        await page.evaluate(() => localStorage.clear());
    });

    test('Support button toggles correctly on details page', async ({ page }) => {
        await test.step('Navigate to game details page', async () => {
            await page.goto('http://localhost:4321');
            await page.getByRole('link', { name: /view details/i }).first().click();
            await page.waitForURL(/\/game\/\d+/);
        });

        await test.step('Click support button to add support', async () => {
            const supportButton = page.getByTestId('support-game-button');
            await expect(supportButton).toContainText('Support This Game');
            await supportButton.click();
            await expect(supportButton).toContainText('Supported ✓');
        });

        await test.step('Click support button again to remove support', async () => {
            const supportButton = page.getByTestId('support-game-button');
            await supportButton.click();
            await expect(supportButton).toContainText('Support This Game');
        });
    });

    test('Supported games show heart badge on cards', async ({ page }) => {
        await test.step('Navigate to homepage and support a game', async () => {
            await page.goto('http://localhost:4321');
            await page.getByRole('link', { name: /view details/i }).first().click();
            await page.waitForURL(/\/game\/\d+/);
            
            const supportButton = page.getByTestId('support-game-button');
            await supportButton.click();
            await expect(supportButton).toContainText('Supported ✓');
        });

        await test.step('Return to homepage and verify heart badge appears', async () => {
            await page.goto('http://localhost:4321');
            await page.waitForSelector('[data-testid="heart-badge"]');
            const heartBadges = page.getByTestId('heart-badge');
            await expect(heartBadges).toHaveCount(1);
        });
    });

    test('Support status persists across page reloads', async ({ page }) => {
        await test.step('Support a game', async () => {
            await page.goto('http://localhost:4321');
            await page.getByRole('link', { name: /view details/i }).first().click();
            await page.waitForURL(/\/game\/\d+/);
            
            const supportButton = page.getByTestId('support-game-button');
            await supportButton.click();
            await expect(supportButton).toContainText('Supported ✓');
        });

        await test.step('Reload page and verify support status persists', async () => {
            await page.reload();
            const supportButton = page.getByTestId('support-game-button');
            await expect(supportButton).toContainText('Supported ✓');
        });

        await test.step('Navigate to homepage and verify heart badge persists', async () => {
            await page.goto('http://localhost:4321');
            const heartBadges = page.getByTestId('heart-badge');
            await expect(heartBadges).toHaveCount(1);
        });
    });

    test('localStorage stores supported game IDs correctly', async ({ page }) => {
        await page.goto('http://localhost:4321');
        
        await test.step('Support first game', async () => {
            await page.getByRole('link', { name: /view details/i }).first().click();
            await page.waitForURL(/\/game\/\d+/);
            await page.getByTestId('support-game-button').click();
        });

        await test.step('Verify localStorage contains game ID', async () => {
            const storedData = await page.evaluate(() => {
                const data = localStorage.getItem('tailspin-supported-games');
                return data ? JSON.parse(data) : [];
            });
            
            expect(Array.isArray(storedData)).toBe(true);
            expect(storedData.length).toBeGreaterThan(0);
        });
    });
});

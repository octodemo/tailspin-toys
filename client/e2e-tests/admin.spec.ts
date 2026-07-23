import { test, expect, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'tailspin-admin';

/** Unique title per test run so parallel specs never collide on catalog data. */
const uniqueTitle = (label: string): string =>
  `E2E ${label} ${Date.now()}-${Math.floor(Math.random() * 10000)}`;

/** Ids of games created during the current test, archived again in afterEach. */
let createdGameIds: string[] = [];

const signIn = async (page: Page): Promise<void> => {
  await page.goto('/admin');
  await page.getByLabel('Admin password').fill(ADMIN_PASSWORD);
  await page.getByTestId('admin-login-submit').click();
  await expect(page.getByTestId('admin-dashboard')).toBeVisible();
};

const createGame = async (page: Page, title: string): Promise<void> => {
  await page.getByTestId('admin-add-game').click();
  await page.getByTestId('game-form-title').fill(title);
  await page
    .getByTestId('game-form-description')
    .fill('A game created by the end-to-end suite to verify admin workflows');
  await page.getByTestId('game-form-publisher').selectOption({ index: 1 });
  await page.getByTestId('game-form-category').selectOption({ index: 1 });
  await page.getByTestId('game-form-rating').fill('4.2');
  await page.getByTestId('game-form-submit').click();

  await expect(page.getByTestId('admin-status')).toContainText(`Created “${title}”`);

  // Register for cleanup as soon as the row exists.
  await getGameId(page, title);
};

/** Resolve the numeric game id from its row so actions target the right record. */
const getGameId = async (page: Page, title: string): Promise<string> => {
  const row = page.getByRole('row', { name: new RegExp(title) });
  const testId = await row.getAttribute('data-testid');

  expect(testId).not.toBeNull();

  const gameId = testId!.replace('admin-game-row-', '');
  if (!createdGameIds.includes(gameId)) {
    createdGameIds.push(gameId);
  }

  return gameId;
};

test.describe('Admin catalog management', () => {
  test.beforeEach(() => {
    createdGameIds = [];
  });

  // Games created by these tests are archived afterwards so repeated local runs
  // do not accumulate test data in the public catalog.
  test.afterEach(async ({ page }) => {
    for (const gameId of createdGameIds) {
      await page.request.delete(`/api/games/${gameId}`).catch(() => undefined);
    }
    createdGameIds = [];
  });

  test('Admin area requires a password before showing the dashboard', async ({ page }) => {
    await page.goto('/admin');

    await expect(page.getByTestId('admin-login-form')).toBeVisible();
    await expect(page.getByTestId('admin-dashboard')).toHaveCount(0);
  });

  test('Incorrect password shows an error and keeps the dashboard hidden', async ({ page }) => {
    await page.goto('/admin');
    await page.getByLabel('Admin password').fill('definitely-not-the-password');
    await page.getByTestId('admin-login-submit').click();

    await expect(page.getByTestId('admin-login-error')).toContainText('Incorrect password');
    await expect(page.getByTestId('admin-dashboard')).toHaveCount(0);
  });

  test('Correct password reveals the game management table', async ({ page }) => {
    await signIn(page);

    await expect(page.getByTestId('admin-games-table')).toBeVisible();
    await expect(page.getByTestId('admin-status')).toContainText('Signed in as administrator');
  });

  test('Header exposes an admin sign in link', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /toggle menu/i }).click();

    const adminLink = page.getByTestId('nav-admin');
    await expect(adminLink).toContainText('Admin sign in');
    await expect(adminLink).toHaveAttribute('href', '/admin');

    await adminLink.click();
    await expect(page).toHaveURL('/admin');
  });

  test('Signing out returns the admin to the login form', async ({ page }) => {
    await signIn(page);

    await page.getByTestId('admin-logout').click();

    await expect(page.getByTestId('admin-login-form')).toBeVisible();
    await expect(page.getByTestId('admin-dashboard')).toHaveCount(0);
  });

  test('Admin can create a game that appears in the public catalog', async ({ page }) => {
    const title = uniqueTitle('Created');

    await signIn(page);
    await createGame(page, title);

    await test.step('New game is listed in the admin table', async () => {
      await expect(page.getByRole('row', { name: new RegExp(title) })).toBeVisible();
    });

    await test.step('New game is reachable from the public API', async () => {
      const response = await page.request.get('/api/games?pageSize=100');
      const body = await response.json();
      const titles = body.games.map((game: { title: string }) => game.title);

      expect(titles).toContain(title);
    });
  });

  test('Form validation blocks a too-short description', async ({ page }) => {
    await signIn(page);

    await page.getByTestId('admin-add-game').click();
    await page.getByTestId('game-form-title').fill(uniqueTitle('Invalid'));
    await page.getByTestId('game-form-description').fill('too short');
    await page.getByTestId('game-form-publisher').selectOption({ index: 1 });
    await page.getByTestId('game-form-category').selectOption({ index: 1 });
    await page.getByTestId('game-form-submit').click();

    await expect(page.getByTestId('game-form-error')).toContainText(
      'Description must be at least 10 characters',
    );
  });

  test('Form validation blocks an out-of-range star rating', async ({ page }) => {
    await signIn(page);

    await page.getByTestId('admin-add-game').click();
    await page.getByTestId('game-form-title').fill(uniqueTitle('Rating'));
    await page
      .getByTestId('game-form-description')
      .fill('A description that comfortably clears the minimum length');
    await page.getByTestId('game-form-publisher').selectOption({ index: 1 });
    await page.getByTestId('game-form-category').selectOption({ index: 1 });
    await page.getByTestId('game-form-rating').fill('9');
    await page.getByTestId('game-form-submit').click();

    await expect(page.getByTestId('game-form-error')).toContainText('between 0 and 5');
  });

  test('Escape closes the game form without saving', async ({ page }) => {
    await signIn(page);

    await page.getByTestId('admin-add-game').click();
    await expect(page.getByTestId('game-form')).toBeVisible();

    await page.keyboard.press('Escape');

    await expect(page.getByTestId('game-form')).toHaveCount(0);
  });

  test('Admin can edit an existing game title', async ({ page }) => {
    const title = uniqueTitle('Editable');
    const renamed = `${title} Deluxe`;

    await signIn(page);
    await createGame(page, title);

    const gameId = await getGameId(page, title);

    await page.getByTestId(`admin-edit-${gameId}`).click();
    await page.getByTestId('game-form-title').fill(renamed);
    await page.getByTestId('game-form-submit').click();

    await expect(page.getByTestId('admin-status')).toContainText(`Updated “${renamed}”`);
    await expect(page.getByRole('row', { name: new RegExp(renamed) })).toBeVisible();
  });

  test('Switching edit targets loads the newly selected game', async ({ page }) => {
    const firstTitle = uniqueTitle('SwitchA');
    const secondTitle = uniqueTitle('SwitchB');

    await signIn(page);
    await createGame(page, firstTitle);
    await createGame(page, secondTitle);

    const firstId = await getGameId(page, firstTitle);
    const secondId = await getGameId(page, secondTitle);

    await test.step('Open the form on the first game', async () => {
      await page.getByTestId(`admin-edit-${firstId}`).click();
      await expect(page.getByTestId('game-form-title')).toHaveValue(firstTitle);
    });

    await test.step('Switching to the second game reloads its values', async () => {
      await page.getByTestId(`admin-edit-${secondId}`).click();
      await expect(page.getByTestId('game-form-title')).toHaveValue(secondTitle);
    });

    await test.step('Switching to Add game clears the form', async () => {
      await page.getByTestId('admin-add-game').click();
      await expect(page.getByTestId('game-form-title')).toHaveValue('');
      await expect(page.getByTestId('game-form')).toContainText('Add a new game');
    });
  });

  test('Archiving a game hides it from the public catalog and can be undone', async ({ page }) => {
    const title = uniqueTitle('Archivable');

    await signIn(page);
    await createGame(page, title);

    const gameId = await getGameId(page, title);

    await test.step('Archive requires confirmation', async () => {
      await page.getByTestId(`admin-archive-${gameId}`).click();

      const confirmation = page.getByTestId('admin-archive-confirm');
      await expect(confirmation).toContainText(title);

      await page.getByTestId('admin-archive-confirm-yes').click();
      await expect(page.getByTestId('admin-status')).toContainText(`Archived “${title}”`);
    });

    await test.step('Archived game disappears from the admin list by default', async () => {
      await expect(page.getByRole('row', { name: new RegExp(title) })).toHaveCount(0);
    });

    await test.step('Archived game is gone from the public API', async () => {
      const response = await page.request.get('/api/games?pageSize=100');
      const body = await response.json();
      const titles = body.games.map((game: { title: string }) => game.title);

      expect(titles).not.toContain(title);
    });

    await test.step('Toggling archived games reveals it as Archived', async () => {
      await page.getByTestId('admin-show-archived').check();

      await expect(page.getByTestId(`admin-game-status-${gameId}`)).toHaveText('Archived');
    });

    await test.step('Restoring returns it to the catalog', async () => {
      await page.getByTestId(`admin-restore-${gameId}`).click();

      await expect(page.getByTestId('admin-status')).toContainText(`Restored “${title}”`);
      await expect(page.getByTestId(`admin-game-status-${gameId}`)).toHaveText('Live');

      const response = await page.request.get('/api/games?pageSize=100');
      const body = await response.json();
      const titles = body.games.map((game: { title: string }) => game.title);

      expect(titles).toContain(title);
    });
  });

  test('Keeping a game cancels the pending archive', async ({ page }) => {
    const title = uniqueTitle('Kept');

    await signIn(page);
    await createGame(page, title);

    const gameId = await getGameId(page, title);

    await page.getByTestId(`admin-archive-${gameId}`).click();
    await page.getByTestId('admin-archive-confirm-no').click();

    await expect(page.getByTestId('admin-archive-confirm')).toHaveCount(0);
    await expect(page.getByTestId(`admin-game-status-${gameId}`)).toHaveText('Live');
  });

  test('Admin login page should not have accessibility violations', async ({ page }) => {
    await page.goto('/admin');
    await expect(page.getByTestId('admin-login-form')).toBeVisible();

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Admin dashboard should not have accessibility violations', async ({ page }) => {
    await signIn(page);
    await expect(page.getByTestId('admin-games-table')).toBeVisible();

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Game form should not have accessibility violations', async ({ page }) => {
    await signIn(page);
    await page.getByTestId('admin-add-game').click();
    await expect(page.getByTestId('game-form')).toBeVisible();

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});

test.describe('Admin API protection', () => {
  test('Write endpoints reject unauthenticated requests', async ({ request }) => {
    const create = await request.post('/api/games', {
      data: { title: 'Nope', description: 'Should never be created', publisherId: 1, categoryId: 1 },
    });
    const update = await request.put('/api/games/1', { data: { title: 'Nope' } });
    const archive = await request.delete('/api/games/1');
    const restore = await request.post('/api/games/1/restore');
    const archivedList = await request.get('/api/games?includeArchived=true');

    expect(create.status()).toBe(401);
    expect(update.status()).toBe(401);
    expect(archive.status()).toBe(401);
    expect(restore.status()).toBe(401);
    expect(archivedList.status()).toBe(401);
  });

  test('Lookup endpoints are available for form dropdowns', async ({ request }) => {
    const publishers = await request.get('/api/publishers');
    const categories = await request.get('/api/categories');

    expect(publishers.status()).toBe(200);
    expect(categories.status()).toBe(200);
    expect((await publishers.json()).publishers.length).toBeGreaterThan(0);
    expect((await categories.json()).categories.length).toBeGreaterThan(0);
  });
});

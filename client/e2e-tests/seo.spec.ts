import { test, expect } from '@playwright/test';

test.describe('SEO Metadata', () => {
  test.describe('Homepage SEO', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/');
    });

    test('should have optimized page title', async ({ page }) => {
      await expect(page).toHaveTitle('Tailspin Toys - Crowdfund Developer-Themed Board Games');
    });

    test('should have meta description', async ({ page }) => {
      const description = await page.locator('meta[name="description"]').getAttribute('content');
      expect(description).toBeTruthy();
      expect(description).toContain('board games');
      expect(description).toContain('DevOps');
    });

    test('should have canonical URL', async ({ page }) => {
      const canonical = await page.locator('link[rel="canonical"]').getAttribute('href');
      expect(canonical).toBeTruthy();
      expect(canonical).toContain('tailspin-toys');
    });

    test('should have Open Graph tags', async ({ page }) => {
      const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content');
      const ogDescription = await page.locator('meta[property="og:description"]').getAttribute('content');
      const ogType = await page.locator('meta[property="og:type"]').getAttribute('content');
      
      expect(ogTitle).toBe('Tailspin Toys - Crowdfund Developer-Themed Board Games');
      expect(ogDescription).toBeTruthy();
      expect(ogType).toBe('website');
    });

    test('should have Twitter Card tags', async ({ page }) => {
      const twitterCard = await page.locator('meta[name="twitter:card"]').getAttribute('content');
      const twitterTitle = await page.locator('meta[name="twitter:title"]').getAttribute('content');
      
      expect(twitterCard).toBe('summary_large_image');
      expect(twitterTitle).toBe('Tailspin Toys - Crowdfund Developer-Themed Board Games');
    });
  });

  test.describe('Game Detail Page SEO', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/game/1');
    });

    test('should have game-specific title', async ({ page }) => {
      const title = await page.title();
      expect(title).toContain('DevOps Dominion');
      expect(title).toContain('Tailspin Toys');
    });

    test('should have game-specific meta description', async ({ page }) => {
      const description = await page.locator('meta[name="description"]').getAttribute('content');
      expect(description).toBeTruthy();
      expect(description).toContain('DevOps Dominion');
    });

    test('should have structured data (JSON-LD)', async ({ page }) => {
      const schemaScript = await page.locator('script[type="application/ld+json"]').textContent();
      expect(schemaScript).toBeTruthy();
      
      const schema = JSON.parse(schemaScript || '{}');
      expect(schema['@context']).toBe('https://schema.org');
      expect(schema['@type']).toBe('Product');
      expect(schema.name).toBe('DevOps Dominion');
      expect(schema.category).toBeTruthy();
      expect(schema.brand).toBeTruthy();
      expect(schema.offers).toBeTruthy();
      expect(schema.aggregateRating).toBeTruthy();
    });

    test('should have game-specific canonical URL', async ({ page }) => {
      const canonical = await page.locator('link[rel="canonical"]').getAttribute('href');
      expect(canonical).toContain('/game/1');
    });
  });

  test.describe('About Page SEO', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/about');
    });

    test('should have optimized title', async ({ page }) => {
      const title = await page.title();
      expect(title).toContain('About');
      expect(title).toContain('Tailspin Toys');
    });

    test('should have proper heading hierarchy with h1', async ({ page }) => {
      const h1 = page.getByRole('heading', { level: 1, name: 'About Tailspin Toys' });
      await expect(h1).toBeVisible();
    });
  });

  test.describe('Sitemap and Robots', () => {
    test('should serve robots.txt', async ({ request }) => {
      const response = await request.get('/robots.txt');
      expect(response.ok()).toBeTruthy();
      
      const content = await response.text();
      expect(content).toContain('User-agent: *');
      expect(content).toContain('Allow: /');
      expect(content).toContain('Sitemap:');
    });

    test('should serve sitemap.xml', async ({ request }) => {
      const response = await request.get('/sitemap.xml');
      expect(response.ok()).toBeTruthy();
      expect(response.headers()['content-type']).toContain('application/xml');
      
      const content = await response.text();
      expect(content).toContain('<?xml version="1.0"');
      expect(content).toContain('<urlset');
      expect(content).toContain('<loc>');
      expect(content).toContain('tailspin-toys');
    });

    test('sitemap should include homepage', async ({ request }) => {
      const response = await request.get('/sitemap.xml');
      const content = await response.text();
      expect(content).toContain('tailspin-toys.example.com/</loc>');
    });

    test('sitemap should include about page', async ({ request }) => {
      const response = await request.get('/sitemap.xml');
      const content = await response.text();
      expect(content).toContain('/about</loc>');
    });

    test('sitemap should include game pages', async ({ request }) => {
      const response = await request.get('/sitemap.xml');
      const content = await response.text();
      expect(content).toContain('/game/');
      // Should have multiple game entries
      const gameMatches = content.match(/\/game\/\d+</g);
      expect(gameMatches).toBeTruthy();
      expect(gameMatches!.length).toBeGreaterThan(0);
    });
  });
});

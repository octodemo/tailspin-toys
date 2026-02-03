# SEO Implementation Guide

This document outlines the SEO improvements implemented for the Tailspin Toys crowdfunding platform.

## Overview

The SEO enhancements ensure that game products are crawlable, discoverable, and optimized for search engines and social media sharing.

## Key Improvements

### 1. Meta Tags & Titles

#### Homepage
- **Title**: "Tailspin Toys - Crowdfund Developer-Themed Board Games"
- **Description**: "Discover and back innovative board games inspired by DevOps, software development, and tech culture. Browse featured games and join our crowdfunding community."
- **Keywords**: Developer, DevOps, board games, crowdfunding

#### Game Detail Pages
- **Dynamic Titles**: Each game has a unique title like "DevOps Dominion - Developer Board Game | Tailspin Toys"
- **Dynamic Descriptions**: Generated from game data, e.g., "Back DevOps Dominion on Tailspin Toys. In DevOps Dominion, strategic planning meets advanced deployment tactics..."

#### About Page
- **Title**: "About Tailspin Toys - DevOps & Developer Board Game Crowdfunding"
- **Description**: "Learn about Tailspin Toys, the premier crowdfunding platform for board games with DevOps and software development themes."

### 2. Open Graph & Social Media

All pages include Open Graph tags for better social media sharing:
- `og:title` - Page-specific title
- `og:description` - Page-specific description
- `og:type` - "website"
- `og:url` - Canonical URL
- `og:image` - Social sharing image

Twitter Card tags are also included:
- `twitter:card` - "summary_large_image"
- `twitter:title` - Page title
- `twitter:description` - Page description
- `twitter:image` - Social sharing image

### 3. Structured Data (Schema.org)

Game detail pages include JSON-LD structured data:
- **@type**: "Product"
- **name**: Game title
- **description**: Game description
- **category**: Game category
- **brand**: Publisher information
- **offers**: Pre-order availability
- **aggregateRating**: Star rating (when available)

This enables rich snippets in search results showing ratings, pricing, and availability.

### 4. Canonical URLs

All pages include canonical URLs to prevent duplicate content issues:
- Homepage: `https://tailspin-toys.example.com/`
- About: `https://tailspin-toys.example.com/about`
- Games: `https://tailspin-toys.example.com/game/{id}`

### 5. XML Sitemap

A dynamic sitemap is generated at `/sitemap.xml` including:
- Homepage (priority: 1.0, changefreq: daily)
- About page (priority: 0.8, changefreq: monthly)
- All game pages (priority: 0.9, changefreq: weekly)

The sitemap is dynamically generated from the games database.

### 6. Robots.txt

A robots.txt file at `/robots.txt` allows all search engine crawlers:
```
User-agent: *
Allow: /
Sitemap: https://tailspin-toys.example.com/sitemap.xml
Crawl-delay: 1
```

### 7. Heading Hierarchy

Proper semantic HTML structure:
- Homepage: H1 "Welcome to Tailspin Toys", H2 "Featured Games", H3 for individual games
- Game pages: H1 with game title, H2 for "About this game"
- About page: H1 "About Tailspin Toys" (fixed from incorrect H2)

## Implementation Details

### Files Modified

1. **`client/src/layouts/Layout.astro`**: Enhanced with meta tags, Open Graph, Twitter Cards, and canonical URLs
2. **`client/src/pages/index.astro`**: Added SEO-optimized title and description
3. **`client/src/pages/about.astro`**: Fixed heading hierarchy (H2 → H1) and added meta tags
4. **`client/src/pages/game/[id].astro`**: Added dynamic meta tags based on game data
5. **`client/astro.config.mjs`**: Added site URL for canonical URLs

### Files Created

1. **`client/src/components/GameSchema.astro`**: Reusable component for Product schema markup
2. **`client/src/pages/sitemap.xml.ts`**: Dynamic sitemap endpoint
3. **`client/public/robots.txt`**: Static robots.txt file
4. **`client/e2e-tests/seo.spec.ts`**: Comprehensive SEO tests

## Testing

All SEO improvements are covered by automated tests in `client/e2e-tests/seo.spec.ts`:

- Meta tag validation
- Open Graph tag validation
- Structured data validation
- Sitemap generation and content
- Robots.txt accessibility
- Heading hierarchy

Run tests with:
```bash
./scripts/run-e2e-tests.sh
```

## Deployment Notes

Before deploying to production:

1. **Update Domain**: Replace `https://tailspin-toys.example.com` in:
   - `client/astro.config.mjs` (site URL)
   - `client/public/robots.txt` (sitemap URL)
   - `client/src/pages/sitemap.xml.ts` (baseUrl)

2. **Add Social Media Image**: Create and add an Open Graph image at `client/public/og-image.png` (recommended size: 1200x630px)

3. **Submit to Search Engines**:
   - Google Search Console: Submit sitemap
   - Bing Webmaster Tools: Submit sitemap

## Best Practices Applied

1. **Primary Keywords**: Included naturally in titles, descriptions, and H1s
2. **Title Length**: All titles under 60 characters
3. **Description Length**: All descriptions under 155 characters
4. **Semantic HTML**: Proper heading hierarchy and landmark elements
5. **Crawlability**: All game pages discoverable via sitemap
6. **Accessibility**: ARIA labels maintained, semantic structure preserved

## Future Enhancements

Consider these additional SEO improvements:

1. **Image Alt Text**: Add descriptive alt text for game images
2. **Breadcrumbs**: Add breadcrumb navigation with schema markup
3. **FAQ Schema**: Add FAQ structured data for common questions
4. **Video Schema**: If game trailers are added
5. **User Reviews**: Implement review schema when user reviews are added
6. **Performance**: Optimize Core Web Vitals (LCP, CLS, INP)

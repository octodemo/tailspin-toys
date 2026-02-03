export const prerender = false;

export async function GET() {
  const baseUrl = 'https://tailspin-toys.example.com'; // Update with actual domain
  const currentDate = new Date().toISOString();
  
  // Fetch all games from the API
  let games = [];
  try {
    const response = await fetch('http://localhost:5100/api/games');
    if (response.ok) {
      games = await response.json();
    }
  } catch (error) {
    console.error('Error fetching games for sitemap:', error);
  }

  // Generate sitemap XML
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Homepage -->
  <url>
    <loc>${baseUrl}/</loc>
    <lastmod>${currentDate}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- About Page -->
  <url>
    <loc>${baseUrl}/about</loc>
    <lastmod>${currentDate}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <!-- Individual Game Pages -->
  ${games.map(game => `
  <url>
    <loc>${baseUrl}/game/${game.id}</loc>
    <lastmod>${currentDate}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>`).join('')}
</urlset>`;

  return new Response(sitemap, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
    }
  });
}

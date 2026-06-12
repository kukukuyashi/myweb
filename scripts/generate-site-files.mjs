import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const outDir = process.argv[2] || path.join(root, 'docs')

const { posts, SITE_URL, SITE_NAME, SITE_DESCRIPTION } = await import('../src/data/posts.js')

const base = '/myweb/'
const sorted = [...posts].sort((a, b) => b.date.localeCompare(a.date))

function escXml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

const feedItems = sorted.map(p => `
  <item>
    <title>${escXml(p.title)}</title>
    <link>${SITE_URL}${base}content/${p.id}</link>
    <guid isPermaLink="true">${SITE_URL}${base}content/${p.id}</guid>
    <pubDate>${new Date(p.date).toUTCString()}</pubDate>
    <description>${escXml(p.excerpt)}</description>
    <category>${escXml(p.category)}</category>
  </item>`).join('')

const feed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escXml(SITE_NAME)}</title>
    <link>${SITE_URL}${base}</link>
    <description>${escXml(SITE_DESCRIPTION)}</description>
    <language>zh-CN</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>${feedItems}
  </channel>
</rss>`

const urls = [
  { loc: `${SITE_URL}${base}`, priority: '1.0' },
  { loc: `${SITE_URL}${base}about`, priority: '0.6' },
  { loc: `${SITE_URL}${base}archive`, priority: '0.7' },
  { loc: `${SITE_URL}${base}music`, priority: '0.5' },
  { loc: `${SITE_URL}${base}guestbook`, priority: '0.6' },
  ...sorted.map(p => ({
    loc: `${SITE_URL}${base}content/${p.id}`,
    priority: '0.8',
    lastmod: p.date,
  })),
]

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(u => `  <url>
    <loc>${escXml(u.loc)}</loc>${u.lastmod ? `\n    <lastmod>${u.lastmod}</lastmod>` : ''}
    <changefreq>monthly</changefreq>
    <priority>${u.priority}</priority>
  </url>`).join('\n')}
</urlset>`

const robots = `User-agent: *
Allow: /

Sitemap: ${SITE_URL}${base}sitemap.xml
`

fs.mkdirSync(outDir, { recursive: true })
fs.writeFileSync(path.join(outDir, 'feed.xml'), feed.trim() + '\n', 'utf8')
fs.writeFileSync(path.join(outDir, 'sitemap.xml'), sitemap.trim() + '\n', 'utf8')
fs.writeFileSync(path.join(outDir, 'robots.txt'), robots, 'utf8')
console.log('Generated feed.xml, sitemap.xml, robots.txt →', outDir)

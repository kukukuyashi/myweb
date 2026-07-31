import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const outDir = process.argv[2] || path.join(root, 'docs')
const indexPath = path.join(outDir, 'index.html')

const base = '/myweb/'
const {
  posts,
  SITE_URL,
  SITE_NAME,
  SITE_DESCRIPTION,
  getTags,
  getPostsByTag,
  getPostCover,
} = await import('../src/data/posts.js')

function escHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function siteUrl(routePath = '') {
  const clean = String(routePath).replace(/^\//, '')
  const root = SITE_URL.replace(/\/$/, '')
  if (!clean) return `${root}/`
  return `${root}/${clean}`.replace(/([^:]\/)\/+/g, '$1')
}

function absoluteAssetUrl(relativePath) {
  const asset = String(relativePath || 'img/xiaoqing.png').replace(/^\//, '')
  return siteUrl(asset)
}

function buildArticleJsonLd(post, url) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.excerpt,
    datePublished: post.date,
    dateModified: post.updated || post.date,
    author: { '@type': 'Person', name: 'Cyinc', url: SITE_URL },
    publisher: { '@type': 'Person', name: 'Cyinc' },
    mainEntityOfPage: { '@type': 'WebPage', '@id': url },
    url,
    image: absoluteAssetUrl(getPostCover(post)),
    keywords: (post.tags || []).join(', '),
    articleSection: post.category,
    inLanguage: 'zh-CN',
  }
}

function readBuiltAssets() {
  if (!fs.existsSync(indexPath)) {
    throw new Error(`Missing ${indexPath} — run vite build first`)
  }
  const html = fs.readFileSync(indexPath, 'utf8')
  const scripts = [...html.matchAll(/<script[^>]+src="([^"]+)"[^>]*>/g)].map(m => m[1])
  const styles = [...html.matchAll(/<link[^>]+href="([^"]+\.css)"[^>]*>/g)].map(m => m[1])
  return { scripts, styles }
}

function fixContentPaths(html) {
  return html
    .replace(/href="\.\.\//g, `href="${base}`)
    .replace(/href="\.\//g, `href="${base}`)
    .replace(/src="\.\.\//g, `src="${base}`)
    .replace(/src="\.\//g, `src="${base}`)
}

function readArticleHtml(post) {
  const contentPath = path.join(root, 'Content', post.file)
  if (!fs.existsSync(contentPath)) return `<p>${escHtml(post.excerpt)}</p>`
  return fixContentPaths(fs.readFileSync(contentPath, 'utf8'))
}

function buildHtml({ title, description, url, ogType = 'website', jsonLd, bodyHtml, image }) {
  const fullTitle = title ? `${title} · ${SITE_NAME}` : SITE_NAME
  const desc = description || SITE_DESCRIPTION
  const ogImage = image || absoluteAssetUrl('img/xiaoqing.png')
  const ogImageAbs = ogImage && /^https?:/i.test(ogImage) ? ogImage : siteUrl(ogImage.replace(/^https?:\/\/[^/]+\//, ''))
  const scriptTags = assets.scripts
    .map(src => `  <script type="module" crossorigin src="${escHtml(src)}"></script>`)
    .join('\n')
  const styleTags = assets.styles
    .map(href => `  <link rel="stylesheet" crossorigin href="${escHtml(href)}">`)
    .join('\n')
  const jsonLdTag = jsonLd
    ? `  <script type="application/ld+json">${JSON.stringify(jsonLd)}</script>\n`
    : ''

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="description" content="${escHtml(desc)}">
  <meta property="og:title" content="${escHtml(fullTitle)}">
  <meta property="og:description" content="${escHtml(desc)}">
  <meta property="og:url" content="${escHtml(url)}">
  <meta property="og:type" content="${escHtml(ogType)}">
  <meta property="og:site_name" content="${escHtml(SITE_NAME)}">
  <meta property="og:image" content="${escHtml(ogImageAbs)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${escHtml(fullTitle)}">
  <meta name="twitter:description" content="${escHtml(desc)}">
  <meta name="twitter:image" content="${escHtml(ogImageAbs)}">
  <link rel="canonical" href="${escHtml(url)}">
  <link rel="icon" type="image/png" href="${base}img/xiaoqing.png">
  <link rel="alternate" type="application/rss+xml" title="${escHtml(SITE_NAME)} RSS" href="${base}feed.xml">
  <title>${escHtml(fullTitle)}</title>
${jsonLdTag}${styleTags}
${scriptTags}
  <style>
    .prerender-fallback{max-width:42rem;margin:0 auto;padding:2rem 1.25rem 4rem;font-family:system-ui,sans-serif;line-height:1.6;color:#1a1a1a}
    .prerender-fallback a{color:#e85d04}
    .prerender-fallback h1{font-size:1.5rem;margin:0 0 .5rem}
    .prerender-meta{font-size:.85rem;color:#5c5c5c;margin-bottom:1.25rem}
    .prerender-note{margin-top:2rem;padding:.75rem 1rem;border:1px dashed #c8c2ba;font-size:.8rem;color:#5c5c5c}
    .prerender-list{list-style:none;padding:0;margin:0}
    .prerender-list li{padding:.45rem 0;border-bottom:1px solid #c8c2ba}
  </style>
</head>
<body>
  <div id="app">
    <main class="prerender-fallback" data-prerender="true">
${bodyHtml}
      <p class="prerender-note">静态预览供搜索引擎阅读；交互版由 Vue 加载后替换本区域。</p>
    </main>
  </div>
</body>
</html>
`
}

function writeRoute(routePath, html) {
  const clean = routePath.replace(/^\//, '').replace(/\/$/, '')
  const dir = clean ? path.join(outDir, clean) : outDir
  fs.mkdirSync(dir, { recursive: true })
  const file = clean ? path.join(dir, 'index.html') : path.join(outDir, 'index.html')
  if (clean === '') return
  fs.writeFileSync(file, html, 'utf8')
  return file
}

const assets = readBuiltAssets()
let count = 0

const staticRoutes = [
  {
    path: 'about',
    title: '关于',
    description: 'Cyinc 是谁、技术栈、ACG 贴纸墙与联系方式。',
    body: `<h1>关于 Cyinc</h1><p class="prerender-meta">${escHtml(SITE_DESCRIPTION)}</p><p>技术笔记本 + ACG 自留地 — 写 Vue / Agent / Java，也写番剧与 OST。</p>`,
  },
  {
    path: 'archive',
    title: '归档',
    description: '按时间与标签浏览全部文章。',
    body: `<h1>文章归档</h1><p class="prerender-meta">${posts.length} 篇文章</p>`,
  },
  {
    path: 'projects',
    title: '项目',
    description: 'Cyinc 的项目与实战复盘。',
    body: `<h1>项目</h1><p class="prerender-meta">个人博客、AI 鉴陈等实战项目。</p>`,
  },
  {
    path: 'changelog',
    title: '更新日志',
    description: 'CYINC.LOG 站点功能演化记录。',
    body: `<h1>更新日志</h1><p class="prerender-meta">站点本身的功能更新，不是文章列表。</p>`,
  },
  {
    path: 'music',
    title: '音乐室',
    description: 'Cyinc 的真实歌单，静态站 FLAC 播放。',
    body: `<h1>音乐室</h1><p class="prerender-meta">OST 与 ACG 曲目收藏。</p>`,
  },
  {
    path: 'guestbook',
    title: '留言板',
    description: '欢迎留下想法、建议或打个招呼。',
    body: `<h1>留言板</h1><p class="prerender-meta">Twikoo 留言，欢迎交流。</p>`,
  },
]

for (const route of staticRoutes) {
  writeRoute(route.path, buildHtml({
    title: route.title,
    description: route.description,
    url: siteUrl(route.path),
    bodyHtml: route.body,
  }))
  count += 1
}

for (const post of posts) {
  const routePath = `content/${post.id}`
  const url = siteUrl(routePath)
  const articleHtml = readArticleHtml(post)
  const bodyHtml = `<h1>${escHtml(post.title)}</h1>
<p class="prerender-meta">${escHtml(post.date)} · ${escHtml(post.category)}</p>
<div class="prerender-article">${articleHtml}</div>`

  writeRoute(routePath, buildHtml({
    title: post.title,
    description: post.excerpt,
    url,
    ogType: 'article',
    image: absoluteAssetUrl(getPostCover(post)),
    jsonLd: buildArticleJsonLd(post, url),
    bodyHtml,
  }))
  count += 1
}

for (const tag of getTags()) {
  const tagPosts = getPostsByTag(tag)
  const routePath = `tags/${encodeURIComponent(tag)}`
  const listItems = tagPosts
    .map(p => `<li><a href="${siteUrl(`content/${p.id}`)}">${escHtml(p.title)}</a> <span>${escHtml(p.date)}</span></li>`)
    .join('\n')
  const bodyHtml = `<h1>#${escHtml(tag)}</h1>
<p class="prerender-meta">${tagPosts.length} 篇文章</p>
<ul class="prerender-list">${listItems}</ul>`

  writeRoute(routePath, buildHtml({
    title: `#${tag}`,
    description: `标签 #${tag} 下的 ${tagPosts.length} 篇文章。`,
    url: siteUrl(routePath),
    bodyHtml,
  }))
  count += 1
}

console.log(`Prerendered ${count} routes → ${outDir}`)

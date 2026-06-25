import fs from 'fs'
import path from 'path'
import { markdownToHtml } from './markdown-to-html.mjs'

export const COMMON_CATEGORIES = ['前端', '项目', '部署', 'Agent', 'Java', '学习', '技术', '小知识']

export function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export function parseTags(input) {
  if (Array.isArray(input)) return input.filter(Boolean)
  return String(input || '')
    .split(/[,，]/)
    .map((t) => t.trim())
    .filter(Boolean)
}

export function parseFrontmatter(text) {
  const normalized = text.replace(/^\uFEFF/, '')
  if (!normalized.startsWith('---\n')) return { meta: {}, body: normalized }

  const end = normalized.indexOf('\n---\n', 4)
  if (end === -1) return { meta: {}, body: normalized }

  const raw = normalized.slice(4, end)
  const body = normalized.slice(end + 5)
  const meta = {}

  for (const line of raw.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue

    const colon = trimmed.indexOf(':')
    if (colon === -1) continue

    const key = trimmed.slice(0, colon).trim()
    let value = trimmed.slice(colon + 1).trim()

    if (value.startsWith('[') && value.endsWith(']')) {
      meta[key] = value
        .slice(1, -1)
        .split(',')
        .map((s) => s.trim().replace(/^['"]|['"]$/g, ''))
        .filter(Boolean)
      continue
    }

    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }

    meta[key] = value
  }

  return { meta, body }
}

export function extractTitleFromBody(body) {
  const match = body.match(/^#\s+(.+)$/m)
  return match ? match[1].trim() : ''
}

export function extractDateFromBody(body) {
  const match = body.match(/^>\s*日期[：:]\s*(\d{4}-\d{2}-\d{2})/m)
  return match ? match[1] : ''
}

export function inferExcerpt(body, title) {
  for (const line of body.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    if (trimmed.startsWith('#')) continue
    if (trimmed.startsWith('>')) continue
    if (trimmed === '---') continue
    if (trimmed.startsWith('```')) continue
    if (trimmed.startsWith('|')) continue
    const text = trimmed
      .replace(/^-\s+/, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\*\*/g, '')
      .replace(/`/g, '')
    if (text) return text.slice(0, 140)
  }
  return `${title} — 学习笔记。`
}

function jsString(value) {
  return `'${String(value).replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'`
}

export function formatPostEntry(post) {
  const lines = [
    '  {',
    `    id: ${post.id},`,
    `    title: ${jsString(post.title)},`,
    `    date: ${jsString(post.date)},`,
    `    category: ${jsString(post.category)},`,
    `    tags: [${post.tags.map((t) => jsString(t)).join(', ')}],`,
    `    excerpt: ${jsString(post.excerpt)},`,
    `    file: ${jsString(post.file)}${post.cover ? ',' : ''}`,
  ]
  if (post.cover) lines.push(`    cover: ${jsString(post.cover)},`)
  lines.push('  },')
  return lines.join('\n')
}

export function insertPostEntry(entryText, postsPath) {
  const content = fs.readFileSync(postsPath, 'utf8')
  const marker = 'export const posts = ['
  const idx = content.indexOf(marker)
  if (idx === -1) throw new Error('posts.js 结构异常：找不到 export const posts = [')

  const insertAt = idx + marker.length
  const next = `${content.slice(0, insertAt)}\n${entryText}${content.slice(insertAt)}`
  fs.writeFileSync(postsPath, next, 'utf8')
}

export function replacePostEntryByFile(file, entryText, postsPath) {
  const content = fs.readFileSync(postsPath, 'utf8')
  const patterns = [`file: ${JSON.stringify(file)}`, `file: '${file.replace(/'/g, "\\'")}'`]

  for (const pattern of patterns) {
    const fileIdx = content.indexOf(pattern)
    if (fileIdx === -1) continue

    const start = content.lastIndexOf('  {', fileIdx)
    const end = content.indexOf('  },', fileIdx)
    if (start === -1 || end === -1) continue

    const next = `${content.slice(0, start)}${entryText}${content.slice(end + '  },'.length)}`
    fs.writeFileSync(postsPath, next, 'utf8')
    return true
  }

  return false
}

export function removePostEntryByFile(file, postsPath) {
  const content = fs.readFileSync(postsPath, 'utf8')
  const patterns = [`file: ${JSON.stringify(file)}`, `file: '${file.replace(/'/g, "\\'")}'`]

  for (const pattern of patterns) {
    const fileIdx = content.indexOf(pattern)
    if (fileIdx === -1) continue

    const start = content.lastIndexOf('  {', fileIdx)
    const end = content.indexOf('  },', fileIdx)
    if (start === -1 || end === -1) continue

    let removeEnd = end + '  },'.length
    if (content[removeEnd] === '\n') removeEnd += 1

    const next = content.slice(0, start) + content.slice(removeEnd)
    fs.writeFileSync(postsPath, next, 'utf8')
    return true
  }

  return false
}

export function buildArticleHtml({ title, date, excerpt, bodyHtml }) {
  const parts = []
  if (excerpt) parts.push(`<p class="article-intro">${escHtml(excerpt)}</p>`)
  if (!/<h1[\s>]/i.test(bodyHtml.trim())) {
    parts.push(`<h1>${escHtml(title)}</h1>`)
    parts.push(`<blockquote>日期：${escHtml(date)}</blockquote>`)
    parts.push('<hr>')
  }
  parts.push(bodyHtml.trim())
  return `${parts.join('\n')}\n`
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function resolvePostMeta({ meta, body, mdPath, posts, defaults = {} }) {
  const baseName = path.basename(mdPath, '.md')
  const htmlFile = meta.file || `${baseName}.html`
  const file = htmlFile.endsWith('.html') ? htmlFile : `${htmlFile}.html`
  const existing = posts.find((p) => p.file === file)

  const title =
    meta.title || extractTitleFromBody(body) || existing?.title || defaults.title || baseName
  const date =
    meta.date || extractDateFromBody(body) || existing?.date || defaults.date || todayISO()
  const category =
    meta.category || existing?.category || defaults.category || '学习'
  const tags = meta.tags
    ? parseTags(meta.tags)
    : existing?.tags?.length
      ? existing.tags
      : parseTags(defaults.tags || category)
  const excerpt =
    meta.excerpt || existing?.excerpt || defaults.excerpt || inferExcerpt(body, title)
  const cover = meta.cover || existing?.cover || defaults.cover || ''
  const id = existing?.id || Math.max(0, ...posts.map((p) => p.id)) + 1

  const post = { id, title, date, category, tags, excerpt, file }
  if (cover) post.cover = cover
  return post
}

export function publishMarkdownFile(mdPath, options = {}) {
  const root = options.root
  const postsPath = path.join(root, 'src/data/posts.js')
  const contentDir = path.join(root, 'Content')
  const raw = fs.readFileSync(mdPath, 'utf8')
  const { meta, body } = parseFrontmatter(raw)
  const { posts } = options

  const post = resolvePostMeta({ meta, body, mdPath, posts, defaults: options.defaults })
  const bodyHtml = markdownToHtml(body)
  const html = buildArticleHtml({
    title: post.title,
    date: post.date,
    excerpt: post.excerpt,
    bodyHtml,
  })

  const htmlPath = path.join(contentDir, post.file)
  fs.mkdirSync(contentDir, { recursive: true })
  fs.writeFileSync(htmlPath, html, 'utf8')

  const entry = formatPostEntry(post)
  const updated = replacePostEntryByFile(post.file, entry, postsPath)
  if (!updated) insertPostEntry(entry, postsPath)

  return { post, htmlPath, updated }
}

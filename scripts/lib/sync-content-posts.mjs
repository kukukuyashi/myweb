import fs from 'fs'
import path from 'path'
import {
  formatPostEntry,
  insertPostEntry,
  todayISO,
} from './post-publish.mjs'

const SKIP_HTML = new Set(['try.html', 'index.html'])

function inferCategory(title, file) {
  const hay = `${title} ${file}`
  if (/Agent|LLM|Skill|MCP/i.test(hay)) return 'Agent'
  if (/Java(?!Script)/i.test(hay) || /^JAVA/i.test(file)) return 'Java'
  if (/Twikoo|GitHub Actions|部署|重构|音乐室|FLAC|Pages/i.test(hay)) return '部署'
  if (/Flask|项目|帕朵|陈皮|root/i.test(hay)) return '项目'
  if (/Vue|Canvas|墨染|Web API|JS|前端|RhinoWeb|Three/i.test(hay)) return '前端'
  if (/FAQ|小知识|RhinoWeb/i.test(hay)) return '小知识'
  return '学习'
}

function inferTags(category, title) {
  const tags = [category]
  if (/Vue3|Vue 3/i.test(title)) tags.push('Vue3', 'Vue')
  if (/Canvas|墨染/i.test(title)) tags.push('Canvas', 'Vue')
  if (/Twikoo/i.test(title)) tags.push('Twikoo', '部署')
  if (/GitHub Actions/i.test(title)) tags.push('GitHub Actions', 'CI/CD')
  if (/Agent|LLM/i.test(title)) tags.push('AI')
  return [...new Set(tags)]
}

export function parseHtmlArticleMeta(html, file) {
  const baseName = path.basename(file, '.html')
  const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i)
  const introMatch = html.match(/<p class="article-intro">([\s\S]*?)<\/p>/i)
  const dateMatch = html.match(/日期[：:]\s*(\d{4}-\d{2}-\d{2})/)

  const title = titleMatch?.[1]?.replace(/&amp;/g, '&').trim() || baseName
  const excerpt = introMatch?.[1]
    ?.replace(/<[^>]+>/g, '')
    ?.replace(/&amp;/g, '&')
    ?.trim()
    ?.slice(0, 140) || `${title} — 学习笔记。`

  const category = inferCategory(title, file)
  return {
    title,
    date: dateMatch?.[1] || todayISO(),
    category,
    tags: inferTags(category, title),
    excerpt,
    file,
  }
}

export function listContentHtmlFiles(root) {
  const contentDir = path.join(root, 'Content')
  if (!fs.existsSync(contentDir)) return []

  return fs
    .readdirSync(contentDir)
    .filter((name) => name.endsWith('.html') && !SKIP_HTML.has(name))
    .sort((a, b) => a.localeCompare(b, 'zh-CN'))
}

export function findOrphanContent(root, posts) {
  const registered = new Set(posts.map((p) => p.file))
  const orphans = []

  for (const file of listContentHtmlFiles(root)) {
    if (registered.has(file)) continue
    const htmlPath = path.join(root, 'Content', file)
    const html = fs.readFileSync(htmlPath, 'utf8')
    const meta = parseHtmlArticleMeta(html, file)
    orphans.push({ ...meta, htmlPath })
  }

  return orphans.sort((a, b) => b.date.localeCompare(a.date))
}

export function registerContentFiles(root, posts, files = null) {
  const postsPath = path.join(root, 'src/data/posts.js')
  const orphans = findOrphanContent(root, posts)
  const targets = files
    ? orphans.filter((o) => files.includes(o.file))
    : orphans

  if (targets.length === 0) {
    return { added: [], skipped: [], posts: [...posts] }
  }

  let nextId = Math.max(0, ...posts.map((p) => p.id)) + 1
  const added = []

  for (const item of targets) {
    const post = {
      id: nextId++,
      title: item.title,
      date: item.date,
      category: item.category,
      tags: item.tags,
      excerpt: item.excerpt,
      file: item.file,
    }
    insertPostEntry(formatPostEntry(post), postsPath)
    added.push(post)
  }

  return { added, skipped: [], count: added.length }
}

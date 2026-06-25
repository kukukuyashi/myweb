import fs from 'fs'
import path from 'path'
import {
  COMMON_CATEGORIES,
  parseFrontmatter,
  removePostEntryByFile,
  resolvePostMeta,
  todayISO,
} from './post-publish.mjs'

export { COMMON_CATEGORIES, todayISO }

export const NOTE_FOLDERS = [...COMMON_CATEGORIES, '_drafts']

export function getNotesRoot(root) {
  return path.join(root, '笔记')
}

export function ensureNoteFolders(root) {
  const notesRoot = getNotesRoot(root)
  fs.mkdirSync(notesRoot, { recursive: true })
  for (const folder of NOTE_FOLDERS) {
    fs.mkdirSync(path.join(notesRoot, folder), { recursive: true })
  }
}

export function categoryFromRelPath(relPath) {
  const parts = relPath.replace(/\\/g, '/').split('/')
  if (parts.length <= 1) return '未分类'
  const folder = parts[0]
  if (folder === '_drafts') return '草稿'
  return folder
}

export function isDraftPath(relPath) {
  return relPath.replace(/\\/g, '/').startsWith('_drafts/')
}

export function sanitizeFileName(name) {
  return String(name)
    .trim()
    .replace(/[<>:"/\\|?*]/g, '-')
    .replace(/\s+/g, ' ')
}

export function buildMarkdownTemplate({ title, date, category, tags, excerpt, cover }) {
  const tagYaml = `[${tags.map((t) => JSON.stringify(t)).join(', ')}]`
  const lines = [
    '---',
    `title: ${JSON.stringify(title)}`,
    `date: ${date}`,
    `category: ${JSON.stringify(category)}`,
    `tags: ${tagYaml}`,
    `excerpt: ${JSON.stringify(excerpt)}`,
  ]
  if (cover) lines.push(`cover: ${JSON.stringify(cover)}`)
  lines.push('---', '', '## 开头', '', '在这里写正文…', '')
  return lines.join('\n')
}

export function serializeNote({ meta, body }) {
  const lines = ['---']
  const order = ['title', 'date', 'category', 'tags', 'excerpt', 'cover', 'file']
  const keys = [...new Set([...order, ...Object.keys(meta)])]

  for (const key of keys) {
    const value = meta[key]
    if (value === undefined || value === null || value === '') continue
    if (Array.isArray(value)) {
      lines.push(`${key}: [${value.map((v) => JSON.stringify(v)).join(', ')}]`)
    } else {
      lines.push(`${key}: ${JSON.stringify(String(value))}`)
    }
  }

  lines.push('---', '')
  const normalizedBody = String(body || '').replace(/^\n+/, '')
  return `${lines.join('\n')}${normalizedBody}`
}

/** 扫描 笔记/ 时跳过的目录（第三方插件、依赖等） */
const SKIP_NOTE_DIRS = new Set([
  'node_modules',
  '.git',
  'typora_plugin',
  'typora_plugin-master',
  'plugin',
  'plugins',
  '.vscode',
  '__pycache__',
  'dist',
  'vendor',
])

function shouldSkipNoteDir(name) {
  return name.startsWith('.') || SKIP_NOTE_DIRS.has(name)
}

function shouldSkipNoteFile(relPath) {
  const normalized = relPath.replace(/\\/g, '/')
  const base = path.basename(normalized).toLowerCase()
  if (base === 'readme.md') return true
  if (/typora_plugin/i.test(normalized)) return true
  if (/\/plugin\//i.test(normalized)) return true
  return false
}

function walkMarkdownFiles(dir, notesRoot, bucket = []) {
  if (!fs.existsSync(dir)) return bucket

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (shouldSkipNoteDir(entry.name)) continue
      walkMarkdownFiles(path.join(dir, entry.name), notesRoot, bucket)
      continue
    }

    if (!entry.name.endsWith('.md')) continue

    const absPath = path.join(dir, entry.name)
    const relPath = path.relative(notesRoot, absPath).replace(/\\/g, '/')
    if (shouldSkipNoteFile(relPath)) continue

    const stat = fs.statSync(absPath)
    bucket.push({ relPath, absPath, stat })
  }

  return bucket
}

export function listNotes(root, { category } = {}) {
  const notesRoot = getNotesRoot(root)
  ensureNoteFolders(root)

  const files = walkMarkdownFiles(notesRoot, notesRoot)
  const items = files.map(({ relPath, absPath, stat }) => {
    const raw = fs.readFileSync(absPath, 'utf8')
    const { meta, body } = parseFrontmatter(raw)
    return {
      relPath,
      folder: categoryFromRelPath(relPath),
      isDraft: isDraftPath(relPath),
      mtime: stat.mtimeMs,
      meta,
      bodyLength: body.length,
    }
  })

  const filtered = category && category !== '全部'
    ? items.filter((item) => {
        if (category === '草稿') return item.isDraft
        if (category === '未分类') return item.folder === '未分类'
        return item.folder === category
      })
    : items

  return filtered.sort((a, b) => b.mtime - a.mtime)
}

export function readNote(root, relPath) {
  const notesRoot = getNotesRoot(root)
  const absPath = path.join(notesRoot, relPath)
  if (!absPath.startsWith(notesRoot) || !fs.existsSync(absPath)) {
    throw new Error('笔记不存在')
  }

  const raw = fs.readFileSync(absPath, 'utf8')
  const { meta, body } = parseFrontmatter(raw)
  return { relPath, raw, meta, body }
}

export function writeNote(root, relPath, { meta, body }) {
  const notesRoot = getNotesRoot(root)
  const absPath = path.join(notesRoot, relPath)
  if (!absPath.startsWith(notesRoot)) throw new Error('非法路径')

  fs.mkdirSync(path.dirname(absPath), { recursive: true })
  fs.writeFileSync(absPath, serializeNote({ meta, body }), 'utf8')
  return { relPath, absPath }
}

export function createNote(root, { title, category, tags, excerpt, date, cover, asDraft = false }) {
  const safeTitle = sanitizeFileName(title)
  if (!safeTitle) throw new Error('标题不能为空')

  const folder = asDraft ? '_drafts' : category || '学习'
  const relPath = `${folder}/${safeTitle}.md`
  const notesRoot = getNotesRoot(root)
  const absPath = path.join(notesRoot, relPath)

  if (fs.existsSync(absPath)) throw new Error(`笔记已存在：${relPath}`)

  const tagList = Array.isArray(tags)
    ? tags
    : String(tags || category || '学习')
        .split(/[,，]/)
        .map((t) => t.trim())
        .filter(Boolean)

  const content = buildMarkdownTemplate({
    title: safeTitle,
    date: date || todayISO(),
    category: folder === '_drafts' ? category || '学习' : folder,
    tags: tagList.length ? tagList : [category || '学习'],
    excerpt: excerpt || `${safeTitle} — 学习笔记。`,
    cover,
  })

  fs.mkdirSync(path.dirname(absPath), { recursive: true })
  fs.writeFileSync(absPath, content, 'utf8')
  return { relPath, absPath }
}

function normalizeMatchKey(name) {
  return String(name)
    .replace(/\.(html|md)$/i, '')
    .replace(/\s+/g, '')
    .toLowerCase()
}

export function findPostsWithoutNotes(root, posts) {
  const notes = listNotes(root)
  const coveredKeys = new Set()

  for (const note of notes) {
    try {
      const noteData = readNote(root, note.relPath)
      const mdPath = path.join(getNotesRoot(root), note.relPath)
      const resolved = resolvePostMeta({
        meta: noteData.meta,
        body: noteData.body,
        mdPath,
        posts,
      })

      for (const value of [
        resolved.file,
        path.basename(note.relPath),
        noteData.meta.title,
        resolved.title,
        noteData.meta.file,
      ]) {
        if (value) coveredKeys.add(normalizeMatchKey(value))
      }
    } catch {
      /* skip broken notes */
    }
  }

  return posts
    .filter((post) => {
      const keys = [normalizeMatchKey(post.file), normalizeMatchKey(post.title)]
      return !keys.some((key) => coveredKeys.has(key))
    })
    .sort((a, b) => b.date.localeCompare(a.date))
}

export function getNotePublishStatus(root, relPath, posts) {
  const notesRoot = getNotesRoot(root)
  const absPath = path.join(notesRoot, relPath)
  const { meta, body } = parseFrontmatter(fs.readFileSync(absPath, 'utf8'))
  const preview = resolvePostMeta({ meta, body, mdPath: absPath, posts })
  const htmlPath = path.join(root, 'Content', preview.file)
  const published = posts.some((p) => p.file === preview.file)

  let status = 'draft'
  if (published) {
    status = 'published'
    if (fs.existsSync(htmlPath)) {
      const mdTime = fs.statSync(absPath).mtimeMs
      const htmlTime = fs.statSync(htmlPath).mtimeMs
      if (mdTime > htmlTime + 1000) status = 'modified'
    } else {
      status = 'modified'
    }
  } else if (isDraftPath(relPath)) {
    status = 'draft'
  }

  return {
    status,
    post: preview,
    postId: preview.id,
    htmlFile: preview.file,
  }
}

export function listSiteOnlyNotes(root, posts) {
  return findPostsWithoutNotes(root, posts).map((post) => ({
    relPath: `__site__/${post.file}`,
    folder: '站点文章',
    isDraft: false,
    title: post.title,
    date: post.date,
    category: post.category,
    tags: post.tags || [],
    excerpt: post.excerpt || '',
    mtime: 0,
    status: 'published',
    postId: post.id,
    htmlFile: post.file,
    siteOnly: true,
  }))
}

export function listCategories(root, posts = []) {
  ensureNoteFolders(root)
  const notes = listNotes(root)
  const siteOnlyNotes = posts.length ? listSiteOnlyNotes(root, posts) : []
  const siteOnlyCount = siteOnlyNotes.length
  const counts = new Map([
    ['全部', notes.length + siteOnlyCount],
    ['草稿', 0],
    ['未分类', 0],
    ['站点文章', siteOnlyCount],
  ])

  for (const cat of COMMON_CATEGORIES) counts.set(cat, 0)
  for (const note of notes) {
    if (note.isDraft) {
      counts.set('草稿', (counts.get('草稿') || 0) + 1)
      continue
    }
    const key = note.folder === '未分类' ? '未分类' : note.folder
    counts.set(key, (counts.get(key) || 0) + 1)
  }

  const dynamic = [...counts.keys()]
    .filter(
      (name) =>
        name !== '全部' &&
        name !== '草稿' &&
        name !== '未分类' &&
        name !== '站点文章' &&
        !COMMON_CATEGORIES.includes(name),
    )
    .sort((a, b) => a.localeCompare(b, 'zh-CN'))

  const order = ['全部', ...COMMON_CATEGORIES, ...dynamic, '站点文章', '草稿', '未分类']
  return order
    .filter((name) => counts.has(name))
    .map((name) => ({ name, count: counts.get(name) || 0 }))
    .filter(
      (item) =>
        item.name === '全部' ||
        item.name === '站点文章' ||
        item.count > 0 ||
        COMMON_CATEGORIES.includes(item.name),
    )
}

export function resolveNotePath(root, input) {
  const notesRoot = getNotesRoot(root)
  const candidates = [
    path.resolve(process.cwd(), input),
    path.join(notesRoot, input),
    path.join(notesRoot, `${input}.md`),
  ]

  for (const candidate of candidates) {
    if (fs.existsSync(candidate) && candidate.endsWith('.md')) {
      return {
        absPath: candidate,
        relPath: path.relative(notesRoot, candidate).replace(/\\/g, '/'),
      }
    }
  }

  const all = walkMarkdownFiles(notesRoot, notesRoot)
  const base = path.basename(input, '.md')
  const hit = all.find((item) => item.relPath === input || path.basename(item.relPath, '.md') === base)
  if (hit) return hit

  return null
}

export function categoryToFolder(categoryName) {
  if (categoryName === '草稿') return '_drafts'
  if (categoryName === '未分类') return ''
  if (categoryName === '全部') throw new Error('不能移动到「全部」')
  return categoryName
}

function assertNotePath(notesRoot, relPath) {
  const absPath = path.join(notesRoot, relPath)
  const normalizedRoot = path.resolve(notesRoot)
  const normalizedAbs = path.resolve(absPath)
  if (!normalizedAbs.startsWith(normalizedRoot)) throw new Error('非法路径')
  return absPath
}

export function moveNote(root, relPath, targetCategory) {
  const notesRoot = getNotesRoot(root)
  const folder = categoryToFolder(targetCategory)
  const normalized = relPath.replace(/\\/g, '/')
  const fileName = path.basename(normalized)
  const newRelPath = folder ? `${folder}/${fileName}` : fileName

  if (newRelPath === normalized) {
    return { relPath: newRelPath, moved: false }
  }

  const srcAbs = assertNotePath(notesRoot, normalized)
  const destAbs = path.join(notesRoot, newRelPath)

  if (!fs.existsSync(srcAbs)) throw new Error('笔记不存在')
  if (fs.existsSync(destAbs)) throw new Error(`目标已存在：${newRelPath}`)

  const note = readNote(root, normalized)
  const meta = { ...note.meta }
  if (folder && folder !== '_drafts') {
    meta.category = targetCategory
  }

  fs.mkdirSync(path.dirname(destAbs), { recursive: true })
  fs.writeFileSync(destAbs, serializeNote({ meta, body: note.body }), 'utf8')
  fs.unlinkSync(srcAbs)

  return { relPath: newRelPath, moved: true, folder: categoryFromRelPath(newRelPath) }
}

export function deleteNote(root, relPath, { unpublish = false, posts = [] } = {}) {
  const notesRoot = getNotesRoot(root)
  const normalized = relPath.replace(/\\/g, '/')
  const absPath = assertNotePath(notesRoot, normalized)

  if (!fs.existsSync(absPath)) throw new Error('笔记不存在')

  let removedPost = false
  let removedHtml = false
  let htmlFile = ''

  if (unpublish) {
    const raw = fs.readFileSync(absPath, 'utf8')
    const { meta, body } = parseFrontmatter(raw)
    const preview = resolvePostMeta({ meta, body, mdPath: absPath, posts })
    htmlFile = preview.file
    const postsPath = path.join(root, 'src/data/posts.js')
    removedPost = removePostEntryByFile(preview.file, postsPath)
    const htmlPath = path.join(root, 'Content', preview.file)
    if (fs.existsSync(htmlPath)) {
      fs.unlinkSync(htmlPath)
      removedHtml = true
    }
  }

  fs.unlinkSync(absPath)

  return { ok: true, removedPost, removedHtml, htmlFile }
}

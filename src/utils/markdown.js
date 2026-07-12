import { marked } from 'marked'
import DOMPurify from 'dompurify'
import TurndownService from 'turndown'
import { apiOrigin, resolveMediaUrl } from '../api/platform.js'

marked.setOptions({ breaks: true, gfm: true })

marked.use({
  renderer: {
    image({ href, title, text }) {
      const src = resolveMediaUrl(href || '')
      const alt = text || ''
      const titleAttr = title ? ` title="${title}"` : ''
      return `<img src="${src}" alt="${alt}"${titleAttr} loading="lazy" />`
    },
  },
})

const turndown = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
  bulletListMarker: '-',
})

turndown.addRule('strikethrough', {
  filter: ['del', 's', 'strike'],
  replacement(content) {
    return `~~${content}~~`
  },
})

turndown.addRule('uploadImage', {
  filter: 'img',
  replacement(_content, node) {
    const alt = node.getAttribute('alt') || 'image'
    let href = node.getAttribute('src') || ''
    const origin = apiOrigin().replace(/\/$/, '')
    if (origin && href.startsWith(origin)) {
      href = href.slice(origin.length)
    }
    return `![${alt}](${href})`
  },
})

/** Markdown → 安全 HTML */
export function renderMarkdown(text) {
  if (!text) return ''
  const raw = marked.parse(text, { async: false })
  return DOMPurify.sanitize(raw)
}

/** HTML → Markdown（富文本模式同步用） */
export function htmlToMarkdown(html) {
  if (!html) return ''
  return turndown.turndown(html).trim()
}

/** Markdown → HTML（富文本编辑区初始内容） */
export function markdownToHtml(text) {
  return renderMarkdown(text)
}

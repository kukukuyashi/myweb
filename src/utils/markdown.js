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

const ALLOWED_STYLE_PROPS = ['color', 'background-color', 'font-size']

export function sanitizeInlineStyle(raw) {
  if (!raw) return ''
  const out = []
  for (const part of String(raw).split(';')) {
    const idx = part.indexOf(':')
    if (idx === -1) continue
    const prop = part.slice(0, idx).trim().toLowerCase()
    const val = part.slice(idx + 1).trim()
    if (!ALLOWED_STYLE_PROPS.includes(prop)) continue
    if (/url\s*\(|expression|javascript:|@import/i.test(val)) continue
    out.push(prop + ': ' + val)
  }
  return out.join('; ')
}

turndown.addRule('inlineStyledSpan', {
  filter(node) {
    return node.nodeName === 'SPAN' && !!sanitizeInlineStyle(node.getAttribute('style'))
  },
  replacement(content, node) {
    const style = sanitizeInlineStyle(node.getAttribute('style'))
    if (!style || !content.trim()) return content
    return '<span style="' + style + '">' + content + '</span>'
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
  return DOMPurify.sanitize(raw, { ADD_ATTR: ['style'] })
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

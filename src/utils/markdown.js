import { marked } from 'marked'
import DOMPurify from 'dompurify'
import TurndownService from 'turndown'

marked.setOptions({ breaks: true, gfm: true })

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

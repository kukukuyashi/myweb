import Prism from 'prismjs'
import 'prismjs/components/prism-javascript'
import 'prismjs/components/prism-java'
import 'prismjs/components/prism-markup'
import 'prismjs/components/prism-css'
import 'prismjs/components/prism-json'
import 'prismjs/components/prism-bash'

const LANG_MAP = {
  js: 'javascript',
  jsx: 'javascript',
  ts: 'javascript',
  html: 'markup',
  xml: 'markup',
  sh: 'bash',
  shell: 'bash',
}

export function highlightArticle(root) {
  if (!root) return
  root.querySelectorAll('pre code').forEach(block => {
    const cls = Array.from(block.classList).find(c => c.startsWith('language-'))
    let lang = cls?.replace('language-', '') || ''
    if (!lang) {
      const parent = block.parentElement
      const parentCls = Array.from(parent?.classList || []).find(c => c.startsWith('language-'))
      lang = parentCls?.replace('language-', '') || 'javascript'
    }
    lang = LANG_MAP[lang] || lang
    block.classList.add(`language-${lang}`)
    Prism.highlightElement(block)
  })
}

export function estimateReadingMinutes(html) {
  const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, '')
  return Math.max(1, Math.ceil(text.length / 450))
}

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

function attachCopyButton(pre) {
  if (pre.querySelector('.code-copy-btn')) return
  const btn = document.createElement('button')
  btn.type = 'button'
  btn.className = 'code-copy-btn'
  btn.textContent = 'COPY'
  btn.setAttribute('aria-label', '复制代码')
  btn.addEventListener('click', async () => {
    const code = pre.querySelector('code')?.textContent || ''
    try {
      await navigator.clipboard.writeText(code)
      btn.textContent = 'OK'
      btn.classList.add('code-copy-btn--done')
      setTimeout(() => {
        btn.textContent = 'COPY'
        btn.classList.remove('code-copy-btn--done')
      }, 1600)
    } catch {
      btn.textContent = 'ERR'
      setTimeout(() => { btn.textContent = 'COPY' }, 1600)
    }
  })
  pre.style.position = 'relative'
  pre.appendChild(btn)
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
    const pre = block.closest('pre')
    if (pre) attachCopyButton(pre)
  })
}

export function estimateReadingMinutes(html) {
  const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, '')
  return Math.max(1, Math.ceil(text.length / 450))
}

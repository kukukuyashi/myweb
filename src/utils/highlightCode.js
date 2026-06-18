let Prism = null
let prismLoaded = false

async function loadPrism() {
  if (prismLoaded) return
  Prism = (await import('prismjs')).default
  await import('prismjs/components/prism-javascript')
  await import('prismjs/components/prism-java')
  await import('prismjs/components/prism-markup')
  await import('prismjs/components/prism-css')
  await import('prismjs/components/prism-json')
  await import('prismjs/components/prism-bash')
  await import('prismjs/themes/prism-tomorrow.css')
  prismLoaded = true
}

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

export async function highlightArticle(root) {
  if (!root) return
  await loadPrism()
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

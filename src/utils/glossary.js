import { fetchGlossaryPublic } from '../api/glossary'

let _cache = null
let _promise = null

/** 拉取全部术语（进程内缓存，避免每篇文章都请求）。 */
export async function loadGlossaryTerms() {
  if (_cache) return _cache
  if (_promise) return _promise
  _promise = fetchGlossaryPublic()
    .then((d) => { _cache = (d && d.terms) || []; return _cache })
    .catch(() => { _cache = []; return _cache })
  return _promise
}

export function clearGlossaryCache() {
  _cache = null
  _promise = null
}

function isAscii(s) {
  return /^[\x00-\x7F]+$/.test(s)
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function skipNode(node, root) {
  let p = node.parentElement
  while (p && p !== root) {
    const tag = p.tagName
    if (tag === 'PRE' || tag === 'CODE' || tag === 'A' || /^H[1-6]$/.test(tag)) return true
    if (p.classList && p.classList.contains('glossary-term')) return true
    p = p.parentElement
  }
  return false
}

function wrapFirst(root, entry) {
  const esc = escapeRegExp(entry.name)
  let re
  try {
    re = entry.ascii
      ? new RegExp('(?<![A-Za-z0-9_])' + esc + '(?![A-Za-z0-9_])', 'i')
      : new RegExp(esc)
  } catch {
    re = new RegExp(esc)
  }
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT
      return skipNode(node, root) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    },
  })
  let node
  while ((node = walker.nextNode())) {
    const m = re.exec(node.nodeValue)
    if (!m) continue
    const start = m.index
    const matchText = m[0]
    const after = node.splitText(start)
    after.splitText(matchText.length)
    const span = document.createElement('span')
    span.className = 'glossary-term'
    span.textContent = matchText
    span.setAttribute('data-def', entry.def)
    span.setAttribute('data-term', entry.term)
    span.setAttribute('tabindex', '0')
    after.parentNode.replaceChild(span, after)
    return true
  }
  return false
}

/** 在 root 内为已登记术语的首次出现加高亮（每术语每篇仅一次）。 */
export function annotateGlossary(root, terms) {
  if (!root || !terms || !terms.length) return
  const entries = []
  for (const t of terms) {
    const names = [t.term, ...String(t.aliases || '').split(/[,，]/)]
      .map((s) => s.trim())
      .filter(Boolean)
    for (const name of names) {
      entries.push({ name, def: t.definition, term: t.term, ascii: isAscii(name) })
    }
  }
  entries.sort((a, b) => b.name.length - a.name.length)
  const done = new Set()
  for (const e of entries) {
    if (done.has(e.term)) continue
    if (wrapFirst(root, e)) done.add(e.term)
  }
}

/** 悬停/点按显示释义的浮层；返回 teardown。 */
export function setupGlossaryTooltip(root) {
  if (!root) return () => {}
  const tip = document.createElement('div')
  tip.className = 'glossary-tooltip'
  tip.setAttribute('role', 'tooltip')
  tip.style.display = 'none'
  document.body.appendChild(tip)
  let hideTimer = null

  function render(el) {
    tip.innerHTML = ''
    const h = document.createElement('strong')
    h.className = 'gt-term'
    h.textContent = el.getAttribute('data-term') || ''
    const p = document.createElement('span')
    p.className = 'gt-def'
    p.textContent = el.getAttribute('data-def') || ''
    tip.appendChild(h)
    tip.appendChild(p)
  }
  function position(el) {
    const r = el.getBoundingClientRect()
    const tr = tip.getBoundingClientRect()
    const gap = 10
    // 浼樺厛鏄剧ず鍦ㄨ瘝鏉ｄ笂鏂癸紝閬垮厤鑷畾涔夊厜鏍囷紙浠庡厜鏍囧皹寮€濮嬪悜鍙充笅寤朵几锛夐伄浣忔诞灞?    const spaceAbove = r.top
    const spaceBelow = document.documentElement.clientHeight - r.bottom
    let top
    if (spaceAbove >= tr.height + gap || spaceAbove >= spaceBelow) {
      top = r.top + window.scrollY - tr.height - gap
    } else {
      top = r.bottom + window.scrollY + gap
    }
    if (top < window.scrollY + 8) top = window.scrollY + 8
    let left = r.left + window.scrollX
    const maxLeft = window.scrollX + document.documentElement.clientWidth - tr.width - 12
    if (left > maxLeft) left = Math.max(window.scrollX + 8, maxLeft)
    if (left < window.scrollX + 8) left = window.scrollX + 8
    tip.style.top = top + 'px'
    tip.style.left = left + 'px'
  }
  function show(el) {
    if (!el.getAttribute('data-def')) return
    render(el)
    tip.style.display = 'block'
    position(el)
  }
  function hide() { tip.style.display = 'none' }

  function onOver(e) {
    const el = e.target.closest && e.target.closest('.glossary-term')
    if (!el || !root.contains(el)) return
    clearTimeout(hideTimer)
    show(el)
  }
  function onOut(e) {
    const el = e.target.closest && e.target.closest('.glossary-term')
    if (!el) return
    hideTimer = setTimeout(hide, 150)
  }
  function onClick(e) {
    const el = e.target.closest && e.target.closest('.glossary-term')
    if (!el || !root.contains(el)) { hide(); return }
    if (tip.style.display === 'block') hide()
    else show(el)
  }
  function onFocus(e) {
    const el = e.target.closest && e.target.closest('.glossary-term')
    if (el && root.contains(el)) show(el)
  }

  root.addEventListener('mouseover', onOver)
  root.addEventListener('mouseout', onOut)
  root.addEventListener('click', onClick)
  root.addEventListener('focusin', onFocus)
  tip.addEventListener('mouseenter', () => clearTimeout(hideTimer))
  tip.addEventListener('mouseleave', hide)
  window.addEventListener('scroll', hide, { passive: true })

  return function teardown() {
    root.removeEventListener('mouseover', onOver)
    root.removeEventListener('mouseout', onOut)
    root.removeEventListener('click', onClick)
    root.removeEventListener('focusin', onFocus)
    window.removeEventListener('scroll', hide)
    tip.remove()
  }
}
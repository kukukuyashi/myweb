import { onMounted, onUnmounted } from 'vue'

const HOTSPOT_X = 8
const HOTSPOT_Y = 8
const CURSOR_SIZE = 64

const POINTER_SELECTOR = [
  'a',
  'button',
  '[role="button"]',
  '.router-link-active',
  '.router-link-exact-active',
  '.topbar-nav a',
  '.filter-btn',
  '.search-btn',
  '.code-copy-link',
  '.tag-link',
  '.featured-read',
  '.post-card-read',
  '.archive-title',
  '.nav-prev',
  '.nav-next',
].join(', ')

const TEXT_SELECTOR = 'input, textarea, select, [contenteditable="true"]'
const DISABLED_SELECTOR = '[disabled], .not-allowed'

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

function hasFinePointer() {
  return window.matchMedia('(pointer: fine)').matches
}

function cursorSrc(name) {
  const base = import.meta.env.BASE_URL || '/'
  return `${base}cursors/${name}.gif`
}

const CURSORS = {
  normal: cursorSrc('normal'),
  pointer: cursorSrc('pointer'),
  text: cursorSrc('text'),
  busy: cursorSrc('busy'),
}

function resolveCursorType(target) {
  if (document.documentElement.classList.contains('cursor-busy')) {
    return 'busy'
  }
  if (!target || target === document.documentElement || target === document.body) {
    return 'normal'
  }
  if (target.closest?.(DISABLED_SELECTOR)) {
    return 'disabled'
  }
  if (target.closest?.(TEXT_SELECTOR)) {
    return 'text'
  }
  if (target.closest?.(POINTER_SELECTOR)) {
    return 'pointer'
  }
  return 'normal'
}

/**
 * 用跟随鼠标的 GIF 图层实现动态光标。
 * Chrome 对 CSS cursor:url() 的 GIF 只显示第一帧，img 叠加层可正常播放动画。
 */
export function useAnimatedCursor() {
  let el = null
  let visible = true
  let currentType = ''
  let rafId = 0
  let pendingX = 0
  let pendingY = 0
  let observer = null

  function setPosition(x, y) {
    if (!el) return
    el.style.transform = `translate(${x - HOTSPOT_X}px, ${y - HOTSPOT_Y}px)`
  }

  function applyType(type) {
    if (!el || type === currentType) return

    currentType = type

    if (type === 'disabled') {
      el.style.visibility = 'hidden'
      return
    }

    el.style.visibility = visible ? 'visible' : 'hidden'
    el.src = CURSORS[type] || CURSORS.normal
  }

  function flushMove() {
    rafId = 0
    const target = document.elementFromPoint(pendingX, pendingY)
    const type = resolveCursorType(target)
    applyType(type)
    if (type !== 'disabled') {
      setPosition(pendingX, pendingY)
    }
  }

  function onMove(e) {
    pendingX = e.clientX
    pendingY = e.clientY
    if (!rafId) {
      rafId = requestAnimationFrame(flushMove)
    }
  }

  function onMouseOut(e) {
    if (e.relatedTarget == null) {
      visible = false
      if (el) el.style.visibility = 'hidden'
    }
  }

  function onMouseOver() {
    visible = true
    if (el && currentType !== 'disabled') {
      el.style.visibility = 'visible'
    }
  }

  onMounted(() => {
    if (prefersReducedMotion() || !hasFinePointer()) return

    el = document.createElement('img')
    el.className = 'animated-cursor'
    el.src = CURSORS.normal
    el.width = CURSOR_SIZE
    el.height = CURSOR_SIZE
    el.alt = ''
    el.draggable = false
    el.setAttribute('aria-hidden', 'true')
    document.body.appendChild(el)

    document.documentElement.classList.add('has-animated-cursor')
    currentType = 'normal'

    document.addEventListener('mousemove', onMove, { passive: true })
    document.addEventListener('mouseout', onMouseOut)
    document.addEventListener('mouseover', onMouseOver)

    observer = new MutationObserver(() => {
      if (rafId) cancelAnimationFrame(rafId)
      rafId = requestAnimationFrame(flushMove)
    })
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    })
  })

  onUnmounted(() => {
    if (!el) return

    document.documentElement.classList.remove('has-animated-cursor')
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseout', onMouseOut)
    document.removeEventListener('mouseover', onMouseOver)
    observer?.disconnect()
    if (rafId) cancelAnimationFrame(rafId)
    el.remove()
    el = null
  })
}

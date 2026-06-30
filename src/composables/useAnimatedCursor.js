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

const CURSOR_NAMES = ['normal', 'pointer', 'text', 'busy']

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
 * Canvas 叠加层播放 GIF 光标：每帧 clearRect 再 drawImage，避免 img+transform 拖影；
 * Chrome 对 CSS cursor:url() 的 GIF 只显示第一帧。
 */
export function useAnimatedCursor() {
  let canvas = null
  let ctx = null
  /** @type {Record<string, HTMLImageElement>} */
  const sources = {}
  let visible = true
  let currentType = 'normal'
  let paintRaf = 0
  let moveRaf = 0
  let pendingX = 0
  let pendingY = 0
  let observer = null

  function activeSource() {
    return sources[currentType] || sources.normal
  }

  function setPosition(x, y) {
    if (!canvas) return
    canvas.style.left = `${x - HOTSPOT_X}px`
    canvas.style.top = `${y - HOTSPOT_Y}px`
  }

  function paintLoop() {
    paintRaf = requestAnimationFrame(paintLoop)
    if (!ctx || !visible || currentType === 'disabled') return

    const img = activeSource()
    ctx.clearRect(0, 0, CURSOR_SIZE, CURSOR_SIZE)
    if (img?.complete && img.naturalWidth > 0) {
      ctx.drawImage(img, 0, 0, CURSOR_SIZE, CURSOR_SIZE)
    }
  }

  function applyType(type) {
    if (type === currentType) return
    currentType = type

    if (!canvas) return

    if (type === 'disabled') {
      canvas.style.visibility = 'hidden'
      ctx?.clearRect(0, 0, CURSOR_SIZE, CURSOR_SIZE)
      return
    }

    canvas.style.visibility = visible ? 'visible' : 'hidden'
  }

  function flushMove() {
    moveRaf = 0
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
    if (!moveRaf) {
      moveRaf = requestAnimationFrame(flushMove)
    }
  }

  function onMouseOut(e) {
    if (e.relatedTarget == null) {
      visible = false
      if (canvas) {
        canvas.style.visibility = 'hidden'
        ctx?.clearRect(0, 0, CURSOR_SIZE, CURSOR_SIZE)
      }
    }
  }

  function onMouseOver() {
    visible = true
    if (canvas && currentType !== 'disabled') {
      canvas.style.visibility = 'visible'
    }
  }

  onMounted(() => {
    if (prefersReducedMotion() || !hasFinePointer()) return

    canvas = document.createElement('canvas')
    canvas.className = 'animated-cursor'
    canvas.width = CURSOR_SIZE
    canvas.height = CURSOR_SIZE
    canvas.setAttribute('aria-hidden', 'true')
    ctx = canvas.getContext('2d', { alpha: true })
    document.body.appendChild(canvas)

    for (const name of CURSOR_NAMES) {
      const img = new Image()
      img.src = cursorSrc(name)
      img.decoding = 'async'
      sources[name] = img
    }

    document.documentElement.classList.add('has-animated-cursor')
    paintRaf = requestAnimationFrame(paintLoop)

    document.addEventListener('mousemove', onMove, { passive: true })
    document.addEventListener('mouseout', onMouseOut)
    document.addEventListener('mouseover', onMouseOver)

    observer = new MutationObserver(() => {
      if (moveRaf) cancelAnimationFrame(moveRaf)
      moveRaf = requestAnimationFrame(flushMove)
    })
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    })
  })

  onUnmounted(() => {
    if (!canvas) return

    document.documentElement.classList.remove('has-animated-cursor')
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseout', onMouseOut)
    document.removeEventListener('mouseover', onMouseOver)
    observer?.disconnect()
    if (paintRaf) cancelAnimationFrame(paintRaf)
    if (moveRaf) cancelAnimationFrame(moveRaf)
    canvas.remove()
    canvas = null
    ctx = null
  })
}

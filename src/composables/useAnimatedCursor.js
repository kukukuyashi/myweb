import { onMounted, onUnmounted } from 'vue'

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
 * Canvas + PNG 精灵图逐帧播放光标动画。
 * GIF 不能直接 drawImage 动画；img+transform 会拖影；精灵图可两者兼得。
 */
export function useAnimatedCursor() {
  let canvas = null
  let ctx = null
  let size = 96
  let hotspotX = 12
  let hotspotY = 12
  let frameMs = 33
  /** @type {Record<string, { sheet: HTMLImageElement, frames: number }>} */
  const assets = {}
  let visible = true
  let currentType = 'normal'
  let frameIndex = 0
  let lastFrameTime = 0
  let loopRaf = 0
  let pendingX = 0
  let pendingY = 0
  let observer = null

  function setPosition(x, y) {
    if (!canvas) return
    canvas.style.left = `${x - hotspotX}px`
    canvas.style.top = `${y - hotspotY}px`
  }

  function drawFrame() {
    if (!ctx || !visible || currentType === 'disabled') return

    const asset = assets[currentType] || assets.normal
    if (!asset?.sheet.complete || asset.sheet.naturalWidth <= 0) return

    ctx.clearRect(0, 0, size, size)
    ctx.drawImage(
      asset.sheet,
      frameIndex * size,
      0,
      size,
      size,
      0,
      0,
      size,
      size,
    )
  }

  function loop(now) {
    loopRaf = requestAnimationFrame(loop)

    const asset = assets[currentType] || assets.normal
    if (asset && now - lastFrameTime >= frameMs) {
      frameIndex = (frameIndex + 1) % asset.frames
      lastFrameTime = now
    }

    drawFrame()
  }

  function applyType(type) {
    if (type === currentType) return
    currentType = type
    frameIndex = 0
    lastFrameTime = performance.now()

    if (!canvas) return

    if (type === 'disabled') {
      canvas.style.visibility = 'hidden'
      ctx?.clearRect(0, 0, size, size)
      return
    }

    canvas.style.visibility = visible ? 'visible' : 'hidden'
    drawFrame()
  }

  function onMove(e) {
    pendingX = e.clientX
    pendingY = e.clientY
    const target = document.elementFromPoint(pendingX, pendingY)
    const type = resolveCursorType(target)
    applyType(type)
    if (type !== 'disabled') {
      setPosition(pendingX, pendingY)
    }
  }

  function onMouseOut(e) {
    if (e.relatedTarget == null) {
      visible = false
      if (canvas) {
        canvas.style.visibility = 'hidden'
        ctx?.clearRect(0, 0, size, size)
      }
    }
  }

  function onMouseOver() {
    visible = true
    if (canvas && currentType !== 'disabled') {
      canvas.style.visibility = 'visible'
      drawFrame()
    }
  }

  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.decoding = 'async'
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = src
    })
  }

  onMounted(async () => {
    if (prefersReducedMotion() || !hasFinePointer()) return

    const base = `${import.meta.env.BASE_URL || '/'}cursors/`

    try {
      const res = await fetch(`${base}manifest.json`)
      if (!res.ok) throw new Error('manifest missing')
      const manifest = await res.json()
      size = manifest.size || 96
      hotspotX = manifest.hotspotX ?? 12
      hotspotY = manifest.hotspotY ?? 12
      frameMs = manifest.frameMs || 33

      await Promise.all(
        Object.entries(manifest.cursors).map(async ([id, info]) => {
          assets[id] = {
            sheet: await loadImage(`${base}${info.sheet}`),
            frames: info.frames,
          }
        }),
      )
    } catch {
      return
    }

    canvas = document.createElement('canvas')
    canvas.className = 'animated-cursor'
    canvas.width = size
    canvas.height = size
    canvas.style.width = `${size}px`
    canvas.style.height = `${size}px`
    canvas.setAttribute('aria-hidden', 'true')
    ctx = canvas.getContext('2d', { alpha: true })
    document.body.appendChild(canvas)

    document.documentElement.classList.add('has-animated-cursor')
    currentType = 'normal'
    lastFrameTime = performance.now()
    loopRaf = requestAnimationFrame(loop)

    document.addEventListener('mousemove', onMove, { passive: true })
    document.addEventListener('mouseout', onMouseOut)
    document.addEventListener('mouseover', onMouseOver)

    observer = new MutationObserver(() => {
      const target = document.elementFromPoint(pendingX, pendingY)
      applyType(resolveCursorType(target))
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
    if (loopRaf) cancelAnimationFrame(loopRaf)
    canvas.remove()
    canvas = null
    ctx = null
  })
}

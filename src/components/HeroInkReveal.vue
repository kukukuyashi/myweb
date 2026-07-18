<template>
  <div ref="rootRef" class="ink-reveal-layers" aria-hidden="true">
    <div class="ink-reveal__bg" :style="bgStyle">
      <div class="ink-reveal__fade" :class="`ink-reveal__fade--${fadeDirection}`" />
    </div>
    <canvas ref="canvasRef" class="ink-reveal__mask" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { imgUrl } from '../data/profile'

const props = defineProps({
  image: { type: String, required: true },
  position: { type: String, default: 'center right' },
  rEnd: { type: Number, default: 118 },
  maxStamps: { type: Number, default: 130 },
  /** left | right — 文字保护渐变方向 */
  fadeDirection: { type: String, default: 'left' },
  /**
   * 遮罩不透明度：1 = 未扫过完全盖住；0.5 = 未扫过半透明看得见图案
   * 鼠标墨染镂空后仍显示底层原图
   */
  maskOpacity: { type: Number, default: 1 },
  /** 墨迹是否保留（登录/注册：扫过即为原图） */
  persistReveal: { type: Boolean, default: false },
})

const rootRef = ref(null)
const canvasRef = ref(null)
const bgReady = ref(false)

const bgStyle = computed(() => ({
  // 加引号，避免路径含空格/括号时 CSS url() 解析失败
  backgroundImage: bgReady.value ? `url("${imgUrl(props.image)}")` : 'none',
  backgroundPosition: props.position,
}))

let cleanup = null

onMounted(() => {
  const root = rootRef.value?.parentElement
  const canvas = canvasRef.value
  if (!root || !canvas) return

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        if (!entries[0]?.isIntersecting) return
        bgReady.value = true
        io.disconnect()
      },
      { rootMargin: '80px' },
    )
    io.observe(root)
  } else {
    bgReady.value = true
  }

  cleanup = initInkMask(root, canvas, {
    rEnd: props.rEnd,
    maxStamps: props.maxStamps,
    maskOpacity: props.maskOpacity,
    persistReveal: props.persistReveal,
  })
})

onUnmounted(() => {
  cleanup?.()
})

function parseCssColor(input) {
  const raw = (input || '').trim()
  if (!raw) return { r: 245, g: 242, b: 238 }
  if (raw.startsWith('#')) {
    const hex = raw.slice(1)
    const full =
      hex.length === 3
        ? hex
            .split('')
            .map((c) => c + c)
            .join('')
        : hex
    const n = Number.parseInt(full.slice(0, 6), 16)
    if (Number.isNaN(n)) return { r: 245, g: 242, b: 238 }
    return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 }
  }
  const m = raw.match(/rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)/i)
  if (m) {
    return { r: Number(m[1]), g: Number(m[2]), b: Number(m[3]) }
  }
  return { r: 245, g: 242, b: 238 }
}

function initInkMask(hero, canvas, { rEnd, maxStamps, maskOpacity = 1, persistReveal = false }) {
  const canHover = window.matchMedia('(hover: hover)').matches
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (!canHover || reduceMotion) return () => {}

  const ctx = canvas.getContext('2d')
  if (!ctx) return () => {}

  const R_START = 6
  const R_END = rEnd
  const R_VARY = 0.48
  const LIFETIME = persistReveal ? 420 : 560
  const STAMP_STEP = 8
  const MAX_STAMPS = maxStamps
  const DPR = Math.min(window.devicePixelRatio || 1, 2)
  const coverAlpha = Math.min(1, Math.max(0, maskOpacity))

  let w = 0
  let h = 0
  let running = false
  let rafId = 0
  const stamps = []
  let lastX = null
  let lastY = null

  function maskColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--bg-paper').trim() || '#f5f2ee'
  }

  function maskFillStyle() {
    if (coverAlpha >= 0.999) return maskColor()
    const { r, g, b } = parseCssColor(maskColor())
    return `rgba(${r}, ${g}, ${b}, ${coverAlpha})`
  }

  function paintBaseMask() {
    ctx.globalCompositeOperation = 'source-over'
    if (coverAlpha < 0.999) ctx.clearRect(0, 0, w, h)
    ctx.fillStyle = maskFillStyle()
    ctx.fillRect(0, 0, w, h)
  }

  function resize() {
    const rect = hero.getBoundingClientRect()
    w = rect.width
    h = rect.height
    canvas.width = Math.round(w * DPR)
    canvas.height = Math.round(h * DPR)
    canvas.style.width = w + 'px'
    canvas.style.height = h + 'px'
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0)
    paintBaseMask()
    if (stamps.length) start()
  }

  function addStamp(x, y) {
    if (stamps.length >= MAX_STAMPS) stamps.shift()
    stamps.push({
      x, y,
      born: performance.now(),
      seed: Math.random() * Math.PI * 2,
      rmax: R_END * (1 - R_VARY + Math.random() * R_VARY),
    })
  }

  function stampAlong(x, y) {
    if (lastX === null) {
      addStamp(x, y)
    } else {
      const dx = x - lastX
      const dy = y - lastY
      const dist = Math.hypot(dx, dy)
      const steps = Math.max(1, Math.ceil(dist / STAMP_STEP))
      for (let i = 1; i <= steps; i++) {
        addStamp(lastX + (dx * i) / steps, lastY + (dy * i) / steps)
      }
    }
    lastX = x
    lastY = y
  }

  function carveInk(x, y, r, alpha, seed) {
    const g = ctx.createRadialGradient(x, y, r * 0.22, x, y, r)
    g.addColorStop(0, `rgba(0, 0, 0, ${0.96 * alpha})`)
    g.addColorStop(0.5, `rgba(0, 0, 0, ${0.9 * alpha})`)
    g.addColorStop(1, 'rgba(0, 0, 0, 0)')
    ctx.fillStyle = g
    ctx.beginPath()
    const segs = 32
    for (let i = 0; i <= segs; i++) {
      const a = (i / segs) * Math.PI * 2
      const wob =
        0.76 +
        0.15 * Math.sin(a * 3 + seed) +
        0.08 * Math.sin(a * 7 + seed * 2.1) +
        0.06 * Math.sin(a * 11 + seed * 0.7)
      const rr = r * wob
      const px = x + Math.cos(a) * rr
      const py = y + Math.sin(a) * rr
      if (i === 0) ctx.moveTo(px, py)
      else ctx.lineTo(px, py)
    }
    ctx.closePath()
    ctx.fill()
  }

  function loop() {
    const now = performance.now()
    paintBaseMask()

    ctx.globalCompositeOperation = 'destination-out'
    let animating = false
    for (let i = stamps.length - 1; i >= 0; i--) {
      const t = (now - stamps[i].born) / LIFETIME
      if (!persistReveal && t >= 1) {
        stamps.splice(i, 1)
        continue
      }
      const tt = Math.min(1, Math.max(0, t))
      if (persistReveal && tt < 1) animating = true
      if (!persistReveal) animating = true
      const ease = 1 - Math.pow(1 - tt, 3)
      const r = R_START + (stamps[i].rmax - R_START) * ease
      const alpha = persistReveal ? 1 : 1 - tt * tt
      carveInk(stamps[i].x, stamps[i].y, r, alpha, stamps[i].seed)
    }

    if (stamps.length && (!persistReveal || animating)) {
      rafId = requestAnimationFrame(loop)
    } else {
      running = false
      // 持久墨迹：停帧前再画一次定格
      if (persistReveal && stamps.length) {
        paintBaseMask()
        ctx.globalCompositeOperation = 'destination-out'
        for (const s of stamps) {
          carveInk(s.x, s.y, s.rmax, 1, s.seed)
        }
      }
    }
  }

  function start() {
    if (!running) {
      running = true
      rafId = requestAnimationFrame(loop)
    }
  }

  function localPos(e) {
    const rect = hero.getBoundingClientRect()
    return { x: e.clientX - rect.left, y: e.clientY - rect.top }
  }

  function onEnter(e) {
    const { x, y } = localPos(e)
    lastX = x
    lastY = y
    stampAlong(x, y)
    start()
  }

  function onMove(e) {
    const { x, y } = localPos(e)
    stampAlong(x, y)
    start()
  }

  function onLeave() {
    lastX = null
    lastY = null
  }

  const ro = new ResizeObserver(resize)
  ro.observe(hero)
  resize()

  const themeObs = new MutationObserver(() => {
    resize()
  })
  themeObs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

  hero.addEventListener('mouseenter', onEnter)
  hero.addEventListener('mousemove', onMove)
  hero.addEventListener('mouseleave', onLeave)
  window.addEventListener('resize', resize)

  return () => {
    cancelAnimationFrame(rafId)
    ro.disconnect()
    themeObs.disconnect()
    hero.removeEventListener('mouseenter', onEnter)
    hero.removeEventListener('mousemove', onMove)
    hero.removeEventListener('mouseleave', onLeave)
    window.removeEventListener('resize', resize)
  }
}
</script>

<style scoped>
.ink-reveal-layers {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.ink-reveal__bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-repeat: no-repeat;
  filter: saturate(0.88) contrast(1.05);
}

.ink-reveal__fade {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.ink-reveal__fade--left {
  background: linear-gradient(
    105deg,
    var(--bg-paper) 0%,
    color-mix(in srgb, var(--bg-paper) 90%, transparent) 35%,
    color-mix(in srgb, var(--bg-paper) 35%, transparent) 65%,
    transparent 92%
  );
}

.ink-reveal__fade--right {
  background: linear-gradient(
    255deg,
    var(--bg-paper) 0%,
    color-mix(in srgb, var(--bg-paper) 90%, transparent) 35%,
    color-mix(in srgb, var(--bg-paper) 35%, transparent) 65%,
    transparent 92%
  );
}

.ink-reveal__mask {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
}

@media (prefers-reduced-motion: reduce) {
  .ink-reveal__mask {
    display: none;
  }

  .ink-reveal__bg {
    opacity: 0.45;
  }
}

@media (hover: none) {
  .ink-reveal__mask {
    display: none;
  }

  .ink-reveal__bg {
    opacity: 0.4;
  }

  .ink-reveal__fade--left {
    background: linear-gradient(
      105deg,
      var(--bg-paper) 0%,
      color-mix(in srgb, var(--bg-paper) 72%, transparent) 50%,
      transparent 100%
    );
  }

  .ink-reveal__fade--right {
    background: linear-gradient(
      255deg,
      var(--bg-paper) 0%,
      color-mix(in srgb, var(--bg-paper) 72%, transparent) 50%,
      transparent 100%
    );
  }
}

[data-theme="dark"] .ink-reveal__bg {
  opacity: 0.55;
}

[data-theme="dark"] .ink-reveal__fade--left {
  background: linear-gradient(
    105deg,
    var(--bg-paper) 0%,
    color-mix(in srgb, var(--bg-paper) 96%, transparent) 28%,
    color-mix(in srgb, var(--bg-paper) 55%, transparent) 58%,
    transparent 86%
  );
}

[data-theme="dark"] .ink-reveal__fade--right {
  background: linear-gradient(
    255deg,
    var(--bg-paper) 0%,
    color-mix(in srgb, var(--bg-paper) 96%, transparent) 28%,
    color-mix(in srgb, var(--bg-paper) 55%, transparent) 58%,
    transparent 86%
  );
}

@media (prefers-reduced-motion: reduce) {
  [data-theme="dark"] .ink-reveal__bg {
    opacity: 0.48;
  }
}
</style>

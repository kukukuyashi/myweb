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
})

const rootRef = ref(null)
const canvasRef = ref(null)

const bgStyle = computed(() => ({
  backgroundImage: `url(${imgUrl(props.image)})`,
  backgroundPosition: props.position,
}))

let cleanup = null

onMounted(() => {
  const root = rootRef.value?.parentElement
  const canvas = canvasRef.value
  if (!root || !canvas) return

  cleanup = initInkMask(root, canvas, {
    rEnd: props.rEnd,
    maxStamps: props.maxStamps,
  })
})

onUnmounted(() => {
  cleanup?.()
})

function initInkMask(hero, canvas, { rEnd, maxStamps }) {
  const canHover = window.matchMedia('(hover: hover)').matches
  if (!canHover) return () => {}

  const ctx = canvas.getContext('2d')
  if (!ctx) return () => {}

  const R_START = 6
  const R_END = rEnd
  const R_VARY = 0.48
  const LIFETIME = 560
  const STAMP_STEP = 8
  const MAX_STAMPS = maxStamps
  const DPR = Math.min(window.devicePixelRatio || 1, 2)

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

  function resize() {
    const rect = hero.getBoundingClientRect()
    w = rect.width
    h = rect.height
    canvas.width = Math.round(w * DPR)
    canvas.height = Math.round(h * DPR)
    canvas.style.width = w + 'px'
    canvas.style.height = h + 'px'
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0)
    ctx.globalCompositeOperation = 'source-over'
    ctx.fillStyle = maskColor()
    ctx.fillRect(0, 0, w, h)
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
    ctx.globalCompositeOperation = 'source-over'
    ctx.fillStyle = maskColor()
    ctx.fillRect(0, 0, w, h)

    ctx.globalCompositeOperation = 'destination-out'
    for (let i = stamps.length - 1; i >= 0; i--) {
      const t = (now - stamps[i].born) / LIFETIME
      if (t >= 1) {
        stamps.splice(i, 1)
        continue
      }
      const ease = 1 - Math.pow(1 - t, 3)
      const r = R_START + (stamps[i].rmax - R_START) * ease
      const alpha = 1 - t * t
      carveInk(stamps[i].x, stamps[i].y, r, alpha, stamps[i].seed)
    }

    if (stamps.length) {
      rafId = requestAnimationFrame(loop)
    } else {
      running = false
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
    if (!stamps.length) resize()
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
</style>

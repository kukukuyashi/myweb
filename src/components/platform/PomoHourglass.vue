<template>
  <div
    class="pomo-hourglass"
    :class="{ 'pomo-hourglass--running': running, 'pomo-hourglass--low': remainingRatio < 0.15 }"
    :style="{ '--hg-accent': accent }"
  >
    <div class="pomo-hourglass__frame">
      <canvas ref="canvasRef" class="pomo-hourglass__canvas" aria-hidden="true" />

      <svg class="pomo-hourglass__svg" viewBox="0 0 200 320" aria-hidden="true">
        <defs>
          <linearGradient id="hg-glass-shine" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="rgba(255,255,255,0.22)" />
            <stop offset="45%" stop-color="rgba(255,255,255,0.04)" />
            <stop offset="100%" stop-color="rgba(255,255,255,0.12)" />
          </linearGradient>
        </defs>
        <path
          class="pomo-hourglass__glass-outer"
          d="M50 10 H150 L118 154 V166 L150 310 H50 L82 166 V154 Z"
        />
        <path
          class="pomo-hourglass__glass-inner"
          d="M54 16 H146 L114 152 V168 L146 304 H54 L86 168 V152 Z"
        />
        <path class="pomo-hourglass__shine" d="M62 24 L78 24 L92 148 L86 148 Z" fill="url(#hg-glass-shine)" opacity="0.5" />
        <ellipse cx="100" cy="160" rx="14" ry="3" class="pomo-hourglass__neck-glow" />
      </svg>

      <div class="pomo-hourglass__time">{{ displayTime }}</div>
    </div>

    <p v-if="subText" class="pomo-hourglass__sub">{{ subText }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  displayTime: { type: String, required: true },
  remainingRatio: { type: Number, default: 1 },
  running: { type: Boolean, default: false },
  accent: { type: String, default: 'var(--orange)' },
  subText: { type: String, default: '' },
})

const canvasRef = ref(null)
const cssAccent = computed(() => resolveAccent(props.accent))

/** 平滑沙位（每帧逼近真实比例，避免粒子与沙堆脱节） */
let displayRatio = 1
let rafId = 0
let lastSpawn = 0
let particles = []
let settled = []

const GEOM = {
  topY: 18 / 320,
  neckTop: 152 / 320,
  neckBot: 168 / 320,
  bottomY: 302 / 320,
  topL: 58 / 200,
  topR: 142 / 200,
  neckL: 88 / 200,
  neckR: 112 / 200,
  botL: 58 / 200,
  botR: 142 / 200,
}

function resolveAccent(raw) {
  if (!raw || raw.startsWith('var(')) return '#e85d04'
  return raw
}

function parseHex(hex) {
  const h = hex.replace('#', '')
  if (h.length !== 6) return null
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  }
}

function tint(hex, amount) {
  const rgb = parseHex(hex)
  if (!rgb) return hex
  const mix = (c) => Math.round(c + (255 - c) * amount)
  return `rgb(${mix(rgb.r)}, ${mix(rgb.g)}, ${mix(rgb.b)})`
}

function shade(hex, amount) {
  const rgb = parseHex(hex)
  if (!rgb) return hex
  const mix = (c) => Math.round(c * (1 - amount))
  return `rgb(${mix(rgb.r)}, ${mix(rgb.g)}, ${mix(rgb.b)})`
}

function lerp(a, b, t) {
  return a + (b - a) * t
}

function lerpX(yNorm, y0, y1, x0, x1, y) {
  const t = (y - y0) / (y1 - y0)
  return lerp(x0, x1, t)
}

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1
  canvas.width = Math.floor(rect.width * dpr)
  canvas.height = Math.floor(rect.height * dpr)
  const ctx = canvas.getContext('2d')
  if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
}

function drawSandChamber(ctx, w, h, ratio, which) {
  const accent = cssAccent.value
  const isTop = which === 'top'
  const yStart = isTop ? h * GEOM.topY : h * GEOM.neckBot
  const yEnd = isTop ? h * GEOM.neckTop : h * GEOM.bottomY
  const chamberH = yEnd - yStart
  const fillRatio = isTop ? ratio : (1 - ratio)
  const fillH = chamberH * fillRatio
  if (fillH <= 0.5) return

  const surfaceY = isTop ? yEnd - fillH : yEnd - fillH
  const baseY = isTop ? yEnd : yEnd

  const steps = Math.max(6, Math.floor(fillH / 3))
  for (let i = 0; i < steps; i += 1) {
    const sliceY0 = baseY - fillH + (i / steps) * fillH
    const sliceY1 = baseY - fillH + ((i + 1) / steps) * fillH
    const yMid = (sliceY0 + sliceY1) / 2
    const yMidNorm = yMid / h

    let left, right
    if (isTop) {
      left = w * lerpX(yMidNorm, GEOM.topY, GEOM.neckTop, GEOM.topL, GEOM.neckL, yMidNorm)
      right = w * lerpX(yMidNorm, GEOM.topY, GEOM.neckTop, GEOM.topR, GEOM.neckR, yMidNorm)
    } else {
      left = w * lerpX(yMidNorm, GEOM.neckBot, GEOM.bottomY, GEOM.neckL, GEOM.botL, yMidNorm)
      right = w * lerpX(yMidNorm, GEOM.neckBot, GEOM.bottomY, GEOM.neckR, GEOM.botR, yMidNorm)
    }

    const depth = i / steps
    ctx.fillStyle = depth > 0.65 ? shade(accent, 0.08) : tint(accent, depth * 0.18)
    ctx.globalAlpha = 0.92
    ctx.beginPath()
    ctx.moveTo(left, sliceY0)
    ctx.lineTo(right, sliceY0)
    ctx.lineTo(right, sliceY1)
    ctx.lineTo(left, sliceY1)
    ctx.closePath()
    ctx.fill()
  }
  ctx.globalAlpha = 1

  // 沙面高光
  const surfNorm = surfaceY / h
  let sLeft, sRight
  if (isTop) {
    sLeft = w * lerpX(surfNorm, GEOM.topY, GEOM.neckTop, GEOM.topL, GEOM.neckL, surfNorm)
    sRight = w * lerpX(surfNorm, GEOM.topY, GEOM.neckTop, GEOM.topR, GEOM.neckR, surfNorm)
  } else {
    sLeft = w * lerpX(surfNorm, GEOM.neckBot, GEOM.bottomY, GEOM.neckL, GEOM.botL, surfNorm)
    sRight = w * lerpX(surfNorm, GEOM.neckBot, GEOM.bottomY, GEOM.neckR, GEOM.botR, surfNorm)
  }
  ctx.strokeStyle = tint(accent, 0.45)
  ctx.lineWidth = 1.2
  ctx.beginPath()
  ctx.moveTo(sLeft, surfaceY)
  ctx.lineTo(sRight, surfaceY)
  ctx.stroke()
}

function bottomSurfaceY(h, ratio) {
  const yStart = h * GEOM.neckBot
  const yEnd = h * GEOM.bottomY
  const fillH = (yEnd - yStart) * (1 - ratio)
  return yEnd - fillH
}

function topSurfaceY(h, ratio) {
  const yStart = h * GEOM.topY
  const yEnd = h * GEOM.neckTop
  const fillH = (yEnd - yStart) * ratio
  return yEnd - fillH
}

function spawnParticle(w, h) {
  const topSurf = topSurfaceY(h, displayRatio)
  particles.push({
    x: w * 0.5 + (Math.random() - 0.5) * w * 0.04,
    y: Math.min(h * GEOM.neckTop, topSurf + 2),
    vx: (Math.random() - 0.5) * 0.25,
    vy: 0.5 + Math.random() * 0.9,
    r: 1 + Math.random() * 1.8,
    life: 1,
  })
}

function tick(ts) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const w = canvas.clientWidth
  const h = canvas.clientHeight
  if (!w || !h) return

  displayRatio += (props.remainingRatio - displayRatio) * 0.12

  ctx.clearRect(0, 0, w, h)

  drawSandChamber(ctx, w, h, displayRatio, 'top')
  drawSandChamber(ctx, w, h, displayRatio, 'bottom')

  const accent = cssAccent.value
  const landY = bottomSurfaceY(h, displayRatio)
  const neckY = h * ((GEOM.neckTop + GEOM.neckBot) / 2)

  if (props.running && displayRatio > 0.02) {
    const rate = 28 + displayRatio * 70
    if (ts - lastSpawn > 1000 / rate) {
      spawnParticle(w, h)
      if (displayRatio > 0.2 && Math.random() > 0.4) spawnParticle(w, h)
      lastSpawn = ts
    }
  }

  // 已堆积的砂粒（落在沙面上不再消失）
  settled = settled.filter((g) => {
    if (g.life <= 0) return false
    g.life -= 0.0015
    ctx.globalAlpha = Math.min(0.75, g.life)
    ctx.fillStyle = tint(accent, 0.08)
    ctx.beginPath()
    ctx.arc(g.x, g.y, g.r, 0, Math.PI * 2)
    ctx.fill()
    return true
  })
  ctx.globalAlpha = 1

  particles = particles.filter((p) => {
    p.x += p.vx
    p.y += p.vy
    p.vy += 0.055

    // 颈部收窄
    if (p.y > h * GEOM.neckTop && p.y < h * GEOM.neckBot) {
      const pull = (p.x - w * 0.5) * 0.04
      p.x -= pull
    }

    if (p.y >= landY - p.r) {
      settled.push({
        x: p.x + (Math.random() - 0.5) * w * 0.06,
        y: landY - p.r * 0.3 + (Math.random() - 0.5) * 2,
        r: p.r * 0.85,
        life: 0.55 + Math.random() * 0.45,
      })
      return false
    }

    if (p.y > h * GEOM.bottomY || p.life <= 0) return false

    ctx.fillStyle = accent
    ctx.globalAlpha = Math.min(0.9, p.life)
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx.fill()

    if (props.running && p.y > neckY) {
      ctx.globalAlpha = 0.25
      ctx.beginPath()
      ctx.arc(p.x, p.y + 3, p.r * 0.7, 0, Math.PI * 2)
      ctx.fill()
    }

    ctx.globalAlpha = 1
    return true
  })

  if (props.running || particles.length || settled.length || Math.abs(displayRatio - props.remainingRatio) > 0.002) {
    rafId = requestAnimationFrame(tick)
  } else {
    rafId = 0
  }
}

function startLoop() {
  if (rafId) return
  lastSpawn = 0
  rafId = requestAnimationFrame(tick)
}

function stopLoop() {
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = 0
  }
}

function redraw() {
  displayRatio = props.remainingRatio
  settled = []
  particles = []
  startLoop()
}

watch(() => props.running, (on) => {
  if (on) startLoop()
  else startLoop()
})

watch(() => props.remainingRatio, (r, prev) => {
  if (r > prev + 0.05) {
    settled = []
    particles = []
    displayRatio = r
  }
  startLoop()
})

function onResize() {
  resizeCanvas()
  startLoop()
}

watch(cssAccent, () => startLoop())

onMounted(() => {
  displayRatio = props.remainingRatio
  resizeCanvas()
  window.addEventListener('resize', onResize)
  startLoop()
})

onUnmounted(() => {
  stopLoop()
  window.removeEventListener('resize', onResize)
})

defineExpose({ redraw })
</script>

<style scoped>
.pomo-hourglass {
  --hg-accent: var(--orange);
  position: relative;
  z-index: 1;
  width: min(240px, 62vw);
  margin: 0.75rem auto 0.35rem;
  text-align: center;
}

.pomo-hourglass__frame {
  position: relative;
  aspect-ratio: 200 / 320;
}

.pomo-hourglass__canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.pomo-hourglass__svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
  filter: drop-shadow(0 10px 28px color-mix(in srgb, var(--hg-accent) 22%, transparent));
}

.pomo-hourglass__glass-outer {
  fill: rgba(255, 255, 255, 0.03);
  stroke: color-mix(in srgb, var(--hg-accent) 55%, var(--border));
  stroke-width: 3;
  stroke-linejoin: round;
}

.pomo-hourglass__glass-inner {
  fill: none;
  stroke: color-mix(in srgb, var(--hg-accent) 22%, rgba(255, 255, 255, 0.35));
  stroke-width: 1.2;
  stroke-linejoin: round;
}

.pomo-hourglass__shine {
  pointer-events: none;
}

.pomo-hourglass__neck-glow {
  fill: color-mix(in srgb, var(--hg-accent) 35%, transparent);
  opacity: 0.55;
}

.pomo-hourglass__time {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 3;
  font-family: var(--mono);
  font-size: clamp(1.85rem, 7vw, 2.65rem);
  font-weight: 500;
  letter-spacing: 0.06em;
  color: var(--hg-accent);
  text-shadow:
    0 0 28px color-mix(in srgb, var(--hg-accent) 40%, transparent),
    0 2px 8px rgba(0, 0, 0, 0.45),
    0 1px 0 rgba(255, 255, 255, 0.12);
  pointer-events: none;
}

.pomo-hourglass__sub {
  margin: 0.35rem 0 0.85rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--text-muted);
}

.pomo-hourglass--running .pomo-hourglass__neck-glow {
  animation: hg-neck-pulse 1.1s ease-in-out infinite;
}

.pomo-hourglass--running .pomo-hourglass__svg {
  filter: drop-shadow(0 12px 32px color-mix(in srgb, var(--hg-accent) 32%, transparent));
}

.pomo-hourglass--low .pomo-hourglass__time {
  animation: hg-time-pulse 1.5s ease-in-out infinite;
}

@keyframes hg-neck-pulse {
  0%, 100% { opacity: 0.45; }
  50% { opacity: 0.95; }
}

@keyframes hg-time-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.78; }
}
</style>

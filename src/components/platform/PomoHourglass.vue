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
      <p v-if="totalMinutes > 0" class="pomo-hourglass__balls-hint" aria-hidden="true">
        {{ settledCount }}/{{ totalMinutes }}
      </p>
    </div>

    <p v-if="subText" class="pomo-hourglass__sub">{{ subText }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  displayTime: { type: String, required: true },
  remainingRatio: { type: Number, default: 1 },
  totalMinutes: { type: Number, default: 25 },
  elapsedSeconds: { type: Number, default: 0 },
  running: { type: Boolean, default: false },
  accent: { type: String, default: 'var(--orange)' },
  subText: { type: String, default: '' },
})

const canvasRef = ref(null)
const cssAccent = computed(() => resolveAccent(props.accent))
const settledCount = computed(() => {
  const elapsed = Math.max(0, props.elapsedSeconds)
  return Math.min(props.totalMinutes, Math.floor(elapsed / 60))
})

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

let balls = []
let rafId = 0
let lastReleasedMinute = 0

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

function chamberXBounds(yNorm, chamber) {
  if (chamber === 'top') {
    return {
      left: lerp(GEOM.topL, GEOM.neckL, (yNorm - GEOM.topY) / (GEOM.neckTop - GEOM.topY)),
      right: lerp(GEOM.topR, GEOM.neckR, (yNorm - GEOM.topY) / (GEOM.neckTop - GEOM.topY)),
    }
  }
  return {
    left: lerp(GEOM.neckL, GEOM.botL, (yNorm - GEOM.neckBot) / (GEOM.bottomY - GEOM.neckBot)),
    right: lerp(GEOM.neckR, GEOM.botR, (yNorm - GEOM.neckBot) / (GEOM.bottomY - GEOM.neckBot)),
  }
}

function boundsAtY(y, w, h, chamber) {
  const yNorm = Math.max(0, Math.min(1, y / h))
  const { left, right } = chamberXBounds(yNorm, chamber)
  const pad = ballRadius(w) * 1.05
  return {
    left: w * left + pad,
    right: w * right - pad,
    yMin: h * (chamber === 'top' ? GEOM.topY : GEOM.neckBot) + pad,
    yMax: h * (chamber === 'top' ? GEOM.neckTop : GEOM.bottomY) - pad,
  }
}

function ballRadius(w) {
  const n = Math.max(1, props.totalMinutes)
  const neckW = w * (GEOM.neckR - GEOM.neckL)
  return Math.min(neckW * 0.38, (w * 0.26) / Math.max(2, Math.sqrt(n)))
}

function minutesDropped() {
  const total = Math.max(0, props.totalMinutes)
  const elapsed = Math.max(0, props.elapsedSeconds)
  return Math.min(total, Math.floor(elapsed / 60))
}

function waitingSlots(w, h, count) {
  const r = ballRadius(w)
  const b = boundsAtY(h * GEOM.neckTop - r * 1.2, w, h, 'top')
  const cols = Math.max(1, Math.floor((b.right - b.left) / (r * 2.15)))
  const slots = []
  for (let i = 0; i < count; i += 1) {
    const col = i % cols
    const row = Math.floor(i / cols)
    const x = b.left + r + col * r * 2.15 + (row % 2 ? r * 0.55 : 0)
    const y = b.yMax - r - row * r * 1.95
    slots.push({
      x: Math.min(b.right - r, Math.max(b.left + r, x)),
      y: Math.max(b.yMin + r, y),
    })
  }
  return slots
}

function bottomStackPositions(w, h, count) {
  const r = ballRadius(w)
  const floor = boundsAtY(h * GEOM.bottomY - r, w, h, 'bottom')
  const cols = Math.max(1, Math.floor((floor.right - floor.left) / (r * 2.1)))
  const positions = []
  for (let i = 0; i < count; i += 1) {
    const col = i % cols
    const row = Math.floor(i / cols)
    const x = floor.left + r + col * r * 2.1 + (row % 2 ? r * 0.5 : 0)
    const y = floor.yMax - r - row * r * 1.85
    positions.push({
      x: Math.min(floor.right - r, Math.max(floor.left + r, x)),
      y: Math.max(floor.yMin + r, y),
    })
  }
  return positions
}

function createBalls(w, h) {
  const total = Math.max(1, props.totalMinutes)
  const dropped = minutesDropped()
  const r = ballRadius(w)
  const waitSlots = waitingSlots(w, h, total - dropped)
  const stackPos = bottomStackPositions(w, h, dropped)

  balls = []
  for (let i = 0; i < dropped; i += 1) {
    const p = stackPos[i] || stackPos[stackPos.length - 1]
    balls.push({
      id: i,
      state: 'settled',
      x: p.x,
      y: p.y,
      vx: 0,
      vy: 0,
      r,
      wobble: Math.random() * Math.PI * 2,
    })
  }
  for (let i = 0; i < total - dropped; i += 1) {
    const p = waitSlots[i] || waitSlots[waitSlots.length - 1]
    balls.push({
      id: dropped + i,
      state: 'waiting',
      x: p.x,
      y: p.y,
      vx: 0,
      vy: 0,
      r,
      wobble: Math.random() * Math.PI * 2,
    })
  }
  lastReleasedMinute = dropped
}

function releaseNextBall(w, h) {
  const waiting = balls
    .filter((b) => b.state === 'waiting')
    .sort((a, b) => b.y - a.y)
  const next = waiting[0]
  if (!next) return

  next.state = 'falling'
  next.vx = (Math.random() - 0.5) * 0.6
  next.vy = 0.15
  const neckY = h * ((GEOM.neckTop + GEOM.neckBot) / 2)
  next.y = Math.min(next.y + next.r * 0.5, h * GEOM.neckTop - next.r * 0.5)
  if (next.y < neckY) next.y = neckY - next.r
}

function constrainToWalls(b, w, h) {
  const yNorm = b.y / h
  let chamber = 'top'
  if (yNorm >= GEOM.neckBot) chamber = 'bottom'
  else if (yNorm > GEOM.neckTop && yNorm < GEOM.neckBot) chamber = 'neck'

  if (chamber === 'neck') {
    const pull = (b.x - w * 0.5) * 0.08
    b.vx -= pull
    b.x -= pull * 0.35
    const neckPad = b.r * 0.9
    const left = w * GEOM.neckL + neckPad
    const right = w * GEOM.neckR - neckPad
    if (b.x < left) {
      b.x = left
      b.vx = Math.abs(b.vx) * 0.35
    }
    if (b.x > right) {
      b.x = right
      b.vx = -Math.abs(b.vx) * 0.35
    }
    return
  }

  const bounds = boundsAtY(b.y, w, h, chamber)
  if (b.x - b.r < bounds.left) {
    b.x = bounds.left + b.r
    b.vx = Math.abs(b.vx) * 0.42
  }
  if (b.x + b.r > bounds.right) {
    b.x = bounds.right - b.r
    b.vx = -Math.abs(b.vx) * 0.42
  }
  if (b.y - b.r < bounds.yMin) {
    b.y = bounds.yMin + b.r
    b.vy = Math.abs(b.vy) * 0.3
  }
}

function resolveBallPair(a, b) {
  const dx = b.x - a.x
  const dy = b.y - a.y
  const dist = Math.hypot(dx, dy) || 0.001
  const minDist = a.r + b.r
  if (dist >= minDist) return

  const nx = dx / dist
  const ny = dy / dist
  const overlap = minDist - dist
  const massA = a.state === 'settled' ? 2.5 : 1
  const massB = b.state === 'settled' ? 2.5 : 1
  const total = massA + massB
  a.x -= nx * overlap * (massB / total)
  a.y -= ny * overlap * (massB / total)
  b.x += nx * overlap * (massA / total)
  b.y += ny * overlap * (massA / total)

  if (a.state === 'falling' || b.state === 'falling') {
    const dvx = a.vx - b.vx
    const dvy = a.vy - b.vy
    const impulse = (dvx * nx + dvy * ny) * 0.55
    if (impulse > 0) {
      a.vx -= impulse * nx / massA
      a.vy -= impulse * ny / massA
      b.vx += impulse * nx / massB
      b.vy += impulse * ny / massB
    }
  }
}

function trySettle(b, w, h) {
  const floor = boundsAtY(h * GEOM.bottomY - b.r, w, h, 'bottom')
  const others = balls.filter((o) => o !== b && (o.state === 'settled' || o.state === 'falling'))

  let supportY = floor.yMax - b.r
  for (const o of others) {
    const dx = Math.abs(o.x - b.x)
    if (dx < b.r + o.r - 0.5) {
      const top = o.y - o.r - b.r
      if (top < supportY) supportY = top
    }
  }

  if (b.y >= supportY - 0.5 && Math.abs(b.vy) < 1.8 && Math.hypot(b.vx, b.vy) < 2.2) {
    b.y = supportY
    b.vy = 0
    b.vx *= 0.72
    if (Math.hypot(b.vx, b.vy) < 0.25) {
      b.vx = 0
      b.state = 'settled'
    }
  }
}

function updatePhysics(w, h) {
  const g = h * 0.00042
  const dropped = minutesDropped()

  while (lastReleasedMinute < dropped) {
    releaseNextBall(w, h)
    lastReleasedMinute += 1
  }

  for (const b of balls) {
    if (b.state === 'waiting') {
      b.wobble += 0.02
      b.x += Math.sin(b.wobble) * 0.04
      continue
    }
    if (b.state === 'settled') {
      b.vx *= 0.9
      b.vy *= 0.9
      continue
    }

    b.vy += g
    b.vx *= 0.998
    b.x += b.vx
    b.y += b.vy

    constrainToWalls(b, w, h)

    if (b.y / h >= GEOM.neckBot - 0.01) {
      trySettle(b, w, h)
    }
  }

  for (let i = 0; i < balls.length; i += 1) {
    for (let j = i + 1; j < balls.length; j += 1) {
      if (balls[i].state === 'waiting' && balls[j].state === 'waiting') {
        resolveBallPair(balls[i], balls[j])
      } else if (balls[i].state !== 'waiting' || balls[j].state !== 'waiting') {
        resolveBallPair(balls[i], balls[j])
      }
    }
  }
}

function clipHourglass(ctx, w, h) {
  ctx.beginPath()
  ctx.moveTo(w * GEOM.topL, h * GEOM.topY)
  ctx.lineTo(w * GEOM.topR, h * GEOM.topY)
  ctx.lineTo(w * GEOM.neckR, h * GEOM.neckTop)
  ctx.lineTo(w * GEOM.neckR, h * GEOM.neckBot)
  ctx.lineTo(w * GEOM.botR, h * GEOM.bottomY)
  ctx.lineTo(w * GEOM.botL, h * GEOM.bottomY)
  ctx.lineTo(w * GEOM.neckL, h * GEOM.neckBot)
  ctx.lineTo(w * GEOM.neckL, h * GEOM.neckTop)
  ctx.closePath()
  ctx.clip()
}

function drawBall(ctx, b, accent) {
  const rgb = parseHex(accent) || { r: 232, g: 93, b: 4 }
  const grad = ctx.createRadialGradient(
    b.x - b.r * 0.35,
    b.y - b.r * 0.35,
    b.r * 0.15,
    b.x,
    b.y,
    b.r,
  )
  grad.addColorStop(0, tint(accent, 0.55))
  grad.addColorStop(0.45, accent)
  grad.addColorStop(1, shade(accent, 0.35))

  ctx.fillStyle = grad
  ctx.beginPath()
  ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = `rgba(255,255,255,${b.state === 'waiting' ? 0.35 : 0.28})`
  ctx.beginPath()
  ctx.arc(b.x - b.r * 0.28, b.y - b.r * 0.32, b.r * 0.28, 0, Math.PI * 2)
  ctx.fill()

  if (b.state === 'falling' && b.vy > 0.5) {
    ctx.strokeStyle = `rgba(${rgb.r},${rgb.g},${rgb.b},0.25)`
    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.moveTo(b.x, b.y - b.r)
    ctx.lineTo(b.x - b.vx * 2, b.y - b.r - b.vy * 1.5)
    ctx.stroke()
  }
}

function tick() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const w = canvas.clientWidth
  const h = canvas.clientHeight
  if (!w || !h) return

  if (balls.length !== Math.max(1, props.totalMinutes)) {
    createBalls(w, h)
  }

  const hasFalling = balls.some((b) => b.state === 'falling')
  if (props.running || hasFalling) {
    updatePhysics(w, h)
  }

  ctx.clearRect(0, 0, w, h)
  ctx.save()
  clipHourglass(ctx, w, h)

  const accent = cssAccent.value
  const order = [...balls].sort((a, b) => a.y - b.y)
  for (const b of order) {
    drawBall(ctx, b, accent)
  }
  ctx.restore()

  const needsLoop = props.running
    || balls.some((b) => b.state === 'falling')
    || minutesDropped() > lastReleasedMinute

  if (needsLoop || balls.length) {
    rafId = requestAnimationFrame(tick)
  } else {
    rafId = 0
  }
}

function startLoop() {
  if (rafId) return
  rafId = requestAnimationFrame(tick)
}

function stopLoop() {
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = 0
  }
}

function redraw() {
  balls = []
  lastReleasedMinute = 0
  startLoop()
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
  balls = []
  startLoop()
}

watch(() => props.totalMinutes, () => redraw())
watch(() => props.elapsedSeconds, (cur, prev) => {
  if (cur < prev - 30) redraw()
  else startLoop()
})
watch(() => props.running, () => startLoop())
watch(cssAccent, () => startLoop())

function onResize() {
  resizeCanvas()
}

onMounted(() => {
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

.pomo-hourglass__balls-hint {
  position: absolute;
  right: 8%;
  bottom: 6%;
  z-index: 3;
  margin: 0;
  font-family: var(--mono);
  font-size: 0.55rem;
  letter-spacing: 0.08em;
  color: color-mix(in srgb, var(--hg-accent) 70%, var(--text-muted));
  opacity: 0.85;
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

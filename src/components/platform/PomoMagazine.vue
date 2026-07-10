<template>
  <div
    class="pomo-mag"
    :class="{
      'pomo-mag--running': running,
      'pomo-mag--low': remainingRatio < 0.15,
      'pomo-mag--break': mode === 'break',
    }"
    :style="{ '--mag-accent': accent }"
  >
    <div class="pomo-mag__cockpit">
      <div class="pomo-mag__display">
        <div class="pomo-mag__time">{{ displayTime }}</div>
        <p class="pomo-mag__hud">{{ hudLine }}</p>
      </div>

      <aside class="pomo-mag__gear" :aria-label="gearLabel">
        <!-- 专注：弹匣 -->
        <div v-if="mode === 'focus'" class="pomo-mag__magazine">
          <p class="pomo-mag__tag">AMMO · MAG</p>
          <div class="pomo-mag__slots" :style="slotGridStyle">
            <div
              v-for="i in segments.visualCount"
              :key="`round-${i}`"
              class="pomo-mag__round"
              :class="{
                'is-spent': roundSpent(i),
                'is-next': roundNext(i),
              }"
            >
              <span
                v-if="!roundSpent(i)"
                class="pomo-mag__round-fill"
                :style="{ width: `${roundFill(i) * 100}%` }"
              />
            </div>
          </div>
          <p v-if="segmentHintText" class="pomo-mag__segment-hint">{{ segmentHintText }}</p>
          <p class="pomo-mag__count">{{ remainingRounds }}/{{ totalMinutes }}</p>
        </div>

        <!-- 休息：医疗包 RELOAD -->
        <div v-else class="pomo-mag__medkit">
          <p class="pomo-mag__tag">RELOAD · MED</p>
          <div class="pomo-mag__med-body">
            <span class="pomo-mag__cross" aria-hidden="true">+</span>
            <div class="pomo-mag__med-slots" :style="slotGridStyle">
              <div
                v-for="i in segments.visualCount"
                :key="`med-${i}`"
                class="pomo-mag__med-cell"
                :class="{ 'is-next': medNext(i) }"
              >
                <span class="pomo-mag__med-fill" :style="{ width: `${medFill(i) * 100}%` }" />
              </div>
            </div>
          </div>
          <p v-if="segmentHintText" class="pomo-mag__segment-hint">{{ segmentHintText }}</p>
          <p class="pomo-mag__count">{{ reloadProgress }}/{{ totalMinutes }}</p>
        </div>

        <canvas ref="canvasRef" class="pomo-mag__fx" aria-hidden="true" />
      </aside>
    </div>

    <p v-if="subText" class="pomo-mag__sub">{{ subText }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  chargedSegmentCount,
  getTimerSegments,
  segmentFillRatio,
  segmentHint,
  spentSegmentCount,
} from '../../utils/pomoTimerSegments.js'

const props = defineProps({
  displayTime: { type: String, required: true },
  remainingRatio: { type: Number, default: 1 },
  totalMinutes: { type: Number, default: 25 },
  elapsedSeconds: { type: Number, default: 0 },
  running: { type: Boolean, default: false },
  mode: { type: String, default: 'focus' },
  accent: { type: String, default: '#e85d04' },
  subText: { type: String, default: '' },
})

const canvasRef = ref(null)

const minutesElapsed = computed(() => {
  const total = Math.max(0, props.totalMinutes)
  const elapsed = Math.max(0, props.elapsedSeconds)
  return Math.min(total, Math.floor(elapsed / 60))
})

const remainingRounds = computed(() => Math.max(0, props.totalMinutes - minutesElapsed.value))
const reloadProgress = computed(() => minutesElapsed.value)

const segments = computed(() => getTimerSegments(props.totalMinutes))
const slotGridStyle = computed(() => ({ '--mag-cols': segments.value.cols }))
const segmentHintText = computed(() => segmentHint(segments.value.minutesPerSlot, segments.value.visualCount))

function roundSpent(i) {
  const { minutesPerSlot, visualCount } = segments.value
  return i <= spentSegmentCount(minutesElapsed.value, minutesPerSlot, visualCount)
}

function roundFill(i) {
  return segmentFillRatio(i - 1, minutesElapsed.value, segments.value.minutesPerSlot, 'focus')
}

function roundNext(i) {
  if (!props.running || props.mode !== 'focus' || remainingRounds.value <= 0) return false
  const spent = spentSegmentCount(minutesElapsed.value, segments.value.minutesPerSlot, segments.value.visualCount)
  return i === spent + 1
}

function medFill(i) {
  return segmentFillRatio(i - 1, minutesElapsed.value, segments.value.minutesPerSlot, 'break')
}

function medNext(i) {
  if (!props.running || props.mode !== 'break') return false
  const charged = chargedSegmentCount(minutesElapsed.value, segments.value.minutesPerSlot, segments.value.visualCount)
  return i === charged + 1
}

const gearLabel = computed(() => (
  props.mode === 'focus'
    ? `弹匣剩余 ${remainingRounds.value} 发`
    : `医疗包充能 ${reloadProgress.value}/${props.totalMinutes}`
))

const hudLine = computed(() => {
  if (props.mode === 'break') return `STAND DOWN · RELOAD ${reloadProgress.value}/${props.totalMinutes}`
  return `FOCUS FIRE · AMMO ${remainingRounds.value}/${props.totalMinutes}`
})

const cssAccent = computed(() => {
  if (!props.accent || props.accent.startsWith('var(')) return '#e85d04'
  return props.accent
})

let shells = []
let rafId = 0
let lastFiredMinute = 0

function spawnShell(canvas) {
  const rect = canvas.getBoundingClientRect()
  const w = rect.width
  const h = rect.height
  shells.push({
    x: w * 0.5 + (Math.random() - 0.5) * 24,
    y: h * 0.22,
    vx: (Math.random() - 0.5) * 2.4,
    vy: 1.2 + Math.random() * 1.5,
    rot: Math.random() * Math.PI,
    vr: (Math.random() - 0.5) * 0.22,
    life: 1,
    w: 5 + Math.random() * 3,
    h: 9 + Math.random() * 4,
  })
}

function tick() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const dpr = window.devicePixelRatio || 1
  const w = canvas.clientWidth
  const h = canvas.clientHeight
  if (!w || !h) return

  if (props.mode === 'focus' && props.running) {
    while (lastFiredMinute < minutesElapsed.value) {
      spawnShell(canvas)
      lastFiredMinute += 1
    }
  }

  ctx.clearRect(0, 0, w, h)

  const accent = cssAccent.value
  shells = shells.filter((s) => {
    s.vy += 0.18
    s.x += s.vx
    s.y += s.vy
    s.rot += s.vr
    s.life -= 0.012

    if (s.life <= 0 || s.y > h + 20) return false

    ctx.save()
    ctx.translate(s.x, s.y)
    ctx.rotate(s.rot)
    ctx.globalAlpha = Math.min(0.9, s.life)
    ctx.fillStyle = '#c9a227'
    ctx.fillRect(-s.w / 2, -s.h / 2, s.w, s.h)
    ctx.fillStyle = accent
    ctx.fillRect(-s.w / 2 + 1, -s.h / 2 + 1, s.w - 2, 2)
    ctx.restore()
    return true
  })

  const animating = shells.length > 0
    || (props.running && props.mode === 'focus')
    || lastFiredMinute !== minutesElapsed.value

  if (animating) {
    rafId = requestAnimationFrame(tick)
  } else {
    rafId = 0
  }
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

function resetFx() {
  shells = []
  lastFiredMinute = minutesElapsed.value
  startLoop()
}

watch(() => props.elapsedSeconds, (cur, prev) => {
  if (cur < prev - 20) resetFx()
  else startLoop()
})

watch(() => props.totalMinutes, resetFx)
watch(() => props.mode, resetFx)
watch(() => props.running, () => startLoop())

function onResize() {
  resizeCanvas()
  startLoop()
}

onMounted(() => {
  lastFiredMinute = minutesElapsed.value
  resizeCanvas()
  window.addEventListener('resize', onResize)
  startLoop()
})

onUnmounted(() => {
  stopLoop()
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.pomo-mag {
  --mag-accent: var(--orange);
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: min(420px, 94vw);
  margin: 0.65rem auto 0.25rem;
}

.pomo-mag__cockpit {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.pomo-mag__gear {
  position: relative;
  width: 100%;
  max-width: min(280px, 88vw);
  min-height: 0;
}

.pomo-mag__fx {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
}

.pomo-mag__tag {
  margin: 0 0 0.35rem;
  font-family: var(--mono);
  font-size: 0.55rem;
  letter-spacing: 0.12em;
  color: color-mix(in srgb, var(--mag-accent) 80%, var(--text-muted));
  text-align: center;
}

.pomo-mag__magazine,
.pomo-mag__medkit {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 0.55rem 0.65rem 0.45rem;
  border: 2px solid color-mix(in srgb, var(--mag-accent) 45%, var(--border));
  background: linear-gradient(
    165deg,
    color-mix(in srgb, var(--bg-paper) 88%, var(--mag-accent)) 0%,
    color-mix(in srgb, var(--bg) 95%, #000) 100%
  );
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

.pomo-mag__medkit {
  border-color: color-mix(in srgb, #5a9fd4 50%, var(--border));
  background: linear-gradient(
    165deg,
    color-mix(in srgb, var(--bg-paper) 90%, #5a9fd4) 0%,
    color-mix(in srgb, var(--bg) 95%, #0a1520) 100%
  );
}

.pomo-mag__med-body {
  position: relative;
  padding-top: 0.15rem;
}

.pomo-mag__cross {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -58%);
  font-size: 1.75rem;
  font-weight: 300;
  line-height: 1;
  color: color-mix(in srgb, #5a9fd4 35%, transparent);
  pointer-events: none;
  z-index: 0;
}

.pomo-mag__slots,
.pomo-mag__med-slots {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(var(--mag-cols, 5), 1fr);
  gap: 0.22rem;
}

.pomo-mag__round {
  position: relative;
  height: 16px;
  border-radius: 2px 2px 1px 1px;
  background: color-mix(in srgb, var(--border) 80%, var(--bg));
  overflow: hidden;
  transition: transform 0.2s ease;
}

.pomo-mag__round-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  border-radius: inherit;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--mag-accent) 75%, #fff) 0%,
    color-mix(in srgb, var(--mag-accent) 90%, #000) 100%
  );
  box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.25);
  transition: width 0.45s ease;
}

.pomo-mag__round.is-spent {
  opacity: 0.35;
  transform: scaleY(0.72);
}

.pomo-mag__round.is-spent .pomo-mag__round-fill {
  width: 0 !important;
}

.pomo-mag__round.is-next {
  animation: mag-round-pulse 0.9s ease-in-out infinite;
}

.pomo-mag__med-cell {
  position: relative;
  height: 14px;
  border: 1px solid color-mix(in srgb, #5a9fd4 30%, var(--border));
  background: color-mix(in srgb, var(--bg) 90%, var(--text-muted));
  overflow: hidden;
}

.pomo-mag__med-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  background: color-mix(in srgb, #5a9fd4 65%, #2d6a4f);
  box-shadow: 0 0 8px color-mix(in srgb, #5a9fd4 40%, transparent);
  transition: width 0.45s ease;
}

.pomo-mag__med-cell.is-charged {
  background: transparent;
}

.pomo-mag__med-cell.is-next {
  animation: mag-med-pulse 1.1s ease-in-out infinite;
}

.pomo-mag__count {
  margin: 0.35rem 0 0;
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  text-align: center;
}

.pomo-mag__segment-hint {
  margin: 0.28rem 0 0;
  font-family: var(--mono);
  font-size: 0.52rem;
  letter-spacing: 0.08em;
  color: color-mix(in srgb, var(--text-muted) 85%, var(--mag-accent));
  text-align: center;
}

.pomo-mag__display {
  width: 100%;
  text-align: center;
}

.pomo-mag__time {
  font-family: var(--mono);
  font-size: clamp(1.75rem, 6.5vw, 2.55rem);
  font-weight: 500;
  letter-spacing: 0.06em;
  color: var(--mag-accent);
  text-shadow:
    0 0 28px color-mix(in srgb, var(--mag-accent) 38%, transparent),
    0 2px 8px rgba(0, 0, 0, 0.45);
}

.pomo-mag--break .pomo-mag__time {
  color: color-mix(in srgb, #5a9fd4 85%, var(--mag-accent));
}

.pomo-mag__hud {
  margin: 0.4rem 0 0;
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.pomo-mag__sub {
  margin: 0.45rem 0 0.75rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--text-muted);
  text-align: center;
}

.pomo-mag--running.pomo-mag:not(.pomo-mag--break) .pomo-mag__magazine {
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.06),
    0 0 16px color-mix(in srgb, var(--mag-accent) 22%, transparent);
}

.pomo-mag--low .pomo-mag__time {
  animation: mag-time-pulse 1.5s ease-in-out infinite;
}

@keyframes mag-round-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.06); opacity: 0.85; }
}

@keyframes mag-med-pulse {
  0%, 100% { opacity: 0.45; }
  50% { opacity: 1; }
}

@keyframes mag-time-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.78; }
}
</style>

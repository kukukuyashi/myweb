<template>
  <div
    class="pomo-clock"
    :class="{
      'pomo-clock--focus': mode === 'focus',
      'pomo-clock--break': mode === 'break',
      'pomo-clock--running': running,
      'pomo-clock--low': remainingRatio < 0.15 && mode === 'focus',
    }"
    :style="cssVars"
    role="timer"
    :aria-label="ariaLabel"
  >
    <p class="pomo-clock__hud">{{ hudLine }}</p>

    <div class="pomo-clock__stage">
      <div class="pomo-clock__aura" aria-hidden="true" />
      <div class="pomo-clock__ripple" aria-hidden="true" />

      <svg
        class="pomo-clock__disc"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <defs>
          <filter id="ink-wobble" x="-20%" y="-20%" width="140%" height="140%">
            <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="3" result="t" />
            <feDisplacementMap in="SourceGraphic" in2="t" scale="2.4" />
          </filter>
          <filter id="ink-tip" x="-20%" y="-20%" width="140%" height="140%">
            <feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="2" seed="7" result="t" />
            <feDisplacementMap in="SourceGraphic" in2="t" scale="1.6" />
          </filter>
          <radialGradient id="ink-face" cx="50%" cy="42%" r="62%">
            <stop offset="0%" :stop-color="paperHi" />
            <stop offset="65%" :stop-color="paperMid" />
            <stop offset="100%" :stop-color="paperLo" />
          </radialGradient>
        </defs>

        <!-- 充墨圆环(仅休息) -->
        <g v-if="mode === 'break'" class="pomo-clock__charge">
          <circle
            class="pomo-clock__charge-ring"
            cx="100" cy="100" r="84"
            fill="none"
            :stroke="inkColor"
            stroke-width="2.2"
            stroke-linecap="round"
            :stroke-dasharray="chargeLen"
            :stroke-dashoffset="chargeOffset"
          />
        </g>

        <!-- 60 细刻度 -->
        <g class="pomo-clock__ticks">
          <line
            v-for="t in minorTicks"
            :key="`mi-${t.idx}`"
            :x1="t.x1" :y1="t.y1" :x2="t.x2" :y2="t.y2"
            :stroke="inkColor"
            stroke-width="0.4"
            stroke-linecap="round"
            opacity="0.3"
          />
        </g>

        <!-- 5 主刻度 + 数字标签 -->
        <g class="pomo-clock__majors">
          <template v-for="m in majorTicks" :key="`ma-${m.idx}`">
            <line
              :x1="m.x1" :y1="m.y1" :x2="m.x2" :y2="m.y2"
              :stroke="inkColor"
              stroke-width="1.5"
              stroke-linecap="round"
              opacity="0.78"
            />
            <text
              :x="m.lx" :y="m.ly"
              :fill="inkColor"
              font-size="7"
              font-family="Kaiti SC, STKaiti, KaiTi, STZhongsong, FangSong, serif"
              text-anchor="middle"
              dominant-baseline="middle"
              opacity="0.6"
            >{{ m.label }}</text>
          </template>
        </g>

        <!-- 底盘:墨纸 -->
        <circle cx="100" cy="100" r="92" fill="url(#ink-face)" />

        <!-- 外圈 3 条墨线(粗细不等,模拟笔触) -->
        <g class="pomo-clock__rings" filter="url(#ink-wobble)">
          <circle cx="100" cy="100" r="88" fill="none" :stroke="inkColor" stroke-width="2.4" opacity="0.85" />
          <circle cx="101.5" cy="98.5" r="86" fill="none" :stroke="inkColor" stroke-width="1.6" opacity="0.6" />
          <circle cx="98.5" cy="101.5" r="84" fill="none" :stroke="inkColor" stroke-width="0.8" opacity="0.4" />
        </g>

        <!-- 指针 -->
        <g
          class="pomo-clock__pointer"
          :style="pointerStyle"
          filter="url(#ink-tip)"
        >
          <path
            d="M 100 100 Q 100 60 100 18"
            fill="none"
            :stroke="inkColor"
            stroke-width="2.2"
            stroke-linecap="round"
            opacity="0.92"
          />
          <circle cx="100" cy="100" r="3.4" :fill="inkColor" opacity="0.92" />
          <circle cx="100" cy="100" r="1.4" :fill="paperHi" opacity="0.85" />
        </g>

        <!-- 中心数字 + 副文字 -->
        <text
          class="pomo-clock__time"
          x="100" y="92"
          text-anchor="middle"
          dominant-baseline="middle"
          :fill="inkColor"
        >{{ displayTime }}</text>
        <text
          class="pomo-clock__sub"
          x="100" y="122"
          text-anchor="middle"
          dominant-baseline="middle"
          :fill="inkColor"
          opacity="0.5"
        >{{ minutesLeft }} / {{ totalMinutes }}</text>

        <!-- 墨滴(仅 focus + running) -->
        <g v-if="mode === 'focus' && running" class="pomo-clock__splatter" aria-hidden="true">
          <circle
            v-for="d in drops"
            :key="`d-${d.idx}`"
            :cx="100 + d.dx"
            :cy="100 + d.dy"
            :r="d.r"
            :fill="inkColor"
            :style="{ animationDelay: `${d.delay}s` }"
          />
        </g>
      </svg>
    </div>

    <p v-if="subText" class="pomo-clock__subtext">{{ subText }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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

const inkColor = computed(() => {
  if (props.mode === 'break') return 'color-mix(in srgb, #5a8aaa 80%, #0a1820)'
  return 'color-mix(in srgb, #c14a2a 80%, #2a1a14)'
})

const paperHi = computed(() => props.mode === 'break' ? 'rgba(238, 245, 252, 0.95)' : 'rgba(252, 246, 238, 0.95)')
const paperMid = computed(() => props.mode === 'break' ? 'rgba(220, 232, 244, 0.82)' : 'rgba(244, 232, 220, 0.82)')
const paperLo = computed(() => props.mode === 'break' ? 'rgba(190, 210, 230, 0.7)' : 'rgba(220, 200, 180, 0.7)')

// 指针顺时针:从 12 点扫到 remainingRatio=0 时回到 12 点
// elapsed = (1 - remainingRatio) * 360
const pointerAngle = computed(() => (1 - Math.max(0, Math.min(1, props.remainingRatio))) * 360)

const pointerStyle = computed(() => ({
  transform: `rotate(${pointerAngle.value}deg)`,
  transformOrigin: '100px 100px',
  transformBox: 'fill-box',
}))

const minorTicks = computed(() => {
  const out = []
  for (let i = 0; i < 60; i++) {
    if (i % 15 === 0) continue
    const a = (i * 6 - 90) * Math.PI / 180
    out.push({
      idx: i,
      x1: 100 + 78 * Math.cos(a), y1: 100 + 78 * Math.sin(a),
      x2: 100 + 81 * Math.cos(a), y2: 100 + 81 * Math.sin(a),
    })
  }
  return out
})

const majorTicks = computed(() => {
  const labels = ['0', '15', '30', '45', '60']
  const out = []
  for (let i = 0; i < 5; i++) {
    const a = (i * 90 - 90) * Math.PI / 180
    out.push({
      idx: i,
      label: labels[i],
      x1: 100 + 76 * Math.cos(a), y1: 100 + 76 * Math.sin(a),
      x2: 100 + 84 * Math.cos(a), y2: 100 + 84 * Math.sin(a),
      lx: 100 + 66 * Math.cos(a), ly: 100 + 66 * Math.sin(a),
    })
  }
  return out
})

const minutesLeft = computed(() => Math.max(0, Math.ceil(props.remainingRatio * props.totalMinutes - 0.001)))

const chargeLen = 2 * Math.PI * 84
const chargeOffset = computed(() => chargeLen * (1 - Math.max(0, Math.min(1, props.remainingRatio))))

const drops = computed(() => {
  const out = []
  for (let i = 0; i < 12; i++) {
    const a = (i * 30 - 90) * Math.PI / 180
    out.push({
      idx: i,
      dx: 95 * Math.cos(a),
      dy: 95 * Math.sin(a),
      r: 0.9 + (i % 3) * 0.45,
      delay: i * 0.22,
    })
  }
  return out
})

const hudLine = computed(() => {
  if (props.mode === 'break') {
    return `屏息 · 充墨 ${Math.min(props.totalMinutes, Math.floor((1 - props.remainingRatio) * props.totalMinutes))} / ${props.totalMinutes}`
  }
  return `墨韵 · 剩余 ${minutesLeft.value} · ${props.totalMinutes}`
})

const ariaLabel = computed(() => {
  const tag = props.mode === 'focus' ? '专注' : '休息'
  return `${tag} 剩余 ${props.displayTime}`
})

const cssVars = computed(() => ({
  '--clock-ink': inkColor.value,
  '--clock-paper': paperMid.value,
}))
</script>

<style scoped>
.pomo-clock {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  padding: 0.75rem 0.5rem 0.5rem;
  isolation: isolate;
  font-family: var(--mono, ui-monospace, monospace);
}

.pomo-clock__hud {
  margin: 0;
  font-size: 0.62rem;
  letter-spacing: 0.2em;
  color: var(--clock-ink, rgba(193, 74, 42, 0.78));
  opacity: 0.85;
}

.pomo-clock__stage {
  position: relative;
  width: clamp(180px, 32vw, 280px);
  height: clamp(180px, 32vw, 280px);
  display: grid;
  place-items: center;
}

.pomo-clock__aura {
  position: absolute;
  inset: -10%;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 50%,
    color-mix(in srgb, var(--clock-ink, #c14a2a) 24%, transparent) 0%,
    color-mix(in srgb, var(--clock-ink, #c14a2a) 8%, transparent) 38%,
    transparent 68%);
  pointer-events: none;
  filter: blur(10px);
  z-index: 0;
  animation: ink-breathe 9s ease-in-out infinite;
}

.pomo-clock--break .pomo-clock__aura {
  animation-direction: reverse;
  animation-duration: 11s;
}

.pomo-clock--running .pomo-clock__aura {
  animation-duration: 6s;
  opacity: 1;
}

.pomo-clock__disc {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 18px color-mix(in srgb, var(--clock-ink, #c14a2a) 28%, transparent));
  animation: ink-disc-pulse 4s ease-in-out infinite;
}

.pomo-clock--break .pomo-clock__disc {
  filter: drop-shadow(0 0 18px color-mix(in srgb, var(--clock-ink, #5a8aaa) 28%, transparent));
}

.pomo-clock--low .pomo-clock__disc {
  filter: drop-shadow(0 0 24px rgba(217, 71, 43, 0.4));
  animation-duration: 1.8s;
}

.pomo-clock__ripple {
  position: absolute;
  inset: -4%;
  border-radius: 50%;
  border: 1.5px solid color-mix(in srgb, var(--clock-ink, #c14a2a) 65%, transparent);
  pointer-events: none;
  z-index: 0;
  opacity: 0;
}

:global(.pomo-core--celebrate) .pomo-clock__ripple {
  animation: ink-ripple 0.8s ease-out;
}
:global(.pomo-core--celebrate) .pomo-clock__disc {
  animation: ink-disc-celebrate 0.8s ease-out;
}

.pomo-clock__time {
  font-family: 'Kaiti SC', 'STKaiti', 'KaiTi', 'STZhongsong', 'FangSong', serif;
  font-size: clamp(1.7rem, 5.5vw, 2.7rem);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.08em;
  paint-order: stroke fill;
}

.pomo-clock__sub {
  font-family: 'Kaiti SC', 'STKaiti', 'KaiTi', serif;
  font-size: 0.62rem;
  letter-spacing: 0.2em;
}

.pomo-clock__pointer {
  transition: transform 0.9s cubic-bezier(0.4, 0, 0.2, 1);
}

.pomo-clock__charge-ring {
  transition: stroke-dashoffset 1.2s ease-out;
  transform-origin: 100px 100px;
  transform: rotate(-90deg);
  filter: drop-shadow(0 0 4px color-mix(in srgb, var(--clock-ink, #5a8aaa) 45%, transparent));
}

.pomo-clock__splatter circle {
  opacity: 0;
  transform-origin: center;
  animation: ink-drop 2.6s ease-out infinite;
  filter: blur(0.3px);
}

@keyframes ink-breathe {
  0%, 100% { transform: scale(0.96); opacity: 0.55; }
  50% { transform: scale(1.06); opacity: 1; }
}

@keyframes ink-disc-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.014); }
}

@keyframes ink-ripple {
  0% { transform: scale(0.96); opacity: 0; }
  20% { opacity: 0.6; }
  100% { transform: scale(1.22); opacity: 0; }
}

@keyframes ink-disc-celebrate {
  0% { transform: scale(1); }
  40% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes ink-drop {
  0% { opacity: 0; transform: translate(0, 0) scale(0.4); }
  12% { opacity: 0.9; transform: translate(calc(var(--tx, 8px) * 0.2), calc(var(--ty, 12px) * 0.2)) scale(1); }
  60% { opacity: 0.5; transform: translate(var(--tx, 8px), var(--ty, 12px)) scale(1.1); }
  100% { opacity: 0; transform: translate(calc(var(--tx, 8px) * 1.5), calc(var(--ty, 12px) * 1.7)) scale(0.55); }
}

.pomo-clock__splatter circle:nth-child(6n+1) { --tx: 12px; --ty: 6px; }
.pomo-clock__splatter circle:nth-child(6n+2) { --tx: -10px; --ty: 4px; }
.pomo-clock__splatter circle:nth-child(6n+3) { --tx: 6px; --ty: 12px; }
.pomo-clock__splatter circle:nth-child(6n+4) { --tx: -4px; --ty: -10px; }
.pomo-clock__splatter circle:nth-child(6n+5) { --tx: 14px; --ty: -6px; }
.pomo-clock__splatter circle:nth-child(6n+6) { --tx: -14px; --ty: -2px; }
.pomo-clock__splatter circle:nth-child(12n+7) { --tx: 8px; --ty: 14px; }
.pomo-clock__splatter circle:nth-child(12n+8) { --tx: -12px; --ty: 8px; }
.pomo-clock__splatter circle:nth-child(12n+9) { --tx: 2px; --ty: -14px; }
.pomo-clock__splatter circle:nth-child(12n+10) { --tx: -6px; --ty: -12px; }
.pomo-clock__splatter circle:nth-child(12n+11) { --tx: 16px; --ty: 0; }
.pomo-clock__splatter circle:nth-child(12n+12) { --tx: -16px; --ty: 0; }

.pomo-clock__subtext {
  margin: 0.45rem 0 0.25rem;
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  color: var(--clock-ink, rgba(193, 74, 42, 0.55));
  opacity: 0.7;
  text-align: center;
}

@media (prefers-reduced-motion: reduce) {
  .pomo-clock__aura,
  .pomo-clock__disc,
  .pomo-clock__pointer,
  .pomo-clock__splatter circle,
  :global(.pomo-core--celebrate) .pomo-clock__ripple,
  :global(.pomo-core--celebrate) .pomo-clock__disc {
    animation: none !important;
    transition: none !important;
  }
  .pomo-clock__splatter circle { opacity: 0; }
  .pomo-clock__aura { opacity: 0.7; }
}
</style>

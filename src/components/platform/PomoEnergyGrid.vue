<template>
  <div
    class="pomo-energy"
    :class="{
      'pomo-energy--running': running,
      'pomo-energy--low': remainingRatio < 0.15,
      'pomo-energy--break': mode === 'break',
    }"
    :style="{ '--pe-accent': accent }"
  >
    <div class="pomo-energy__time">{{ displayTime }}</div>

    <div class="pomo-energy__grid" :style="gridStyle" :aria-label="gridLabel">
      <span
        v-for="i in segments.visualCount"
        :key="i"
        class="pomo-energy__cell"
        :class="cellClass(i - 1)"
      >
        <span class="pomo-energy__cell-fill" :style="{ width: `${cellFill(i - 1) * 100}%` }" />
      </span>
    </div>

    <p v-if="segmentHintText" class="pomo-energy__segment-hint">{{ segmentHintText }}</p>
    <p class="pomo-energy__hud">{{ hudText }}</p>
    <p v-if="subText" class="pomo-energy__sub">{{ subText }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getTimerSegments, segmentFillRatio, segmentHint } from '../../utils/pomoTimerSegments.js'

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

const minutesElapsed = computed(() => {
  const total = Math.max(0, props.totalMinutes)
  const elapsed = Math.max(0, props.elapsedSeconds)
  return Math.min(total, Math.floor(elapsed / 60))
})

const segments = computed(() => getTimerSegments(props.totalMinutes))
const gridStyle = computed(() => ({ '--pe-cols': segments.value.cols }))
const segmentHintText = computed(() => segmentHint(segments.value.minutesPerSlot, segments.value.visualCount))

const gridLabel = computed(() => {
  if (props.mode === 'break') {
    return `恢复进度 ${minutesElapsed.value}/${props.totalMinutes}`
  }
  return `剩余能量 ${props.totalMinutes - minutesElapsed.value}/${props.totalMinutes}`
})

const hudText = computed(() => {
  if (props.mode === 'break') {
    return `RECHARGE · ${minutesElapsed.value}/${props.totalMinutes}`
  }
  return `ENERGY · ${props.totalMinutes - minutesElapsed.value}/${props.totalMinutes}`
})

function cellFill(index) {
  const mode = props.mode === 'break' ? 'break' : 'focus'
  return segmentFillRatio(index, minutesElapsed.value, segments.value.minutesPerSlot, mode)
}

function cellClass(index) {
  const fill = cellFill(index)
  const isNext = props.running && (
    props.mode === 'break'
      ? fill > 0 && fill < 1
      : fill > 0 && fill < 1
  )
  return {
    'is-filled': fill >= 0.999,
    'is-empty': fill <= 0.001,
    'is-next': isNext || (props.running && fill > 0.001 && fill < 0.999),
  }
}
</script>

<style scoped>
.pomo-energy {
  --pe-accent: var(--orange);
  position: relative;
  z-index: 1;
  width: min(320px, 88vw);
  margin: 0.75rem auto 0.35rem;
  text-align: center;
}

.pomo-energy__time {
  font-family: var(--mono);
  font-size: clamp(1.85rem, 7vw, 2.65rem);
  font-weight: 500;
  letter-spacing: 0.06em;
  color: var(--pe-accent);
  text-shadow:
    0 0 24px color-mix(in srgb, var(--pe-accent) 35%, transparent),
    0 2px 6px rgba(0, 0, 0, 0.35);
  margin-bottom: 0.85rem;
}

.pomo-energy__grid {
  display: grid;
  grid-template-columns: repeat(var(--pe-cols, 5), 1fr);
  gap: 0.4rem;
  max-width: 280px;
  margin: 0 auto;
  padding: 0.65rem;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg-paper) 90%, var(--pe-accent));
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
}

.pomo-energy__cell {
  position: relative;
  aspect-ratio: 1;
  border: 1px solid color-mix(in srgb, var(--pe-accent) 25%, var(--border));
  background: color-mix(in srgb, var(--bg) 92%, var(--text-muted));
  overflow: hidden;
}

.pomo-energy__cell-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  background: color-mix(in srgb, var(--pe-accent) 72%, #000);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--pe-accent) 40%, #fff);
  transition: width 0.45s ease;
}

.pomo-energy--break .pomo-energy__cell-fill {
  background: color-mix(in srgb, var(--pe-accent) 55%, #2d6a4f);
}

.pomo-energy__cell.is-next {
  animation: pe-pulse 1.1s ease-in-out infinite;
}

.pomo-energy--running .pomo-energy__cell.is-next {
  transform: scale(1.04);
}

.pomo-energy__segment-hint {
  margin: 0.45rem 0 0;
  font-family: var(--mono);
  font-size: 0.52rem;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.pomo-energy__hud {
  margin: 0.55rem 0 0;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  color: var(--text-muted);
}

.pomo-energy__sub {
  margin: 0.35rem 0 0.85rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--text-muted);
}

.pomo-energy--low .pomo-energy__time {
  animation: pe-time-pulse 1.5s ease-in-out infinite;
}

@keyframes pe-pulse {
  0%, 100% { opacity: 0.55; }
  50% { opacity: 1; }
}

@keyframes pe-time-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.78; }
}
</style>

<template>
  <div
    class="player-spectrum"
    :class="{ 'player-spectrum--live': playing, 'player-spectrum--mini': collapsed }"
    aria-hidden="true"
  >
    <span
      v-for="i in barCount"
      :key="i"
      class="spectrum-bar"
      :style="{ '--h': heights[i - 1] }"
    />
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  playing: { type: Boolean, default: false },
  collapsed: { type: Boolean, default: false },
})

const barCount = props.collapsed ? 8 : 14
const heights = ref(Array.from({ length: barCount }, () => 0.12))

let raf = 0
let phase = 0

function fakeBars() {
  phase += 0.14
  heights.value = heights.value.map((_, i) => {
    const wave = Math.sin(phase + i * 0.55) * 0.5 + 0.5
    const jitter = Math.random() * 0.25
    return 0.1 + (wave * 0.55 + jitter) * 0.65
  })
}

function tick() {
  if (!props.playing) return

  const spec = window.__musicSpectrum
  if (spec) {
    if (spec.ctx.state === 'suspended') spec.ctx.resume()
    spec.analyser.getByteFrequencyData(spec.data)
    const len = spec.data.length
    heights.value = heights.value.map((_, i) => {
      const idx = Math.min(len - 1, Math.floor((i / barCount) * len * 0.85))
      return 0.08 + (spec.data[idx] / 255) * 0.92
    })
  } else {
    fakeBars()
  }

  raf = requestAnimationFrame(tick)
}

function stopLoop() {
  if (raf) cancelAnimationFrame(raf)
  raf = 0
  heights.value = heights.value.map(() => 0.12)
}

function startLoop() {
  stopLoop()
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    heights.value = heights.value.map(() => props.playing ? 0.35 : 0.12)
    return
  }
  if (props.playing) raf = requestAnimationFrame(tick)
}

watch(
  () => props.playing,
  playing => { playing ? startLoop() : stopLoop() },
  { immediate: true }
)

onUnmounted(stopLoop)
</script>

<style scoped>
.player-spectrum {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 22px;
  flex-shrink: 0;
  opacity: 0.45;
  transition: opacity 0.2s;
}

.player-spectrum--live {
  opacity: 1;
}

.player-spectrum--mini {
  height: 14px;
  gap: 1px;
}

.spectrum-bar {
  display: block;
  width: 3px;
  min-height: 3px;
  height: calc(3px + var(--h, 0.12) * 18px);
  background: linear-gradient(to top, rgba(232, 93, 4, 0.55), var(--orange));
  transition: height 0.07s ease-out;
}

.player-spectrum--mini .spectrum-bar {
  width: 2px;
  height: calc(2px + var(--h, 0.12) * 10px);
}

@media (prefers-reduced-motion: reduce) {
  .spectrum-bar {
    transition: none;
  }
}
</style>

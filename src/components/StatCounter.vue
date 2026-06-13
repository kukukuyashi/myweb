<template>
  <span ref="rootRef" class="stat-counter">{{ display }}</span>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  value: { type: [Number, String], required: true },
  duration: { type: Number, default: 900 },
})

const rootRef = ref(null)
const display = ref(typeof props.value === 'number' ? 0 : props.value)
let observer = null
let raf = 0

function animateTo(target) {
  if (typeof target !== 'number') {
    display.value = target
    return
  }
  const start = performance.now()
  const from = 0
  const run = now => {
    const t = Math.min(1, (now - start) / props.duration)
    const eased = 1 - (1 - t) ** 3
    display.value = Math.round(from + (target - from) * eased)
    if (t < 1) raf = requestAnimationFrame(run)
  }
  raf = requestAnimationFrame(run)
}

function startIfVisible() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    display.value = props.value
    return
  }
  animateTo(props.value)
}

onMounted(() => {
  if (typeof props.value !== 'number') {
    display.value = props.value
    return
  }
  observer = new IntersectionObserver(
    entries => {
      if (entries[0]?.isIntersecting) {
        startIfVisible()
        observer?.disconnect()
      }
    },
    { threshold: 0.3 }
  )
  if (rootRef.value) observer.observe(rootRef.value)
})

watch(() => props.value, v => {
  if (typeof v !== 'number') display.value = v
})

onUnmounted(() => {
  observer?.disconnect()
  if (raf) cancelAnimationFrame(raf)
})
</script>

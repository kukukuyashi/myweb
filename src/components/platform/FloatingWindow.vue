<template>
  <section
    class="floating-window"
    :style="{ transform: `translate(${offset.x}px, ${offset.y}px)` }"
  >
    <header
      class="floating-window__header"
      @pointerdown="startDrag"
    >
      <div class="floating-window__title">
        <p>{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
      </div>
      <button type="button" aria-label="关闭窗口" title="关闭窗口" @click="emit('close')">
        <span aria-hidden="true">✕</span>
      </button>
    </header>
    <div class="floating-window__body">
      <slot />
    </div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, ref } from 'vue'

defineProps({
  eyebrow: { type: String, default: 'FLOATING WINDOW' },
  title: { type: String, required: true },
})

const emit = defineEmits(['close'])

const offset = ref({ x: 0, y: 0 })
let dragStart = null

function startDrag(event) {
  if (event.button !== 0 || event.target.closest('button')) return
  dragStart = {
    pointerX: event.clientX,
    pointerY: event.clientY,
    offsetX: offset.value.x,
    offsetY: offset.value.y,
  }
  event.currentTarget.setPointerCapture(event.pointerId)
  window.addEventListener('pointermove', onDrag)
  window.addEventListener('pointerup', stopDrag)
  window.addEventListener('pointercancel', stopDrag)
}

function onDrag(event) {
  if (!dragStart) return
  offset.value = {
    x: dragStart.offsetX + event.clientX - dragStart.pointerX,
    y: dragStart.offsetY + event.clientY - dragStart.pointerY,
  }
}

function stopDrag() {
  dragStart = null
  window.removeEventListener('pointermove', onDrag)
  window.removeEventListener('pointerup', stopDrag)
  window.removeEventListener('pointercancel', stopDrag)
}

onBeforeUnmount(stopDrag)
</script>

<style scoped>
.floating-window {
  position: fixed;
  z-index: 1200;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 18px;
  background:
    radial-gradient(circle at 18% 0%, rgba(255, 209, 102, 0.10), transparent 38%),
    rgba(15, 18, 24, 0.90);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.03),
    0 24px 70px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(20px);
}

.floating-window__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.8rem 0.9rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.10);
  cursor: grab;
  touch-action: none;
  user-select: none;
}

.floating-window__header:active {
  cursor: grabbing;
}

.floating-window__title p {
  margin: 0 0 0.15rem;
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.56);
}

.floating-window__title h2 {
  margin: 0;
  font-size: 0.95rem;
}

.floating-window__header button {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.floating-window__header button:hover {
  border-color: rgba(255, 255, 255, 0.32);
  background: rgba(255, 255, 255, 0.14);
}

.floating-window__body {
  min-height: 0;
  overflow: auto;
}
</style>

<template>
  <section
    class="floating-window"
    :style="windowStyle"
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
    <div
      class="floating-window__resize"
      role="separator"
      aria-orientation="diagonal"
      aria-label="调整窗口大小"
      title="拖拽调整大小"
      tabindex="0"
      @pointerdown="startResize"
      @keydown="onResizeKeydown"
    >
      <span aria-hidden="true"></span>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'

const props = defineProps({
  eyebrow: { type: String, default: 'FLOATING WINDOW' },
  title: { type: String, required: true },
  width: { type: Number, default: null },
  height: { type: Number, default: null },
  minWidth: { type: Number, default: 300 },
  minHeight: { type: Number, default: 220 },
})

const emit = defineEmits(['close'])

const offset = ref({ x: 0, y: 0 })
const size = ref({
  width: props.width,
  height: props.height,
})
let dragStart = null
let resizeStart = null

const windowStyle = computed(() => ({
  transform: `translate(${offset.value.x}px, ${offset.value.y}px)`,
  ...(size.value.width ? { width: `${size.value.width}px` } : {}),
  ...(size.value.height ? { height: `${size.value.height}px` } : {}),
}))

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

function startResize(event) {
  if (event.button !== 0) return
  resizeStart = {
    pointerX: event.clientX,
    pointerY: event.clientY,
    offsetX: offset.value.x,
    offsetY: offset.value.y,
    width: size.value.width ?? event.currentTarget.parentElement.offsetWidth,
    height: size.value.height ?? event.currentTarget.parentElement.offsetHeight,
  }
  event.currentTarget.setPointerCapture(event.pointerId)
  window.addEventListener('pointermove', onResize)
  window.addEventListener('pointerup', stopResize)
  window.addEventListener('pointercancel', stopResize)
}

function onResize(event) {
  if (!resizeStart) return
  const maxWidth = Math.max(props.minWidth, window.innerWidth - 16)
  const maxHeight = Math.max(props.minHeight, window.innerHeight - 16)
  const width = Math.min(maxWidth, Math.max(props.minWidth, resizeStart.width + event.clientX - resizeStart.pointerX))
  const height = Math.min(maxHeight, Math.max(props.minHeight, resizeStart.height + event.clientY - resizeStart.pointerY))
  size.value = { width, height }
  offset.value = {
    x: resizeStart.offsetX + width - resizeStart.width,
    y: resizeStart.offsetY + height - resizeStart.height,
  }
}

function onResizeKeydown(event) {
  if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return
  event.preventDefault()
  const step = event.shiftKey ? 40 : 12
  const delta = {
    ArrowLeft: [-step, 0],
    ArrowRight: [step, 0],
    ArrowUp: [0, -step],
    ArrowDown: [0, step],
  }[event.key]
  const currentWidth = size.value.width ?? event.currentTarget.parentElement.offsetWidth
  const currentHeight = size.value.height ?? event.currentTarget.parentElement.offsetHeight
  const width = Math.max(props.minWidth, currentWidth + delta[0])
  const height = Math.max(props.minHeight, currentHeight + delta[1])
  size.value = { width, height }
  offset.value = {
    x: offset.value.x + width - currentWidth,
    y: offset.value.y + height - currentHeight,
  }
}

function stopResize() {
  resizeStart = null
  window.removeEventListener('pointermove', onResize)
  window.removeEventListener('pointerup', stopResize)
  window.removeEventListener('pointercancel', stopResize)
}

onBeforeUnmount(() => {
  stopDrag()
  stopResize()
})
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

.floating-window__resize {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  cursor: nwse-resize;
  touch-action: none;
}

.floating-window__resize span {
  width: 10px;
  height: 10px;
  border-right: 2px solid rgba(255, 255, 255, 0.34);
  border-bottom: 2px solid rgba(255, 255, 255, 0.34);
  border-radius: 0 0 4px 0;
  transition: border-color 0.2s ease;
}

.floating-window__resize:hover span,
.floating-window__resize:focus-visible span {
  border-color: rgba(255, 209, 102, 0.85);
}

.floating-window__resize:focus-visible {
  outline: none;
  box-shadow: inset 0 0 0 1px rgba(255, 209, 102, 0.35);
}
</style>

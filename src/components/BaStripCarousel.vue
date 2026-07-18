<template>
  <div class="ba-carousel" @mouseenter="paused = true" @mouseleave="paused = false">
    <div class="ba-carousel-viewport">
      <div
        class="ba-carousel-track"
        :class="{
          'ba-carousel-track--paused': paused,
          'ba-carousel-track--loop': showLoop,
        }"
      >
        <button
          v-for="(item, index) in renderItems"
          :key="`${item.path}-${item._copy}-${index}`"
          type="button"
          class="ba-carousel-cell"
          @click="emit('select', item.index)"
        >
          <div class="acg-frame acg-frame--gallery">
            <img :src="thumbUrl(item.path)" :alt="item.label" loading="lazy" decoding="async">
          </div>
          <span class="ba-carousel-label">{{ item.label }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { imgUrl } from '../data/profile.js'
import { thumbUrl } from '../utils/thumbs.js'

const props = defineProps({
  items: { type: Array, required: true },
})

const emit = defineEmits(['select'])

const paused = ref(false)
/** 延后挂载第二份，避免首屏并发翻倍；第二份命中浏览器缓存 */
const showLoop = ref(false)
let loopTimer = null

const baseItems = computed(() =>
  props.items.map((item, index) => ({ ...item, index, _copy: 0 })),
)

const renderItems = computed(() => {
  if (!showLoop.value) return baseItems.value
  return [
    ...baseItems.value,
    ...props.items.map((item, index) => ({ ...item, index, _copy: 1 })),
  ]
})

onMounted(() => {
  loopTimer = window.setTimeout(() => {
    showLoop.value = true
  }, 1800)
})

onUnmounted(() => {
  if (loopTimer) window.clearTimeout(loopTimer)
})
</script>

<style scoped>
.ba-carousel {
  margin: 0 -0.35rem;
}

.ba-carousel-viewport {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent);
}

.ba-carousel-viewport::-webkit-scrollbar {
  display: none;
}

.ba-carousel-track {
  display: flex;
  gap: 0.75rem;
  width: max-content;
  padding: 0.25rem 0.5rem 0.5rem;
}

.ba-carousel-track--loop {
  animation: ba-scroll 42s linear infinite;
}

.ba-carousel-track--paused {
  animation-play-state: paused;
}

.ba-carousel-cell {
  flex: 0 0 auto;
  width: clamp(100px, 14vw, 140px);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-align: center;
  color: inherit;
}

.ba-carousel-cell:hover :deep(.acg-frame) {
  border-color: var(--orange);
}

.ba-carousel-label {
  display: block;
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  margin-top: 0.3rem;
}

@keyframes ba-scroll {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

@media (prefers-reduced-motion: reduce) {
  .ba-carousel-track--loop {
    animation: none;
  }
}
</style>

<template>
  <div class="ba-carousel" @mouseenter="paused = true" @mouseleave="paused = false">
    <div class="ba-carousel-viewport">
      <div class="ba-carousel-track" :class="{ 'ba-carousel-track--paused': paused }">
        <button
          v-for="(item, index) in loopItems"
          :key="`${item.path}-${index}`"
          type="button"
          class="ba-carousel-cell"
          @click="emit('select', item.index)"
        >
          <div class="acg-frame acg-frame--gallery">
            <img :src="imgUrl(item.path)" :alt="item.label" loading="lazy" decoding="async">
          </div>
          <span class="ba-carousel-label">{{ item.label }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { imgUrl } from '../data/profile.js'

const props = defineProps({
  items: { type: Array, required: true },
})

const emit = defineEmits(['select'])

const paused = ref(false)

const loopItems = computed(() => [
  ...props.items.map((item, index) => ({ ...item, index })),
  ...props.items.map((item, index) => ({ ...item, index })),
])
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
  .ba-carousel-track {
    animation: none;
  }
}
</style>

<template>
  <div class="sticker-wall">
    <div class="sticker-grid">
      <article
        v-for="(item, index) in items"
        :key="item.path"
        class="sticker-card"
        :class="{ active: activeIndex === index }"
        @mouseenter="activeIndex = index"
        @mouseleave="activeIndex = -1"
        @click="openLightbox(index)"
      >
        <span class="sticker-badge">
          <span class="badge-icon">◉</span>
          <span class="badge-num">{{ item.label }}</span>
        </span>
        <div class="sticker-img">
          <img
            :src="imgUrl(item.path)"
            :alt="`收藏 ${item.label}`"
            loading="lazy"
            decoding="async"
          >
        </div>
        <footer class="sticker-foot">
          <div class="sticker-title">[ {{ item.label }} ]</div>
          <div class="sticker-sub">{{ item.sub || 'ACG · 收藏' }}</div>
        </footer>
      </article>
    </div>

    <Teleport to="body">
      <div v-if="lightboxIndex >= 0" class="sticker-lightbox" @click.self="closeLightbox">
        <button type="button" class="lb-close" aria-label="关闭" @click="closeLightbox">✕</button>
        <button type="button" class="lb-nav lb-prev" @click.stop="shiftLightbox(-1)">‹</button>
        <figure class="lb-figure">
          <img :src="imgUrl(items[lightboxIndex].path)" :alt="items[lightboxIndex].label">
          <figcaption>[ {{ items[lightboxIndex].label }} ] · {{ items[lightboxIndex].sub }}</figcaption>
        </figure>
        <button type="button" class="lb-nav lb-next" @click.stop="shiftLightbox(1)">›</button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { imgUrl } from '../data/profile'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const activeIndex = ref(-1)
const lightboxIndex = ref(-1)

function openLightbox(i) {
  lightboxIndex.value = i
  document.body.style.overflow = 'hidden'
}

function closeLightbox() {
  lightboxIndex.value = -1
  document.body.style.overflow = ''
}

function shiftLightbox(delta) {
  if (lightboxIndex.value < 0 || !props.items.length) return
  const n = props.items.length
  lightboxIndex.value = (lightboxIndex.value + delta + n) % n
}

function onKeydown(e) {
  if (lightboxIndex.value < 0) return
  if (e.key === 'Escape') closeLightbox()
  if (e.key === 'ArrowLeft') shiftLightbox(-1)
  if (e.key === 'ArrowRight') shiftLightbox(1)
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.sticker-wall {
  margin: 0 -0.5rem;
}

.sticker-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.sticker-card {
  position: relative;
  display: flex;
  flex-direction: column;
  aspect-ratio: 3 / 4.35;
  background: #121212;
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}

.sticker-card:hover,
.sticker-card.active {
  border-color: var(--orange);
  box-shadow: 0 0 0 1px var(--orange), 0 8px 24px rgba(232, 93, 4, 0.22);
  transform: translateY(-2px);
  z-index: 1;
}

.sticker-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15rem 0.4rem;
  background: rgba(0, 0, 0, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 4px;
  font-family: var(--mono);
  font-size: 0.55rem;
  color: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(4px);
}

.badge-icon {
  color: var(--orange);
  font-size: 0.45rem;
}

.sticker-img {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  background: #1a1a1a;
}

.sticker-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  filter: saturate(0.72) brightness(0.95);
  transition: filter 0.25s ease, transform 0.3s ease;
}

.sticker-card:hover .sticker-img img,
.sticker-card.active .sticker-img img {
  filter: saturate(1) brightness(1);
  transform: scale(1.03);
}

.sticker-foot {
  flex-shrink: 0;
  padding: 0.45rem 0.55rem 0.5rem;
  background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.sticker-title {
  font-family: var(--mono);
  font-size: 0.72rem;
  font-weight: 500;
  color: #f0f0f0;
  letter-spacing: 0.04em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sticker-sub {
  font-size: 0.62rem;
  color: rgba(255, 255, 255, 0.42);
  margin-top: 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

/* Lightbox */
.sticker-lightbox {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.lb-figure {
  max-width: min(420px, 90vw);
  max-height: 85vh;
  margin: 0;
  text-align: center;
}

.lb-figure img {
  max-width: 100%;
  max-height: calc(85vh - 3rem);
  object-fit: contain;
  border: 2px solid var(--orange);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
}

.lb-figure figcaption {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.75rem;
}

.lb-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
}

.lb-close:hover { border-color: var(--orange); color: var(--orange); }

.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.lb-prev { left: 1rem; }
.lb-next { right: 1rem; }
.lb-nav:hover { border-color: var(--orange); color: var(--orange); }

@media (max-width: 900px) {
  .sticker-grid { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: 680px) {
  .sticker-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
}

@media (max-width: 460px) {
  .sticker-grid { grid-template-columns: repeat(2, 1fr); }
  .sticker-card { aspect-ratio: 3 / 4.1; }
}
</style>

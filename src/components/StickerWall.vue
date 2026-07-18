<template>
  <div class="sticker-wall">
    <div class="sticker-masonry">
      <component
        :is="cardTag(item)"
        v-for="(item, index) in visibleItems"
        :key="itemKey(item, index)"
        :to="item.to || undefined"
        class="sticker-card"
        :class="[
          `sticker-card--${sizeClass(index)}`,
          {
            active: activeIndex === index,
            'sticker-card--tilt': canTilt && !item.to,
            'sticker-card--link': !!item.to,
          },
        ]"
        @mouseenter="activeIndex = index"
        @mouseleave="onCardLeave($event)"
        @mousemove="onCardMove"
        @click="onCardClick(item, index)"
      >
        <span class="sticker-badge">{{ item.label }}</span>
        <div v-if="item.path" class="sticker-img">
          <img
            :src="thumbUrl(item.path)"
            :alt="item.title || item.label"
            loading="lazy"
            decoding="async"
          >
        </div>
        <div v-else class="sticker-img sticker-img--empty" aria-hidden="true" />
        <footer class="sticker-foot">
          <div
            v-if="mode === 'gallery'"
            class="sticker-title"
          >
            [ {{ item.label }} ]
          </div>
          <template v-else>
            <div class="sticker-title sticker-title--forum">{{ item.title || item.label }}</div>
            <p v-if="item.subtitle" class="sticker-sub">{{ item.subtitle }}</p>
          </template>
        </footer>
      </component>
    </div>

    <div
      v-if="hasMore"
      ref="sentinelRef"
      class="sticker-more"
    >
      <button type="button" class="sticker-more-btn" @click="loadMore">
        加载更多（{{ visibleCount }}/{{ items.length }}）
      </button>
    </div>

    <Teleport v-if="mode === 'gallery'" to="body">
      <div v-if="lightboxIndex >= 0" class="sticker-lightbox" @click.self="closeLightbox">
        <button type="button" class="lb-close" aria-label="关闭" @click="closeLightbox">✕</button>
        <button type="button" class="lb-nav lb-prev" aria-label="上一张" @click.stop="shiftLightbox(-1)">‹</button>
        <figure class="lb-figure">
          <img :src="imgUrl(items[lightboxIndex].path)" :alt="items[lightboxIndex].label">
          <figcaption v-if="items[lightboxIndex].label">[ {{ items[lightboxIndex].label }} ]</figcaption>
        </figure>
        <button type="button" class="lb-nav lb-next" aria-label="下一张" @click.stop="shiftLightbox(1)">›</button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { imgUrl } from '../data/profile'
import { thumbUrl } from '../utils/thumbs.js'

const BATCH = 24

const props = defineProps({
  items: { type: Array, default: () => [] },
  /** gallery：关于页灯箱；forum：帖子链接 + 标题在底部 */
  mode: { type: String, default: 'gallery' },
})

const activeIndex = ref(-1)
const lightboxIndex = ref(-1)
const canTilt = ref(false)
const visibleCount = ref(BATCH)
const sentinelRef = ref(null)
let loadObserver = null

const visibleItems = computed(() => props.items.slice(0, visibleCount.value))
const hasMore = computed(() => visibleCount.value < props.items.length)

watch(
  () => props.items.length,
  () => {
    visibleCount.value = Math.min(BATCH, props.items.length || BATCH)
  },
)

function loadMore() {
  if (!hasMore.value) return
  visibleCount.value = Math.min(visibleCount.value + BATCH, props.items.length)
}

const TILT_MAX = 12

function cardTag(item) {
  if (item.to) return RouterLink
  return 'article'
}

function itemKey(item, index) {
  return item.to || item.path || item.label || index
}

function resetTilt(el) {
  if (!el) return
  el.style.setProperty('--tilt-x', '0deg')
  el.style.setProperty('--tilt-y', '0deg')
  el.style.setProperty('--shine-x', '50%')
  el.style.setProperty('--shine-y', '50%')
}

function onCardMove(e) {
  if (!canTilt.value) return
  const el = e.currentTarget
  const rect = el.getBoundingClientRect()
  const px = (e.clientX - rect.left) / rect.width
  const py = (e.clientY - rect.top) / rect.height
  const rx = (py - 0.5) * -TILT_MAX
  const ry = (px - 0.5) * TILT_MAX
  el.style.setProperty('--tilt-x', `${rx.toFixed(2)}deg`)
  el.style.setProperty('--tilt-y', `${ry.toFixed(2)}deg`)
  el.style.setProperty('--shine-x', `${(px * 100).toFixed(1)}%`)
  el.style.setProperty('--shine-y', `${(py * 100).toFixed(1)}%`)
}

function onCardLeave(e) {
  activeIndex.value = -1
  resetTilt(e.currentTarget)
}

function sizeClass(index) {
  const m = index % 5
  if (m === 0 || m === 3) return 'tall'
  if (m === 2) return 'short'
  return 'mid'
}

function onCardClick(item, index) {
  if (item.to || props.mode !== 'gallery') return
  openLightbox(index)
}

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

onMounted(() => {
  canTilt.value =
    !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    && window.matchMedia('(hover: hover)').matches
  window.addEventListener('keydown', onKeydown)

  if ('IntersectionObserver' in window) {
    loadObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) loadMore()
      },
      { rootMargin: '240px' },
    )
    // sentinel 可能稍后才挂载，用 nextTick + watch 更稳
    const tryObserve = () => {
      if (sentinelRef.value && loadObserver) loadObserver.observe(sentinelRef.value)
    }
    tryObserve()
    watch(sentinelRef, tryObserve)
  }
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
  loadObserver?.disconnect()
})
</script>

<style scoped>
a.sticker-card {
  text-decoration: none;
  color: inherit;
}

.sticker-masonry {
  columns: 5 148px;
  column-gap: 12px;
  perspective: 1100px;
}

.sticker-more {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  padding: 0.5rem 0 0.25rem;
}

.sticker-more-btn {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  background: transparent;
  border: 1px dashed var(--border);
  padding: 0.45rem 1rem;
  cursor: pointer;
}

.sticker-more-btn:hover {
  color: var(--text);
  border-color: var(--orange);
}

.sticker-card {
  --tilt-x: 0deg;
  --tilt-y: 0deg;
  --shine-x: 50%;
  --shine-y: 50%;
  --card-lift: 0px;
  position: relative;
  display: inline-block;
  width: 100%;
  margin-bottom: 12px;
  break-inside: avoid;
  background: var(--bg-paper);
  border: 1px solid var(--border);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%);
  overflow: hidden;
  cursor: pointer;
  transform-style: preserve-3d;
  transform:
    translateY(calc(-1 * var(--card-lift)))
    rotateX(var(--tilt-x))
    rotateY(var(--tilt-y));
  transition:
    transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    border-color 0.2s,
    box-shadow 0.2s;
  will-change: transform;
}

.sticker-card--link {
  cursor: pointer;
}

.sticker-card--tilt {
  transition:
    transform 0.1s ease-out,
    border-color 0.2s,
    box-shadow 0.2s;
}

.sticker-card::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
  background: radial-gradient(
    200px circle at var(--shine-x) var(--shine-y),
    rgba(255, 255, 255, 0.22),
    transparent 62%
  );
  opacity: 0;
  transition: opacity 0.25s;
}

[data-theme="dark"] .sticker-card::before {
  background: radial-gradient(
    200px circle at var(--shine-x) var(--shine-y),
    rgba(255, 255, 255, 0.1),
    transparent 62%
  );
}

.sticker-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  background: var(--orange);
  clip-path: polygon(100% 0, 0 100%, 100% 100%);
  pointer-events: none;
  opacity: 0.35;
  transition: opacity 0.2s;
}

.sticker-card:hover,
.sticker-card.active {
  --card-lift: 6px;
  border-color: var(--orange);
  box-shadow:
    0 8px 24px rgba(232, 93, 4, 0.14),
    0 2px 8px rgba(0, 0, 0, 0.08);
  z-index: 2;
}

.sticker-card:hover::before,
.sticker-card.active::before {
  opacity: 1;
}

.sticker-card:hover::after,
.sticker-card.active::after {
  opacity: 1;
}

.sticker-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  z-index: 2;
  padding: 0.12rem 0.35rem;
  background: var(--topbar-bg);
  border: 1px solid rgba(255, 255, 255, 0.12);
  font-family: var(--mono);
  font-size: 0.55rem;
  color: rgba(255, 255, 255, 0.8);
  letter-spacing: 0.04em;
}

.sticker-img {
  overflow: hidden;
  background: var(--bg);
  transform: translateZ(28px);
  transform-style: preserve-3d;
}

.sticker-img--empty {
  min-height: 88px;
  background: color-mix(in srgb, var(--orange) 8%, var(--bg));
}

.sticker-card--tall .sticker-img { max-height: 280px; }
.sticker-card--mid .sticker-img { max-height: 220px; }
.sticker-card--short .sticker-img { max-height: 165px; }

.sticker-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  display: block;
  filter: saturate(0.88);
  transform: translateZ(12px) scale(1);
  transition: filter 0.25s ease, transform 0.25s ease;
}

.sticker-card:hover .sticker-img img,
.sticker-card.active .sticker-img img {
  filter: saturate(1);
  transform: translateZ(12px) scale(1.04);
}

.sticker-foot {
  position: relative;
  z-index: 4;
  padding: 0.45rem 0.55rem 0.5rem;
  background: var(--bg-paper);
  border-top: 1px dashed var(--border);
  transform: translateZ(16px);
}

.sticker-title {
  font-family: var(--mono);
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--text);
  letter-spacing: 0.04em;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sticker-title--forum {
  white-space: normal;
  text-align: left;
  font-size: 0.72rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sticker-card--link:hover .sticker-title--forum,
.sticker-card--link.active .sticker-title--forum {
  color: var(--orange);
}

.sticker-sub {
  margin: 0.25rem 0 0;
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--orange);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Lightbox */
.sticker-lightbox {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.82);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.lb-figure {
  max-width: min(440px, 92vw);
  max-height: 85vh;
  margin: 0;
  text-align: center;
}

.lb-figure img {
  max-width: 100%;
  max-height: calc(85vh - 3rem);
  object-fit: contain;
  border: 2px solid var(--orange);
  background: var(--bg-paper);
}

.lb-figure figcaption {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.75);
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
  .sticker-masonry { columns: 4 140px; }
}

@media (max-width: 680px) {
  .sticker-masonry { columns: 3 130px; column-gap: 10px; }
  .sticker-card--tall .sticker-img { max-height: 240px; }
  .sticker-card--mid .sticker-img { max-height: 190px; }
  .sticker-card--short .sticker-img { max-height: 140px; }
}

@media (max-width: 460px) {
  .sticker-masonry { columns: 2 140px; }
}

@media (prefers-reduced-motion: reduce) {
  .sticker-masonry {
    perspective: none;
  }

  .sticker-card {
    transform: none;
    will-change: auto;
  }

  .sticker-card:hover,
  .sticker-card.active {
    --card-lift: 0px;
    transform: translateY(-2px);
  }

  .sticker-card::before {
    display: none;
  }

  .sticker-img,
  .sticker-foot,
  .sticker-img img {
    transform: none;
  }
}
</style>

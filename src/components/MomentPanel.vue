<template>
  <div class="panel moment-panel">
    <div class="panel-header">
      <span>此刻</span>
      <span class="moment-dots" aria-hidden="true">
        <span
          v-for="(_, i) in slides.length"
          :key="i"
          class="moment-dot"
          :class="{ active: i === activeIndex }"
        />
      </span>
    </div>
    <div class="panel-body">
      <Transition name="moment-fade" mode="out-in">
        <div :key="activeIndex" class="moment-slide">
          <span class="moment-label">{{ slides[activeIndex].label }}</span>
          <p class="moment-text">{{ slides[activeIndex].text }}</p>
          <router-link
            v-if="slides[activeIndex].link"
            :to="slides[activeIndex].link"
            class="moment-link"
          >{{ slides[activeIndex].linkLabel }} →</router-link>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMusicStore } from '../store'
import { profile } from '../data/profile'

const props = defineProps({
  totalPosts: { type: [Number, String], default: 0 },
  siteAge: { type: String, default: '—' },
})

const musicStore = useMusicStore()
const activeIndex = ref(0)
let timer = null

const watchingLine = computed(() => {
  const fav = profile.favorites?.find(f => f.label === '最近在看')
  return fav?.text || profile.acgTags.slice(0, 3).join(' · ')
})

const slides = computed(() => [
  {
    label: 'LISTEN',
    text: musicStore.currentSong
      ? `${musicStore.isPlaying ? '▶' : '❚❚'} ${musicStore.currentSong.title}`
      : '暂无播放 — 去音乐室选一首',
    link: '/music',
    linkLabel: '音乐室',
  },
  {
    label: 'WATCH',
    text: watchingLine.value,
    link: '/about',
    linkLabel: '关于',
  },
  {
    label: 'STATUS',
    text: `${props.totalPosts} 篇笔记 · ${props.siteAge} online · CYINC.LOG`,
    link: '/archive',
    linkLabel: '归档',
  },
])

function startRotation() {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduceMotion) return
  timer = setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % slides.value.length
  }, 4500)
}

onMounted(startRotation)
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.moment-panel .panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.moment-dots {
  display: flex;
  gap: 0.25rem;
}

.moment-dot {
  width: 4px;
  height: 4px;
  background: var(--border);
  transition: background 0.2s;
}

.moment-dot.active {
  background: var(--orange);
}

.moment-slide {
  min-height: 3.5rem;
}

.moment-label {
  display: block;
  font-family: var(--mono);
  font-size: 0.52rem;
  letter-spacing: 0.14em;
  color: var(--orange);
  margin-bottom: 0.35rem;
}

.moment-text {
  font-size: 0.78rem;
  line-height: 1.45;
  margin: 0 0 0.55rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.moment-link {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--steel);
  text-decoration: none;
}

.moment-link:hover {
  color: var(--orange);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.moment-fade-enter-active,
.moment-fade-leave-active {
  transition: opacity 0.25s ease;
}

.moment-fade-enter-from,
.moment-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .moment-fade-enter-active,
  .moment-fade-leave-active {
    transition: none;
  }
}
</style>

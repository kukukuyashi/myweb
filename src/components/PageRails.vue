<template>
  <div class="page-rails" aria-hidden="true">
    <aside class="page-rail page-rail--left">
      <div class="rail-block">
        <span class="rail-label">DOC</span>
        <span class="rail-value">CYINC.LOG</span>
      </div>
      <div class="rail-block">
        <span class="rail-label">NOW</span>
        <div
          class="rail-now-wrap"
          :class="{ 'rail-now-wrap--scroll': scrollNowPlaying }"
        >
          <span class="rail-now-track">{{ nowPlayingFull }}</span>
        </div>
      </div>
      <div class="rail-block">
        <span class="rail-label">REV</span>
        <span class="rail-value">{{ buildRev }}</span>
      </div>
      <div class="rail-ticks" />
      <p class="rail-vertical">{{ railTagline }}</p>
    </aside>

    <aside class="page-rail page-rail--right">
      <div class="rail-block rail-block--right">
        <span class="rail-label">POSTS</span>
        <span class="rail-value rail-num">{{ totalPosts }}</span>
      </div>
      <div class="rail-block rail-block--right">
        <span class="rail-label">RECENT</span>
        <nav class="rail-recent">
          <router-link
            v-for="post in recentPosts"
            :key="post.id"
            :to="post.url"
            :title="post.title"
          >{{ post.date.slice(5) }} · {{ truncate(post.title, 12) }}</router-link>
        </nav>
      </div>
      <div class="rail-block rail-block--right">
        <span class="rail-label">VISIT</span>
        <div class="rail-visit">
          <span>TODAY {{ visitorToday }}</span>
          <span>TTL {{ visitorTotal }}</span>
        </div>
      </div>
      <nav class="rail-nav">
        <router-link v-for="link in quickLinks" :key="link.to" :to="link.to">{{ link.label }}</router-link>
      </nav>
      <ul class="rail-tags">
        <li v-for="t in fanTags" :key="t">
          <router-link :to="{ path: '/', query: { tag: t } }">{{ t }}</router-link>
        </li>
      </ul>
      <div class="rail-ticks rail-ticks--flip" />
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { posts, getRecentPosts } from '../data/posts'
import { useMusicStore } from '../store'
import { getSeasonConfig } from '../data/seasonTheme'

const musicStore = useMusicStore()
const totalPosts = posts.length
const buildRev = '2026.06'
const recentPosts = getRecentPosts(3)
const railTagline = getSeasonConfig().railTagline

const visitorToday = ref(0)
const visitorTotal = ref(0)

const nowPlayingFull = computed(() => {
  if (!musicStore.currentSong) return '— idle —'
  return musicStore.isPlaying
    ? `▶ ${musicStore.currentSong.title}`
    : `❚❚ ${musicStore.currentSong.title}`
})

const scrollNowPlaying = computed(() =>
  musicStore.currentSong && nowPlayingFull.value.length > 16
)

const quickLinks = [
  { to: '/music', label: 'MUSIC' },
  { to: '/archive', label: 'ARCH' },
  { to: '/guestbook', label: 'GUEST' },
  { to: '/about', label: 'ABOUT' },
]

const fanTags = ['フリーレン', 'MyGO!!!!!', 'BA']

function truncate(text, max) {
  const s = String(text || '')
  return s.length > max ? `${s.slice(0, max)}…` : s
}

function loadVisitorStats() {
  try {
    const data = JSON.parse(localStorage.getItem('cyincVisitorStats') || '{}')
    const day = new Date().toISOString().slice(0, 10)
    visitorToday.value = data[day] || 0
    visitorTotal.value = data.total || 0
  } catch {
    visitorToday.value = 0
    visitorTotal.value = 0
  }
}

onMounted(loadVisitorStats)
</script>

<style scoped>
.page-rails {
  pointer-events: none;
}

.page-rail {
  position: fixed;
  top: calc(var(--topbar-height) + 1.5rem);
  bottom: 5.5rem;
  width: clamp(72px, calc((100vw - var(--content-width)) / 2 - 0.75rem), 140px);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
  z-index: 0;
  opacity: 0.72;
}

.page-rail--left {
  left: max(0.35rem, calc((100vw - var(--content-width)) / 2 - clamp(72px, calc((100vw - var(--content-width)) / 2 - 0.75rem), 140px) - 0.25rem));
}

.page-rail--right {
  right: max(0.35rem, calc((100vw - var(--content-width)) / 2 - clamp(72px, calc((100vw - var(--content-width)) / 2 - 0.75rem), 140px) - 0.25rem));
  align-items: flex-end;
  text-align: right;
}

.rail-block {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding-bottom: 0.65rem;
  border-bottom: 1px dashed var(--border);
  width: 100%;
}

.rail-block--right {
  align-items: flex-end;
}

.rail-label {
  letter-spacing: 0.14em;
  color: var(--orange);
  font-size: 0.52rem;
}

.rail-value {
  letter-spacing: 0.06em;
  line-height: 1.3;
}

.rail-now-wrap {
  overflow: hidden;
  width: 100%;
  max-width: 100%;
}

.rail-now-track {
  display: inline-block;
  font-size: 0.55rem;
  line-height: 1.35;
  white-space: nowrap;
}

.rail-now-wrap--scroll .rail-now-track {
  padding-left: 100%;
  animation: rail-now-scroll 12s linear infinite;
}

@keyframes rail-now-scroll {
  from { transform: translateX(0); }
  to { transform: translateX(-100%); }
}

.rail-visit {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.52rem;
  letter-spacing: 0.06em;
  color: var(--steel);
}

.rail-num {
  font-size: 1.1rem;
  color: var(--steel);
  font-weight: 500;
}

.rail-recent {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
  pointer-events: auto;
}

.rail-recent a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.52rem;
  line-height: 1.35;
  transition: color 0.15s;
}

.rail-recent a:hover {
  color: var(--orange);
}

.rail-ticks {
  flex: 1;
  min-height: 2rem;
  width: 100%;
  border-left: 1px solid var(--border);
  margin-left: 0.35rem;
  background: repeating-linear-gradient(
    to bottom,
    var(--border) 0,
    var(--border) 1px,
    transparent 1px,
    transparent 12px
  );
  opacity: 0.55;
}

.rail-ticks--flip {
  border-left: none;
  border-right: 1px solid var(--border);
  margin-left: 0;
  margin-right: 0.35rem;
}

.rail-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  letter-spacing: 0.18em;
  font-size: 0.52rem;
  opacity: 0.45;
  align-self: center;
  margin-top: auto;
}

.rail-nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  width: 100%;
  pointer-events: auto;
}

.rail-nav a {
  color: var(--text-muted);
  text-decoration: none;
  letter-spacing: 0.1em;
  padding: 0.2rem 0;
  border-bottom: 1px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.rail-nav a:hover,
.rail-nav a.router-link-active {
  color: var(--orange);
  border-bottom-color: var(--orange);
}

.rail-tags {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: auto;
  width: 100%;
  pointer-events: auto;
}

.rail-tags li {
  border: 1px solid var(--border);
  background: rgba(245, 242, 238, 0.5);
  font-size: 0.52rem;
  letter-spacing: 0.04em;
  transition: border-color 0.15s, background 0.15s;
}

.rail-tags li:hover {
  border-color: var(--orange);
}

.rail-tags a {
  display: block;
  padding: 0.15rem 0.35rem;
  color: inherit;
  text-decoration: none;
}

.rail-tags a:hover {
  color: var(--orange);
}

[data-theme="dark"] .rail-tags li {
  background: rgba(36, 34, 32, 0.6);
}

@media (max-width: 1440px) {
  .page-rails {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .rail-now-wrap--scroll .rail-now-track {
    animation: none;
    padding-left: 0;
    white-space: normal;
    word-break: break-word;
  }
}
</style>

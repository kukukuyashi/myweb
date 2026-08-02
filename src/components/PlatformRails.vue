<template>
  <div class="platform-rails" aria-hidden="true">
    <aside class="platform-rail platform-rail--left">
      <div class="rail-block">
        <span class="rail-label">SYS</span>
        <span class="rail-value">CYINC.APP</span>
      </div>
      <div class="rail-block">
        <span class="rail-label">MODE</span>
        <span class="rail-value">PLATFORM</span>
      </div>
      <div class="rail-block">
        <span class="rail-label">UP</span>
        <span class="rail-value rail-num">{{ siteDays }}D</span>
      </div>
      <div class="rail-block rail-block--interactive">
        <SidebarMusicPanel
          variant="rail"
          :show-progress="false"
          :show-volume="false"
        />
      </div>
      <div class="rail-block rail-block--interactive">
        <StudyRoomPomoCard />
      </div>
      <div class="rail-ticks" />
      <p class="rail-vertical">FORUM · POMO · GUEST</p>
    </aside>

    <aside class="platform-rail platform-rail--right">
      <div class="rail-block rail-block--right">
        <span class="rail-label">TIME</span>
        <span class="rail-value rail-clock">{{ clockText }}</span>
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
        <li v-for="t in acgTags" :key="t">
          <span>{{ t }}</span>
        </li>
      </ul>
      <div class="rail-ticks rail-ticks--flip" />
    </aside>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { profile } from '../data/profile'
import { platformLaunchDate } from '../data/platformBaGallery.js'
import SidebarMusicPanel from './SidebarMusicPanel.vue'
import StudyRoomPomoCard from './StudyRoomPomoCard.vue'

const clockText = ref('')
const visitorToday = ref(0)
const visitorTotal = ref(0)
const siteDays = ref(0)
let clockTimer = null

const acgTags = profile.acgTags.slice(0, 4)

const quickLinks = [
  { to: '/app', label: 'HOME' },
  { to: '/app/pomo', label: 'POMO' },
  { to: '/app/music', label: 'MUSIC' },
  { to: '/app/forum', label: 'FORUM' },
  { to: '/app/me', label: 'ME' },
  { to: '/', label: 'BLOG' },
]

function updateClock() {
  clockText.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
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

function calcSiteDays() {
  const start = new Date(platformLaunchDate)
  const diff = Math.floor((Date.now() - start) / 86400000)
  siteDays.value = diff > 0 ? diff : 0
}

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  loadVisitorStats()
  calcSiteDays()
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
})
</script>

<style scoped>
.platform-rails {
  pointer-events: none;
}

.platform-rail {
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

.platform-rail--left {
  left: max(0.35rem, calc((100vw - var(--content-width)) / 2 - clamp(72px, calc((100vw - var(--content-width)) / 2 - 0.75rem), 140px) - 0.25rem));
}

.platform-rail--right {
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

.rail-block--interactive {
  pointer-events: auto;
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

.rail-num {
  font-size: 1.1rem;
  color: var(--steel);
  font-weight: 500;
}

.rail-clock {
  font-variant-numeric: tabular-nums;
  font-size: 0.68rem;
  color: var(--steel);
}

.rail-visit {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.52rem;
  letter-spacing: 0.06em;
  color: var(--steel);
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
}

.rail-tags li {
  border: 1px solid var(--border);
  background: rgba(245, 242, 238, 0.5);
  font-size: 0.52rem;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.35rem;
}

[data-theme="dark"] .rail-tags li {
  background: rgba(36, 34, 32, 0.6);
}

@media (max-width: 1440px) {
  .platform-rails {
    display: none;
  }
}
</style>

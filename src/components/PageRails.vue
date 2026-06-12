<template>
  <div class="page-rails" aria-hidden="true">
    <aside class="page-rail page-rail--left">
      <div class="rail-block">
        <span class="rail-label">DOC</span>
        <span class="rail-value">CYINC.LOG</span>
      </div>
      <div class="rail-block">
        <span class="rail-label">REV</span>
        <span class="rail-value">{{ buildRev }}</span>
      </div>
      <div class="rail-block">
        <span class="rail-label">GRID</span>
        <span class="rail-value">24×24</span>
      </div>
      <div class="rail-ticks" />
      <p class="rail-vertical">LEARNING · AGENT · ACG</p>
    </aside>

    <aside class="page-rail page-rail--right">
      <div class="rail-block rail-block--right">
        <span class="rail-label">POSTS</span>
        <span class="rail-value rail-num">{{ totalPosts }}</span>
      </div>
      <div class="rail-block rail-block--right">
        <span class="rail-label">TAGS</span>
        <span class="rail-value rail-num">{{ totalTags }}</span>
      </div>
      <nav class="rail-nav">
        <router-link v-for="link in quickLinks" :key="link.to" :to="link.to">{{ link.label }}</router-link>
      </nav>
      <ul class="rail-tags">
        <li v-for="t in fanTags" :key="t">{{ t }}</li>
      </ul>
      <div class="rail-ticks rail-ticks--flip" />
    </aside>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { posts, getTags } from '../data/posts'

const totalPosts = posts.length
const totalTags = getTags().length
const buildRev = '2026.06'

const quickLinks = [
  { to: '/music', label: 'MUSIC' },
  { to: '/archive', label: 'ARCH' },
  { to: '/guestbook', label: 'GUEST' },
  { to: '/about', label: 'ABOUT' },
]

const fanTags = ['フリーレン', 'MyGO!!!!!', 'BA']
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

.rail-num {
  font-size: 1.1rem;
  color: var(--steel);
  font-weight: 500;
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
  padding: 0.15rem 0.35rem;
  border: 1px solid var(--border);
  background: rgba(245, 242, 238, 0.5);
  font-size: 0.52rem;
  letter-spacing: 0.04em;
}

[data-theme="dark"] .rail-tags li {
  background: rgba(36, 34, 32, 0.6);
}

@media (max-width: 1440px) {
  .page-rails {
    display: none;
  }
}
</style>

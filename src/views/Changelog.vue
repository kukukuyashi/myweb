<template>
  <div ref="pageRef" class="changelog-page">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <header class="changelog-header">
            <p class="page-ink-coord">CHANGELOG · SITE · <span class="ink-hint">演化记录</span></p>
            <h1 class="page-title">更新日志</h1>
            <p class="changelog-lead">
              记录 <strong>CYINC.LOG 站点本身</strong> 的功能演化 — 不是文章目录。详细实现见对应笔记。
            </p>
            <p v-if="latest" class="changelog-latest">
              最新 · {{ latest.version }} · {{ latest.date }} — {{ latest.title }}
            </p>
          </header>

          <ol class="changelog-list">
            <li
              v-for="entry in entries"
              :key="entry.version + entry.date"
              class="changelog-entry reveal-item"
              data-reveal
            >
              <div class="changelog-entry-head">
                <time :datetime="entry.date">{{ entry.date }}</time>
                <span class="changelog-version">{{ entry.version }}</span>
              </div>
              <h2 class="changelog-entry-title">{{ entry.title }}</h2>
              <p class="changelog-entry-summary">{{ entry.summary }}</p>
              <ul v-if="entry.items?.length" class="changelog-entry-items">
                <li v-for="item in entry.items" :key="item">{{ item }}</li>
              </ul>
              <router-link v-if="entry.postId" :to="postLink(entry.postId)" class="changelog-entry-link">
                读相关笔记 →
              </router-link>
            </li>
          </ol>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, nextTick } from 'vue'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { usePageMeta } from '../composables/usePageMeta'
import { useRevealOnScroll, observeReveal } from '../composables/useRevealOnScroll'
import { getChangelogSorted } from '../data/changelog'
import { postUrl } from '../data/posts'

usePageMeta({
  title: '更新日志',
  description: 'CYINC.LOG 站点功能演化记录：重构、音乐室、墨染、SEO 等。',
})

const pageRef = ref(null)
useRevealOnScroll(pageRef)

const entries = getChangelogSorted()
const latest = computed(() => entries[0])

function postLink(id) {
  return postUrl(id)
}

onMounted(() => {
  nextTick(() => observeReveal(pageRef.value))
})
</script>

<style scoped>
.changelog-header {
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px dashed var(--border);
}

.changelog-lead {
  margin-top: 0.75rem;
  max-width: 40rem;
  color: var(--text-muted);
  line-height: 1.55;
}

.changelog-latest {
  margin-top: 0.85rem;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--orange);
  letter-spacing: 0.04em;
}

.changelog-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border-left: 2px solid var(--border);
}

.changelog-entry {
  position: relative;
  padding: 0 0 1.75rem 1.35rem;
}

.changelog-entry::before {
  content: '';
  position: absolute;
  left: -5px;
  top: 0.35rem;
  width: 8px;
  height: 8px;
  background: var(--orange);
  box-shadow: 0 0 0 3px var(--bg);
}

.changelog-entry-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  margin-bottom: 0.35rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
}

.changelog-version {
  color: var(--steel);
}

.changelog-entry-title {
  font-size: 1.05rem;
  margin: 0 0 0.35rem;
  line-height: 1.35;
}

.changelog-entry-summary {
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0 0 0.55rem;
}

.changelog-entry-items {
  margin: 0 0 0.65rem;
  padding-left: 1.1rem;
  font-size: 0.82rem;
  color: var(--text);
  line-height: 1.45;
}

.changelog-entry-items li {
  margin-bottom: 0.2rem;
}

.changelog-entry-link {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--steel);
  text-decoration: none;
}

.changelog-entry-link:hover {
  color: var(--orange);
  text-decoration: underline;
  text-underline-offset: 2px;
}
</style>

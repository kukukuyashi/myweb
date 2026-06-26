<template>
  <div class="archive">
    <NavBar />
    <main class="page-main">
      <div class="container archive-wrap">
        <header class="archive-header">
          <h1 class="page-title">文章归档</h1>
          <div class="archive-meta">
            TOTAL {{ totalPosts }} POSTS · {{ totalTags }} TAGS · LAST UPDATE {{ lastUpdate }}
          </div>
        </header>

        <div class="archive-columns">
          <section ref="streamRef" class="archive-main" aria-label="文章时间轴">
            <div v-if="activeCategory" class="archive-filter-hint">
              正在查看「{{ activeCategory }}」·
              <button type="button" class="archive-filter-clear" @click="activeCategory = ''">显示全部</button>
            </div>

            <template v-for="(entry, index) in timelineEntries" :key="entry.key">
              <div v-if="entry.kind === 'year'" class="archive-stream-year">
                <span class="archive-stream-year-dot" aria-hidden="true" />
                <span class="archive-stream-year-label">{{ entry.year }}</span>
              </div>

              <article
                v-else
                class="archive-stream-item reveal-item"
                data-reveal
                :style="{ '--reveal-delay': `${Math.min(index, 8) * 40}ms` }"
              >
                <span class="archive-stream-dot" aria-hidden="true" />
                <div class="archive-stream-card">
                  <time class="archive-stream-date" :datetime="entry.post.date">
                    {{ formatTimelineDate(entry.post.date) }}
                  </time>
                  <h2 class="archive-stream-title">
                    <router-link :to="entry.post.url">{{ entry.post.title }}</router-link>
                  </h2>
                  <p v-if="entry.post.excerpt" class="archive-stream-excerpt">
                    {{ entry.post.excerpt }}
                  </p>
                  <div class="archive-stream-foot">
                    <button
                      type="button"
                      class="archive-stream-cat"
                      :style="{ '--cat-color': getCategoryColor(entry.post.category) }"
                      @click="activeCategory = entry.post.category"
                    >
                      {{ entry.post.category }}
                    </button>
                    <span v-if="entry.post.tags?.length" class="archive-stream-tags">
                      <router-link
                        v-for="t in entry.post.tags.slice(0, 3)"
                        :key="t"
                        :to="tagUrl(t)"
                        class="archive-stream-tag"
                      >#{{ t }}</router-link>
                    </span>
                  </div>
                </div>
              </article>
            </template>

            <p v-if="!timelineEntries.some((e) => e.kind === 'post')" class="archive-empty">
              该分类暂无文章
            </p>
          </section>

          <aside class="archive-aside" aria-label="笔记分类">
            <div class="archive-panel archive-type-panel">
              <div class="archive-panel-head">
                <span class="archive-panel-label">笔记类型</span>
                <span class="archive-panel-count">{{ categoryStats.length }}</span>
              </div>
              <ul class="archive-type-list">
                <li>
                  <button
                    type="button"
                    class="archive-type-item"
                    :class="{ active: !activeCategory }"
                    @click="activeCategory = ''"
                  >
                    <span class="archive-type-icon archive-type-icon--all">ALL</span>
                    <span class="archive-type-body">
                      <span class="archive-type-name">全部笔记</span>
                      <span class="archive-type-desc">按时间浏览</span>
                    </span>
                    <span class="archive-type-badge">{{ totalPosts }}</span>
                  </button>
                </li>
                <li v-for="cat in categoryStats" :key="cat.name">
                  <button
                    type="button"
                    class="archive-type-item"
                    :class="{ active: activeCategory === cat.name }"
                    :style="{ '--cat-color': cat.color }"
                    @click="toggleCategory(cat.name)"
                  >
                    <span class="archive-type-icon">{{ cat.icon }}</span>
                    <span class="archive-type-body">
                      <span class="archive-type-name">{{ cat.name }}</span>
                      <span class="archive-type-desc">{{ categoryDesc(cat.name) }}</span>
                    </span>
                    <span class="archive-type-badge">{{ cat.count }}</span>
                  </button>
                </li>
              </ul>
            </div>

            <div class="archive-panel archive-tag-panel">
              <div class="archive-panel-head">
                <span class="archive-panel-label">热门标签</span>
                <span class="archive-panel-count">{{ allTags.length }}</span>
              </div>
              <div class="archive-tag-cloud">
                <router-link
                  v-for="item in topTags"
                  :key="item.tag"
                  :to="tagUrl(item.tag)"
                  class="archive-tag-chip"
                >
                  #{{ item.tag }}
                  <span class="archive-tag-chip-count">{{ item.count }}</span>
                </router-link>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { ref, computed } from 'vue'
import {
  getPostsSorted,
  getLastUpdateDate,
  getTags,
  getTagStats,
  getCategories,
  getCategoryColor,
  getCategoryIcon,
  tagUrl,
  postUrl,
} from '../data/posts'
import { usePageMeta } from '../composables/usePageMeta'
import { useRevealOnScroll } from '../composables/useRevealOnScroll'

usePageMeta({ title: '归档', description: '按时间轴浏览全部技术学习笔记。' })

const streamRef = ref(null)
const activeCategory = ref('')
useRevealOnScroll(streamRef, '[data-reveal]')

const totalPosts = computed(() => getPostsSorted().length)
const totalTags = computed(() => getTags().length)
const allTags = computed(() => getTags())
const lastUpdate = computed(() => getLastUpdateDate())
const topTags = computed(() => getTagStats().slice(0, 18))

const categoryStats = computed(() => {
  const counts = new Map()
  for (const post of getPostsSorted()) {
    counts.set(post.category, (counts.get(post.category) || 0) + 1)
  }

  return getCategories()
    .map((name) => ({
      name,
      count: counts.get(name) || 0,
      color: getCategoryColor(name),
      icon: getCategoryIcon(name),
    }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh-CN'))
})

const filteredPosts = computed(() => {
  const sorted = getPostsSorted().map((post) => ({
    ...post,
    url: postUrl(post.id),
  }))
  if (!activeCategory.value) return sorted
  return sorted.filter((post) => post.category === activeCategory.value)
})

const timelineEntries = computed(() => {
  const entries = []
  let lastYear = ''

  for (const post of filteredPosts.value) {
    const year = post.date.slice(0, 4)
    if (year !== lastYear) {
      entries.push({ kind: 'year', year, key: `year-${year}` })
      lastYear = year
    }
    entries.push({ kind: 'post', post, key: `post-${post.id}` })
  }

  return entries
})

const CATEGORY_DESC = {
  前端: 'Vue / CSS / 交互',
  Java: '语法与 JVM 笔记',
  Agent: 'LLM / MCP / Skill',
  部署: 'CI/CD / 静态站',
  项目: '实战与复盘',
  学习: '踩坑与记录',
  技术: '通用技术笔记',
  小知识: '零碎知识点',
}

function categoryDesc(name) {
  return CATEGORY_DESC[name] || '技术笔记'
}

function toggleCategory(name) {
  activeCategory.value = activeCategory.value === name ? '' : name
}

function formatTimelineDate(date) {
  const [y, m, d] = date.split('-')
  return `${y}.${m}.${d}`
}
</script>

<style scoped>
.archive-wrap {
  position: relative;
  z-index: 1;
}

.archive-header {
  margin-bottom: 1.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed var(--border);
}

.archive-header .page-title {
  margin-bottom: 0.65rem;
  padding-bottom: 0;
  border-bottom: none;
}

.archive-meta {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
}

.archive-columns {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 300px);
  gap: clamp(1.25rem, 2.5vw, 2rem);
  align-items: start;
}

.archive-main {
  min-width: 0;
}

.archive-filter-hint {
  margin-bottom: 1rem;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

.archive-filter-clear {
  font: inherit;
  color: var(--orange);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.archive-empty {
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--text-muted);
  padding: 2rem 0;
}

/* 右侧分类栏 */
.archive-aside {
  position: sticky;
  top: calc(var(--topbar-height) + 1.25rem);
  display: grid;
  gap: 1rem;
}

.archive-panel {
  background: var(--bg-paper);
  border: 1px solid var(--border);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%);
}

.archive-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.55rem 0.85rem;
  background: var(--topbar-bg);
  color: #fff;
}

[data-theme="dark"] .archive-panel-head {
  background: #0d0d0d;
}

.archive-panel-label {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.archive-panel-count {
  font-family: var(--mono);
  font-size: 0.58rem;
  color: rgba(255, 255, 255, 0.55);
}

.archive-type-list {
  list-style: none;
  margin: 0;
  padding: 0.45rem;
  display: grid;
  gap: 0.35rem;
}

.archive-type-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.65rem;
  width: 100%;
  padding: 0.65rem 0.7rem;
  border: 1px solid transparent;
  border-left: 3px solid var(--cat-color, var(--border));
  background: color-mix(in srgb, var(--bg) 70%, transparent);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s, transform 0.15s;
}

.archive-type-item:hover,
.archive-type-item.active {
  border-color: color-mix(in srgb, var(--cat-color, var(--orange)) 35%, var(--border));
  background: color-mix(in srgb, var(--cat-color, var(--orange)) 6%, var(--bg-paper));
}

.archive-type-item.active {
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--cat-color, var(--orange)) 18%, transparent);
}

.archive-type-icon {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  font-family: var(--mono);
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--cat-color, var(--steel));
  border: 1px solid color-mix(in srgb, var(--cat-color, var(--border)) 40%, var(--border));
  background: var(--bg-paper);
}

.archive-type-icon--all {
  color: var(--orange);
  border-color: color-mix(in srgb, var(--orange) 35%, var(--border));
}

.archive-type-body {
  min-width: 0;
}

.archive-type-name {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.3;
}

.archive-type-desc {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.68rem;
  color: var(--text-muted);
  line-height: 1.35;
}

.archive-type-badge {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  padding: 0.12rem 0.4rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
}

.archive-type-item.active .archive-type-badge {
  color: var(--cat-color, var(--orange));
  border-color: color-mix(in srgb, var(--cat-color, var(--orange)) 35%, var(--border));
}

.archive-tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.75rem;
}

.archive-tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--steel);
  text-decoration: none;
  padding: 0.18rem 0.42rem;
  border: 1px solid var(--border);
  background: var(--bg);
  transition: color 0.15s, border-color 0.15s;
}

.archive-tag-chip:hover {
  color: var(--orange);
  border-color: var(--orange);
}

.archive-tag-chip-count {
  color: var(--text-muted);
  font-size: 0.52rem;
}

/* 时间轴 */
.archive-stream {
  position: relative;
  margin-top: 0.15rem;
  padding-left: 2.35rem;
}

.archive-stream-year {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin: 0.25rem 0 1rem;
  padding-left: 0.15rem;
}

.archive-stream-year:first-child {
  margin-top: 0;
}

.archive-stream-year-dot {
  position: absolute;
  left: -2.35rem;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  margin-left: 0.48rem;
  border-radius: 50%;
  border: 2px solid var(--orange);
  background: var(--bg-paper);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--orange) 12%, transparent);
}

.archive-stream-year-label {
  font-family: var(--mono);
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--orange);
}

.archive-main {
  position: relative;
  padding-left: 2.35rem;
}

.archive-main::before {
  content: '';
  position: absolute;
  left: 0.55rem;
  top: 0.35rem;
  bottom: 0.35rem;
  width: 2px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--steel) 18%, transparent),
    color-mix(in srgb, var(--steel) 42%, var(--border)),
    color-mix(in srgb, var(--steel) 18%, transparent)
  );
  border-radius: 999px;
}

.archive-stream-item {
  position: relative;
  display: grid;
  grid-template-columns: 1fr;
  margin-bottom: 1.25rem;
}

.archive-stream-item:last-child {
  margin-bottom: 0;
}

.archive-stream-dot {
  position: absolute;
  left: -2.35rem;
  top: 1.35rem;
  width: 12px;
  height: 12px;
  margin-left: 0.52rem;
  border-radius: 50%;
  border: 2px solid color-mix(in srgb, var(--steel) 70%, var(--border));
  background: var(--bg-paper);
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.archive-stream-item:hover .archive-stream-dot,
.archive-stream-item:focus-within .archive-stream-dot {
  border-color: var(--orange);
  transform: scale(1.08);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--orange) 10%, transparent);
}

.archive-stream-card {
  padding: 0.95rem 1.05rem 1rem;
  border-radius: 12px;
  background: linear-gradient(
    165deg,
    color-mix(in srgb, var(--bg-paper) 92%, #fff) 0%,
    color-mix(in srgb, var(--steel) 8%, var(--bg-paper)) 52%,
    color-mix(in srgb, var(--steel) 14%, var(--bg-paper)) 100%
  );
  border: 1px solid color-mix(in srgb, var(--steel) 16%, var(--border));
  box-shadow:
    0 10px 24px rgba(26, 26, 26, 0.05),
    0 1px 0 rgba(255, 255, 255, 0.45) inset;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

[data-theme="dark"] .archive-stream-card {
  background: linear-gradient(
    165deg,
    color-mix(in srgb, var(--bg-paper) 88%, #fff) 0%,
    color-mix(in srgb, var(--steel) 12%, var(--bg-paper)) 100%
  );
  box-shadow:
    0 12px 28px rgba(0, 0, 0, 0.22),
    0 1px 0 rgba(255, 255, 255, 0.04) inset;
}

.archive-stream-item:hover .archive-stream-card,
.archive-stream-item:focus-within .archive-stream-card {
  transform: translateX(4px);
  border-color: color-mix(in srgb, var(--orange) 28%, var(--border));
}

.archive-stream-date {
  display: block;
  font-family: var(--mono);
  font-size: 0.76rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: color-mix(in srgb, var(--steel) 82%, var(--text));
  margin-bottom: 0.4rem;
}

.archive-stream-title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.45;
}

.archive-stream-title a {
  color: var(--text);
  text-decoration: none;
}

.archive-stream-title a:hover {
  color: var(--orange);
}

.archive-stream-excerpt {
  margin: 0 0 0.65rem;
  font-size: 0.86rem;
  line-height: 1.6;
  color: var(--text-muted);
}

.archive-stream-foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px dashed color-mix(in srgb, var(--border) 80%, transparent);
}

.archive-stream-cat {
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--cat-color, var(--steel));
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.archive-stream-cat:hover {
  text-decoration: underline;
}

.archive-stream-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.archive-stream-tag {
  font-family: var(--mono);
  font-size: 0.56rem;
  color: var(--text-muted);
  text-decoration: none;
}

.archive-stream-tag:hover {
  color: var(--orange);
}

@media (max-width: 960px) {
  .archive-columns {
    grid-template-columns: 1fr;
  }

  .archive-aside {
    position: static;
    order: -1;
  }

  .archive-type-list {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}

@media (max-width: 640px) {
  .archive-main {
    padding-left: 1.85rem;
  }

  .archive-main::before {
    left: 0.35rem;
  }

  .archive-stream-dot,
  .archive-stream-year-dot {
    margin-left: 0.28rem;
  }

  .archive-stream-dot {
    left: -1.85rem;
    top: 1.2rem;
  }

  .archive-stream-year-dot {
    left: -1.85rem;
  }

  .archive-type-list {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .archive-stream-card,
  .archive-stream-dot,
  .archive-type-item {
    transition: none;
  }

  .archive-stream-item:hover .archive-stream-card,
  .archive-stream-item:focus-within .archive-stream-card {
    transform: none;
  }
}
</style>

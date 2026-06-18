<template>
  <div class="archive">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <h1 class="page-title">文章归档</h1>
          <div class="archive-meta">
            TOTAL {{ totalPosts }} POSTS · {{ totalTags }} TAGS · LAST UPDATE {{ lastUpdate }}
          </div>

          <div v-if="allTags.length" class="archive-tags">
            <router-link
              v-for="tag in allTags"
              :key="tag"
              :to="tagUrl(tag)"
              class="archive-tag"
            >#{{ tag }}</router-link>
          </div>

          <InkRevealPanel
            v-if="timelineYears.length"
            tag="section"
            root-class="archive-timeline archive-timeline--ink"
            :image="ARCHIVE_INK_IMAGE"
            :position="ARCHIVE_INK_POSITION"
            :r-end="108"
            :max-stamps="110"
            fade-direction="left"
            aria-label="归档时间轴"
            @mouseleave="clearHoverMonth"
          >
            <div class="timeline-head">
              <span class="timeline-head-label">
                TIMELINE · <span class="ink-hint">hover 晕染</span>
              </span>
              <button v-if="monthFilter" type="button" class="timeline-clear" @click="monthFilter = ''">
                清除筛选
              </button>
            </div>

            <div class="timeline-preview-area">
              <Transition name="timeline-preview-fade" mode="out-in">
                <div
                  v-if="hoverPreviewPosts.length"
                  key="preview"
                  class="timeline-preview"
                >
                  <div class="timeline-preview-head">
                    {{ hoverPreviewLabel }} · {{ hoverPreviewPosts.length }} 篇
                  </div>
                  <ul class="timeline-preview-list">
                    <li v-for="post in hoverPreviewPosts.slice(0, 6)" :key="post.id">
                      <span class="timeline-preview-date">{{ post.date }}</span>
                      <router-link :to="post.url">{{ post.title }}</router-link>
                    </li>
                  </ul>
                  <p v-if="hoverPreviewPosts.length > 6" class="timeline-preview-more">
                    +{{ hoverPreviewPosts.length - 6 }} more…
                  </p>
                </div>
                <p v-else key="placeholder" class="timeline-preview-placeholder">
                  悬停月份预览文章 · 面板内 hover 可晕染
                </p>
              </Transition>
            </div>

            <div class="timeline-years">
              <div v-for="year in timelineYears" :key="year.year" class="timeline-year">
                <span class="timeline-year-label">{{ year.year }}</span>
                <div class="timeline-months">
                  <button
                    v-for="m in year.months"
                    :key="m.key"
                    type="button"
                    class="timeline-month"
                    :class="{ active: monthFilter === m.key, empty: !m.count, hovered: hoverMonth === m.key }"
                    :style="{ '--heat': heatRatio(m.count) }"
                    :disabled="!m.count"
                    @mouseenter="setHoverMonth(m.key, m.count)"
                    @focus="setHoverMonth(m.key, m.count)"
                    @click="toggleMonth(m.key)"
                  >
                    <span class="timeline-bar" aria-hidden="true" />
                    <span class="timeline-label">{{ m.month }}</span>
                  </button>
                </div>
              </div>
            </div>
          </InkRevealPanel>

          <template v-for="group in visibleGroups" :key="group.year">
            <h2 class="archive-year">{{ group.year }}</h2>
            <template v-for="month in group.months" :key="`${group.year}-${month.month}`">
              <h3 class="archive-month">{{ month.label }}</h3>
              <ul class="archive-items">
                <li v-for="post in month.posts" :key="post.id">
                  <span class="date">{{ post.date }}</span>
                  <router-link :to="post.url">{{ post.title }}</router-link>
                  <span v-if="post.tags?.length" class="post-tags">
                    <span v-for="t in post.tags.slice(0, 2)" :key="t" class="mini-tag">{{ t }}</span>
                  </span>
                </li>
              </ul>
            </template>
          </template>

          <p v-if="monthFilter && !visibleGroups.length" class="timeline-empty">该月份暂无文章</p>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import InkRevealPanel from '../components/InkRevealPanel.vue'
import { ref, computed } from 'vue'
import { posts, buildArchive, getLastUpdateDate, getTags, tagUrl } from '../data/posts'
import { ARCHIVE_INK_IMAGE, ARCHIVE_INK_POSITION } from '../data/inkTheme'
import { usePageMeta } from '../composables/usePageMeta'

usePageMeta({ title: '归档', description: '按年月浏览全部技术学习笔记。' })

const totalPosts = computed(() => posts.length)
const totalTags = computed(() => getTags().length)
const allTags = computed(() => getTags())
const lastUpdate = computed(() => getLastUpdateDate())
const archiveGroups = computed(() => buildArchive())
const monthFilter = ref('')
const hoverMonth = ref('')

const monthPostsMap = computed(() => {
  const map = new Map()
  for (const group of archiveGroups.value) {
    for (const month of group.months) {
      const key = `${group.year}-${String(month.month).padStart(2, '0')}`
      map.set(key, month.posts)
    }
  }
  return map
})

const hoverPreviewPosts = computed(() => {
  if (!hoverMonth.value) return []
  return monthPostsMap.value.get(hoverMonth.value) || []
})

const hoverPreviewLabel = computed(() => {
  if (!hoverMonth.value) return ''
  const [year, monthStr] = hoverMonth.value.split('-')
  return `${year}年${parseInt(monthStr, 10)}月`
})

const maxMonthCount = computed(() => {
  let max = 1
  for (const group of archiveGroups.value) {
    for (const month of group.months) {
      max = Math.max(max, month.posts.length)
    }
  }
  return max
})

const timelineYears = computed(() =>
  archiveGroups.value.map(group => ({
    year: group.year,
    months: group.months.map(m => ({
      key: `${group.year}-${String(m.month).padStart(2, '0')}`,
      month: m.month,
      count: m.posts.length,
    })),
  }))
)

const visibleGroups = computed(() => {
  if (!monthFilter.value) return archiveGroups.value
  const [year, monthStr] = monthFilter.value.split('-')
  const monthNum = parseInt(monthStr, 10)
  return archiveGroups.value
    .filter(g => g.year === year)
    .map(g => ({
      ...g,
      months: g.months.filter(m => m.month === monthNum),
    }))
    .filter(g => g.months.length)
})

function heatRatio(count) {
  if (!count) return 0
  return Math.max(0.15, count / maxMonthCount.value)
}

function toggleMonth(key) {
  monthFilter.value = monthFilter.value === key ? '' : key
}

function setHoverMonth(key, count) {
  if (!count) return
  hoverMonth.value = key
}

function clearHoverMonth() {
  hoverMonth.value = ''
}
</script>

<style scoped>
.archive-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 2rem;
}

.archive-tag {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--steel);
  text-decoration: none;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border);
}

.archive-tag:hover {
  color: var(--orange);
  border-color: var(--orange);
}

.archive-timeline--ink {
  margin-bottom: 2.5rem;
}

:deep(.archive-timeline--ink .ink-panel__content) {
  padding: 1.15rem 1.25rem 1.25rem;
}

.timeline-head-label {
  letter-spacing: 0.1em;
}

.timeline-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--orange);
}

.timeline-preview-area {
  position: relative;
  min-height: 10.5rem;
  margin-bottom: 1rem;
}

.timeline-preview-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 1rem;
  border: 1px dashed color-mix(in srgb, var(--border) 70%, transparent);
  background: color-mix(in srgb, var(--bg-paper) 52%, transparent);
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  text-align: center;
  line-height: 1.6;
}

.timeline-preview {
  position: absolute;
  inset: 0;
  padding: 1rem 1.1rem;
  border: 1px dashed var(--orange);
  background: color-mix(in srgb, var(--bg-paper) 82%, transparent);
  overflow: auto;
}

.timeline-years {
  position: relative;
  padding-top: 0.15rem;
}

.timeline-clear {
  font-family: inherit;
  font-size: 0.6rem;
  color: var(--text-muted);
  background: none;
  border: 1px solid var(--border);
  padding: 0.15rem 0.45rem;
  cursor: pointer;
}

.timeline-clear:hover {
  color: var(--orange);
  border-color: var(--orange);
}

.timeline-preview-fade-enter-active,
.timeline-preview-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.timeline-preview-fade-enter-from,
.timeline-preview-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.timeline-preview-head {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--orange);
  letter-spacing: 0.06em;
  margin-bottom: 0.65rem;
}

.timeline-preview-list {
  list-style: none;
  display: grid;
  gap: 0.15rem;
}

.timeline-preview-list li {
  display: grid;
  grid-template-columns: 4.5rem 1fr;
  align-items: baseline;
  gap: 0.65rem;
  padding: 0.35rem 0;
  font-size: 0.875rem;
  border-bottom: 1px solid color-mix(in srgb, var(--orange) 12%, var(--border));
}

.timeline-preview-date {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.timeline-preview-list li:last-child {
  border-bottom: none;
}

.timeline-preview a {
  color: var(--text);
  text-decoration: none;
}

.timeline-preview a:hover {
  color: var(--orange);
  text-decoration: underline;
}

.timeline-preview-more {
  margin: 0.35rem 0 0;
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
}

.timeline-year {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding-top: 0.15rem;
}

.timeline-year:last-child {
  margin-bottom: 0;
}

.timeline-year-label {
  flex-shrink: 0;
  width: 2.5rem;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--steel);
  padding-bottom: 0.15rem;
}

.timeline-months {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  flex: 1;
}

.timeline-month {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.25rem 0.35rem;
  border: 1px solid transparent;
  background: none;
  cursor: pointer;
  min-width: 1.75rem;
}

.timeline-month.empty {
  opacity: 0.25;
  cursor: default;
}

.timeline-month:not(.empty):hover,
.timeline-month.hovered,
.timeline-month.active {
  border-color: var(--orange);
  background: color-mix(in srgb, var(--bg-paper) 75%, var(--orange-light));
}

.timeline-bar {
  display: block;
  width: 100%;
  min-width: 1.25rem;
  height: calc(4px + var(--heat, 0.15) * 28px);
  background: color-mix(in srgb, var(--orange) calc(var(--heat, 0.15) * 100%), var(--border));
  transition: height 0.15s;
}

.timeline-month.active .timeline-bar {
  background: var(--orange);
}

.timeline-label {
  font-family: var(--mono);
  font-size: 0.55rem;
  color: var(--text-muted);
}

.timeline-empty {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  padding: 2rem 0;
}

.post-tags {
  margin-left: auto;
  display: flex;
  gap: 0.25rem;
}

.mini-tag {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}

.archive-items li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

@media (prefers-reduced-motion: reduce) {
  .timeline-bar {
    transition: none;
  }

  .timeline-preview-fade-enter-active,
  .timeline-preview-fade-leave-active {
    transition: none;
  }
}
</style>

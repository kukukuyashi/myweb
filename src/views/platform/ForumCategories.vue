<template>
  <div class="forum-community platform-page container layout-single">
    <div
      v-if="backdropUrl"
      class="forum-backdrop"
      :style="backdropStyle"
      aria-hidden="true"
    ></div>
    <!-- 顶栏统计 -->
    <InkRevealPanel
      tag="header"
      root-class="forum-hero forum-hero--ink ink-panel"
      :image="PLATFORM_FORUM_INK_IMAGE"
      :position="PLATFORM_FORUM_INK_POSITION"
      :r-end="118"
      fade-direction="left"
    >
      <div class="forum-hero-text">
        <p class="platform-coord page-ink-coord">ACG · COMMUNITY · <span class="ink-hint">hover 晕染</span></p>
        <h1 class="forum-hero-title">CYINC 社区</h1>
        <p class="forum-hero-sub">分享你的 ACG 生活与技术笔记，结识同好</p>
      </div>
      <ForumCheckinCard :token="token" />
    </InkRevealPanel>

    <div class="forum-layout">
      <main class="forum-main">
        <!-- 排序 Tab -->
        <div class="forum-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
          <router-link v-if="token" to="/app/forum/new" class="forum-post-btn platform-btn-primary">
            发帖
          </router-link>
          <router-link v-else to="/app/login?redirect=/app/forum" class="forum-post-btn platform-btn-ghost">
            登录发帖
          </router-link>
        </div>

        <!-- 搜索 -->
        <div class="forum-search">
          <input v-model="searchQuery" type="search" placeholder="搜索话题…" class="forum-search-input" aria-label="搜索话题">
        </div>

        <!-- 分类标签 -->
        <div class="forum-tags">
          <button
            type="button"
            class="forum-tag"
            :class="{ active: !activeCategory }"
            @click="activeCategory = ''"
          >
            全部
          </button>
          <button
            v-for="cat in categories"
            :key="cat.slug"
            type="button"
            class="forum-tag"
            :class="{ active: activeCategory === cat.slug }"
            @click="activeCategory = cat.slug"
          >
            {{ cat.name }}
          </button>
        </div>

        <p v-if="loading" class="muted">加载中…</p>
        <p v-else-if="error" class="error">{{ error }}</p>

        <template v-else>
          <!-- 贴纸墙精选 7 篇 -->
          <ForumFeaturedWall :items="featuredThreads" />

          <!-- 帖子列表 -->
          <section class="forum-thread-section">
            <h2 class="forum-list-title">话题列表</h2>
            <p v-if="!displayThreads.length" class="muted">暂无匹配话题。</p>
            <ul v-else class="forum-thread-list">
              <li v-for="t in pagedThreads" :key="t.id || t.title" class="forum-thread-card platform-panel">
                <router-link v-if="t.id" :to="`/app/forum/t/${t.id}`" class="forum-thread-link">
                  <div class="forum-thread-head">
                    <img
                      v-if="authorAvatar(t)"
                      :src="authorAvatar(t)"
                      alt=""
                      class="forum-thread-avatar"
                    >
                    <span v-else class="forum-thread-avatar forum-thread-avatar--placeholder" aria-hidden="true">
                      {{ (t.author?.nickname || t.author?.username || '?').slice(0, 1) }}
                    </span>
                    <div class="forum-thread-meta-top">
                      <span class="forum-thread-author">{{ t.author?.nickname || t.author?.username || '访客' }}</span>
                      <span class="forum-thread-time">{{ formatDate(t.created_at) }}</span>
                      <span v-if="t.category_name" class="forum-thread-cat">{{ t.category_name }}</span>
                    </div>
                  </div>
                  <h3 class="forum-thread-title">{{ t.title }}</h3>
                  <p v-if="t.excerpt" class="forum-thread-excerpt">{{ t.excerpt }}</p>
                  <div class="forum-thread-stats">
                    <span>👁 {{ t.view_count || 0 }}</span>
                    <span>💬 {{ t.reply_count || 0 }}</span>
                  </div>
                </router-link>
                <div v-else class="forum-thread-link is-demo">
                  <h3 class="forum-thread-title">{{ t.title }}</h3>
                  <p class="forum-thread-excerpt muted">示例帖 — 登录后发第一篇真实话题吧</p>
                </div>
              </li>
            </ul>

            <nav v-if="pageCount > 1" class="forum-pagination">
              <button type="button" class="platform-btn-ghost" :disabled="page <= 1" @click="page--">上一页</button>
              <span class="forum-page-num">{{ page }} / {{ pageCount }}</span>
              <button type="button" class="platform-btn-ghost" :disabled="page >= pageCount" @click="page++">下一页</button>
            </nav>
          </section>
        </template>
      </main>

      <aside class="forum-aside">
        <section class="platform-panel forum-aside-block">
          <h3 class="forum-aside-title">📢 社区公告</h3>
          <ul class="forum-announce-list">
            <li v-for="(a, i) in forumAnnouncements" :key="i">
              <span>{{ a.icon }}</span> {{ a.text }}
            </li>
          </ul>
        </section>

        <section class="platform-panel forum-aside-block">
          <h3 class="forum-aside-title">🔥 热门话题</h3>
          <ol class="forum-hot-list">
            <li v-for="(t, i) in hotThreads" :key="t.id || i">
              <span class="hot-rank">{{ i + 1 }}</span>
              <router-link v-if="t.id" :to="`/app/forum/t/${t.id}`">{{ t.title }}</router-link>
              <span v-else>{{ t.title }}</span>
              <span class="hot-replies">{{ t.reply_count || 0 }} 回复</span>
            </li>
          </ol>
        </section>

        <section class="platform-panel forum-aside-block">
          <h3 class="forum-aside-title">板块</h3>
          <ul class="forum-cat-list">
            <li v-for="cat in categories" :key="cat.id">
              <router-link :to="`/app/forum/c/${cat.slug}`">{{ cat.name }}</router-link>
              <span>{{ cat.thread_count }} 帖</span>
            </li>
          </ul>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import InkRevealPanel from '../../components/InkRevealPanel.vue'
import ForumFeaturedWall from '../../components/forum/ForumFeaturedWall.vue'
import ForumCheckinCard from '../../components/forum/ForumCheckinCard.vue'
import { PLATFORM_FORUM_INK_IMAGE, PLATFORM_FORUM_INK_POSITION, pickForumBackdrop } from '../../data/inkTheme.js'
import { imgUrl } from '../../data/profile.js'
import { useForumBackdrop } from '../../composables/useForumBackdrop.js'
import { usePageMeta } from '../../composables/usePageMeta'
import { forumAnnouncements, pickCover } from '../../data/forumDemo.js'
import {
  fetchForumCategories,
  fetchForumFeaturedThreads,
  fetchForumRecentThreads,
  fetchMyForumThreads,
  getPlatformToken,
  resolvePublicUrl,
} from '../../api/platform.js'

usePageMeta({ title: '论坛', description: 'CYINC ACG 社区论坛。' })

const token = ref(getPlatformToken())
const backdropUrl = ref(imgUrl(pickForumBackdrop()))
const { blur: backdropBlur, dark: backdropDark } = useForumBackdrop()
const backdropStyle = computed(() => {
  if (!backdropUrl.value) return {}
  const brightness = Math.max(0, 1 - backdropDark.value / 100)
  const mask = Math.min(0.92, 0.25 + backdropDark.value / 130)
  return {
    backgroundImage: `url("${backdropUrl.value}")`,
    filter: `blur(${backdropBlur.value}px) saturate(1.08) brightness(${brightness})`,
    '--backdrop-mask': String(mask),
  }
})
const categories = ref([])
const allThreads = ref([])
const featuredThreads = ref([])
const myThreads = ref([])
const loading = ref(true)
const error = ref('')
const activeTab = ref('all')
const activeCategory = ref('')
const searchQuery = ref('')
const page = ref(1)
const pageSize = 8

const tabs = [
  { id: 'all', label: '全部话题' },
  { id: 'hot', label: '热门话题' },
  { id: 'latest', label: '最新话题' },
  { id: 'mine', label: '我的话题' },
]

const sortedThreads = computed(() => {
  let list = activeTab.value === 'mine' && token.value
    ? [...myThreads.value]
    : [...allThreads.value.filter((t) => t.id)]

  if (activeTab.value === 'hot') {
    list.sort((a, b) => (b.reply_count || 0) - (a.reply_count || 0))
  } else {
    list.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
  }

  if (activeCategory.value) {
    list = list.filter((t) => t.category_slug === activeCategory.value)
  }

  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter((t) => t.title?.toLowerCase().includes(q))
  }

  return list.map((t, i) => ({
    ...t,
    cover: t.cover_url || t.cover || pickCover(i),
    excerpt: t.excerpt || t.title,
  }))
})

const displayThreads = computed(() => sortedThreads.value)

const pageCount = computed(() => Math.max(1, Math.ceil(displayThreads.value.length / pageSize)))

const pagedThreads = computed(() => {
  const start = (page.value - 1) * pageSize
  return displayThreads.value.slice(start, start + pageSize)
})

const hotThreads = computed(() =>
  [...allThreads.value.filter((t) => t.id)]
    .sort((a, b) => (b.reply_count || 0) - (a.reply_count || 0))
    .slice(0, 5),
)

function formatDate(iso) {
  if (!iso) return '刚刚'
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

function authorAvatar(t) {
  return resolvePublicUrl(t?.author?.avatar || '')
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [catJson, threadJson, featuredJson] = await Promise.all([
      fetchForumCategories(),
      fetchForumRecentThreads(20),
      fetchForumFeaturedThreads(),
    ])
    categories.value = catJson.data || []
    allThreads.value = threadJson.data?.items || threadJson.data || []
    const rawFeatured = featuredJson.data?.items || []
    featuredThreads.value = rawFeatured.map((t, i) => ({
      ...t,
      cover: t.cover_url || pickCover(i),
      excerpt: t.excerpt || t.title,
    }))
    if (token.value) {
      const mineJson = await fetchMyForumThreads()
      myThreads.value = mineJson.data?.items || []
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch([activeTab, activeCategory, searchQuery], () => { page.value = 1 })

onMounted(load)
</script>

<style scoped>
.forum-community {
  position: relative;
}

.forum-backdrop {
  position: fixed;
  inset: 0;
  z-index: -1;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: blur(22px) saturate(1.08) brightness(0.55);
  transform: scale(1.12);
  opacity: 0.85;
  pointer-events: none;
  transition: filter 0.2s ease;
}

.forum-backdrop::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--bg) calc(var(--backdrop-mask, 0.45) * 70%), transparent) 0%,
    color-mix(in srgb, var(--bg) calc(var(--backdrop-mask, 0.45) * 100%), transparent) 100%
  );
}

.forum-hero {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1.25rem;
  align-items: center;
  margin-bottom: 1.25rem;
}

.forum-hero--ink :deep(.ink-panel__content) {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1.25rem;
  align-items: center;
  padding: clamp(1.15rem, 3vw, 1.75rem);
  min-height: 140px;
}

@media (max-width: 720px) {
  .forum-hero--ink :deep(.ink-panel__content) {
    grid-template-columns: 1fr;
  }
}

.forum-hero-title {
  margin: 0.25rem 0 0;
  font-size: clamp(1.5rem, 4vw, 2rem);
}

.forum-hero-sub {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.forum-stat-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.forum-stat {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--bg);
  min-width: 7rem;
}

.forum-stat-icon {
  font-size: 1.25rem;
}

.forum-stat strong {
  display: block;
  font-family: var(--mono);
  font-size: 1.1rem;
  color: var(--orange);
}

.forum-stat span {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.forum-layout {
  display: grid;
  grid-template-columns: 1fr minmax(220px, 280px);
  gap: 1.25rem;
  align-items: start;
}

.forum-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
  margin-bottom: 0.85rem;
}

.forum-tabs button {
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--bg-paper);
  cursor: pointer;
  color: var(--text-muted);
}

.forum-tabs button.active {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.forum-post-btn {
  margin-left: auto;
  border-radius: 999px;
  text-decoration: none;
}

.forum-search {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
}

.forum-search-input {
  flex: 1;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--bg);
  font: inherit;
}

.forum-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1.25rem;
}

.forum-tag {
  font-family: var(--mono);
  font-size: 0.68rem;
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--bg-paper);
  cursor: pointer;
  color: var(--text-muted);
}

.forum-tag.active {
  background: color-mix(in srgb, var(--orange) 12%, var(--bg-paper));
  border-color: var(--orange);
  color: var(--orange);
}

.forum-thread-section {
  margin-top: 1.5rem;
}

.forum-list-title {
  margin: 0 0 0.75rem;
  font-size: 1rem;
}

.forum-thread-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.75rem;
}

.forum-thread-card {
  border-radius: 14px;
  padding: 0;
  overflow: hidden;
}

.forum-thread-link {
  display: block;
  padding: 1rem 1.1rem;
  text-decoration: none;
  color: inherit;
}

.forum-thread-link.is-demo {
  opacity: 0.85;
}

.forum-thread-head {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  margin-bottom: 0.5rem;
}

.forum-thread-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.forum-thread-avatar--placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-paper);
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 0.75rem;
}

.forum-thread-meta-top {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.65rem;
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}

.forum-thread-cat {
  color: var(--orange);
}

.forum-thread-title {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
  line-height: 1.4;
}

.forum-thread-link:hover .forum-thread-title {
  color: var(--orange);
}

.forum-thread-excerpt {
  margin: 0 0 0.5rem;
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.forum-thread-stats {
  display: flex;
  gap: 1rem;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.forum-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 1rem;
}

.forum-page-num {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

.forum-aside-title {
  margin: 0 0 0.65rem;
  font-size: 0.88rem;
}

.forum-aside-block + .forum-aside-block {
  margin-top: 0.85rem;
}

.forum-announce-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.forum-hot-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.55rem;
  font-size: 0.82rem;
}

.forum-hot-list li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.35rem 0.5rem;
  align-items: baseline;
}

.hot-rank {
  font-family: var(--mono);
  color: var(--orange);
  font-size: 0.72rem;
}

.forum-hot-list a {
  color: inherit;
  text-decoration: none;
}

.forum-hot-list a:hover {
  color: var(--orange);
}

.hot-replies {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.forum-cat-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.45rem;
  font-size: 0.82rem;
}

.forum-cat-list li {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.forum-cat-list a {
  color: inherit;
  text-decoration: none;
}

.forum-cat-list a:hover {
  color: var(--orange);
}

.forum-cat-list span {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}

.muted { color: var(--text-muted); font-size: 0.88rem; }
.error { color: #c0392b; }

@media (max-width: 900px) {
  .forum-hero {
    grid-template-columns: 1fr;
  }

  .forum-layout {
    grid-template-columns: 1fr;
  }

  .forum-aside {
    order: -1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
  }

  .forum-aside-block + .forum-aside-block {
    margin-top: 0;
  }
}
</style>

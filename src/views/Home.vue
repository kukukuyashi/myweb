<template>
  <div ref="homeRef" class="home">
    <NavBar />
    <main class="page-main">
      <div class="container">
        <div class="layout">
          <div class="main-col">
            <InkRevealPanel
              tag="section"
              root-class="hero hero--ink"
              :image="HOME_INK_IMAGE"
              :position="HOME_INK_POSITION"
              :r-end="128"
              :max-stamps="150"
            >
              <HeroTicker :items="tickerItems" />
              <p class="hero-season">{{ seasonLabel }} · SEASON SKIN</p>
              <div class="hero-row">
                <div class="hero-text">
                  <h1>技术学习日志</h1>
                  <p class="hero-desc">前端笔记、Agent 探索、踩坑记录 — 追番听歌和技术一样认真。</p>
                  <p class="hero-about">
                    <router-link to="/about">我是谁</router-link>
                    <span class="hero-about-sep">·</span>
                    <span>贴纸墙与 ACG 档案</span>
                  </p>
                </div>
                <router-link to="/about" class="hero-avatar-link hero-avatar-float" title="关于 Cyinc">
                  <div class="acg-frame acg-frame--avatar acg-frame--hero">
                    <img :src="avatarUrl" alt="Cyinc" width="80" height="80" loading="lazy">
                  </div>
                </router-link>
              </div>
              <div class="hero-stats">
                <div>
                  <div class="stat-num"><StatCounter :value="totalPosts" /></div>
                  <div class="stat-label">Articles</div>
                </div>
                <div>
                  <div class="stat-num"><StatCounter :value="totalCategories" /></div>
                  <div class="stat-label">Categories</div>
                </div>
                <div>
                  <div class="stat-num"><StatCounter :value="totalTags" /></div>
                  <div class="stat-label">Tags</div>
                </div>
                <div>
                  <div class="stat-num"><StatCounter :value="siteAge" /></div>
                  <div class="stat-label">Online</div>
                </div>
              </div>
            </InkRevealPanel>

            <ChangelogStrip v-if="!hasActiveFilter" :delay="85" />

            <div class="filter-bar reveal-item" data-reveal style="--reveal-delay: 80ms">
              <label>分类</label>
              <button
                v-for="category in categories"
                :key="category"
                :class="['filter-btn', { active: selectedCategory === category }]"
                @click="selectCategory(category)"
              >{{ category }}</button>
            </div>

            <TagBar v-model="selectedTag" @update:model-value="onTagChange" />

            <div class="search-row">
              <input
                type="text"
                placeholder="搜索标题或摘要..."
                class="search-input"
                v-model="searchQuery"
              >
              <button v-if="searchQuery" class="search-btn" @click="searchQuery = ''">清除</button>
            </div>

            <SeriesSection v-if="!hasActiveFilter" :delay="110" />

            <div class="section-head reveal-item" data-reveal style="--reveal-delay: 120ms"><h2>精选</h2></div>
            <div v-if="highlightPosts.length && !hasActiveFilter" class="featured-grid">
              <PostCard
                v-for="(post, i) in highlightPosts"
                :key="post.id"
                :post="post"
                :featured="post.featured"
                :reveal-delay="160 + i * 90"
              />
            </div>

            <div class="section-head reveal-item" data-reveal style="--reveal-delay: 100ms">
              <h2>全部文章</h2>
              <span class="result-count">{{ filteredPosts.length }} 篇</span>
            </div>
            <ul v-if="paginatedPosts.length" class="archive-list">
              <li
                v-for="(post, index) in paginatedPosts"
                :key="post.id"
                class="archive-row reveal-item"
                data-reveal
                :style="{ '--reveal-delay': `${120 + index * 45}ms`, '--cat-color': getCategoryColor(post.category) }"
              >
                <span class="archive-idx">{{ String(listOffset + index + 1).padStart(2, '0') }}</span>
                <router-link :to="post.url" class="archive-title">{{ post.title }}</router-link>
                <span class="archive-date hide-mobile">{{ post.date }}</span>
                <span class="archive-cat tag">{{ post.category }}</span>
              </li>
            </ul>
            <SystemHaltPanel
              v-else
              compact
              code="EMPTY"
              headline="NO MATCH"
              message="没有找到匹配的文章"
              status="FILTER_IDLE"
              :lines="emptyDiagLines"
              :home-link="false"
            />

            <div v-if="totalPages > 1" class="pagination">
              <button :disabled="currentPage <= 1" @click="currentPage--">上一页</button>
              <span>{{ currentPage }} / {{ totalPages }}</span>
              <button :disabled="currentPage >= totalPages" @click="currentPage++">下一页</button>
            </div>

            <section class="about-strip reveal-item" data-reveal style="--reveal-delay: 200ms">
              <router-link to="/about" class="about-strip-inner">
                <div class="acg-frame acg-frame--avatar about-strip-avatar">
                  <img :src="avatarUrl" alt="Cyinc" width="56" height="56" loading="lazy">
                </div>
                <div class="about-strip-text">
                  <h3>关于 Cyinc</h3>
                  <p>写代码，也写番剧观后感；Agent 在学，芙莉莲旅途进行中。</p>
                  <p class="about-strip-sub">技术笔记本 + ACG 自留地 — 不必把爱好分开。</p>
                </div>
                <span class="about-strip-cta">贴纸墙 →</span>
              </router-link>
            </section>
          </div>

          <BlogAside
            :total-posts="totalPosts"
            :total-categories="totalCategories"
            :total-tags="totalTags"
            :site-age="siteAge"
          />
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import BlogAside from '../components/BlogAside.vue'
import SiteFooter from '../components/SiteFooter.vue'
import TagBar from '../components/TagBar.vue'
import InkRevealPanel from '../components/InkRevealPanel.vue'
import PostCard from '../components/PostCard.vue'
import HeroTicker from '../components/HeroTicker.vue'
import StatCounter from '../components/StatCounter.vue'
import SystemHaltPanel from '../components/SystemHaltPanel.vue'
import SeriesSection from '../components/SeriesSection.vue'
import ChangelogStrip from '../components/ChangelogStrip.vue'
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  postsWithUrl,
  getHighlightPosts,
  getCategories,
  getTags,
  getCategoryColor,
  postMatchesFanTag,
  FAN_TAG_FILTERS,
  SITE_DESCRIPTION,
} from '../data/posts'
import { usePageMeta } from '../composables/usePageMeta'
import { useRevealOnScroll, observeReveal } from '../composables/useRevealOnScroll'
import { useSeasonTheme } from '../composables/useSeasonTheme'
import { HOME_INK_IMAGE, HOME_INK_POSITION } from '../data/inkTheme'
import { profile, imgUrl } from '../data/profile'

usePageMeta({ title: '', description: SITE_DESCRIPTION })

const { seasonLabel, tickerItems } = useSeasonTheme()

const homeRef = ref(null)
useRevealOnScroll(homeRef)

const avatarUrl = computed(() => imgUrl(profile.avatar))

const route = useRoute()
const router = useRouter()
const PAGE_SIZE = 10

const allPosts = postsWithUrl()
const selectedCategory = ref('全部')
const selectedTag = ref('')
const searchQuery = ref('')
const currentPage = ref(1)
const siteStartDate = new Date('2024-01-01')

const totalPosts = computed(() => allPosts.length)
const totalCategories = computed(() => getCategories().length)
const totalTags = computed(() => getTags().length)
const categories = computed(() => ['全部', ...getCategories()])

const siteAge = computed(() => {
  const diffDays = Math.floor((Date.now() - siteStartDate) / (1000 * 60 * 60 * 24))
  if (diffDays < 30) return `${diffDays}d`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo`
  return `${Math.floor(diffDays / 365)}y`
})

const hasActiveFilter = computed(() =>
  selectedCategory.value !== '全部' || !!selectedTag.value || !!searchQuery.value
)

const highlightPosts = computed(() => getHighlightPosts(3))

const emptyDiagLines = computed(() => {
  const parts = []
  if (selectedCategory.value !== '全部') parts.push(`CAT:: ${selectedCategory.value}`)
  if (selectedTag.value) parts.push(`TAG:: ${selectedTag.value}`)
  if (searchQuery.value) parts.push(`Q:: ${searchQuery.value}`)
  parts.push('HINT:: clear filters or try another keyword')
  return parts
})

const filteredPosts = computed(() => {
  let list = allPosts
  if (!hasActiveFilter.value) {
    const excludeIds = new Set(highlightPosts.value.map(p => p.id))
    list = list.filter(p => !excludeIds.has(p.id))
  }
  return list.filter(post => {
    const cat = selectedCategory.value === '全部' || post.category === selectedCategory.value
    let tag = true
    if (selectedTag.value) {
      tag = FAN_TAG_FILTERS[selectedTag.value]
        ? postMatchesFanTag(post, selectedTag.value)
        : (post.tags || []).includes(selectedTag.value)
    }
    const q = searchQuery.value.toLowerCase()
    const search = !q || post.title.toLowerCase().includes(q) || post.excerpt.toLowerCase().includes(q)
    return cat && tag && search
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredPosts.value.length / PAGE_SIZE)))

const listOffset = computed(() => (currentPage.value - 1) * PAGE_SIZE)

const paginatedPosts = computed(() =>
  filteredPosts.value.slice(listOffset.value, listOffset.value + PAGE_SIZE)
)

watch([selectedCategory, selectedTag, searchQuery], () => { currentPage.value = 1 })

watch([paginatedPosts, currentPage], () => {
  nextTick(() => observeReveal(homeRef.value))
})

function selectCategory(category) {
  selectedCategory.value = category
}

function onTagChange(tag) {
  selectedTag.value = tag
  router.replace({ query: tag ? { tag } : {} })
}

onMounted(() => {
  if (route.query.tag) selectedTag.value = String(route.query.tag)
})

watch(() => route.query.tag, (t) => {
  selectedTag.value = t ? String(t) : ''
})
</script>

<style scoped>
.hero-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.25rem;
  margin-bottom: 0.25rem;
}

.hero-text {
  flex: 1;
  min-width: 0;
}

.hero-avatar-link {
  flex-shrink: 0;
  text-decoration: none;
  transition: transform 0.15s;
}

.hero-avatar-link:hover {
  transform: translateY(-2px);
}

.search-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.search-row .search-input { flex: 1; }

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.result-count {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  font-family: var(--mono);
  font-size: 0.75rem;
}

.pagination button {
  padding: 0.35rem 0.85rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  cursor: pointer;
  font-family: inherit;
}

.pagination button:hover:not(:disabled) {
  border-color: var(--orange);
  color: var(--orange);
}

.pagination button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.hero-about {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 0.65rem;
}

.hero-about a {
  color: var(--orange);
  text-decoration: none;
}

.hero-about a:hover {
  text-decoration: underline;
}

.hero-about-sep {
  margin: 0 0.35rem;
  opacity: 0.5;
}

.hero-season {
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.14em;
  color: var(--orange);
  opacity: 0.75;
  margin: -0.35rem 0 0.85rem;
}

@media (max-width: 640px) {
  .hero-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-avatar-link {
    align-self: flex-end;
  }

  .search-row {
    flex-direction: column;
  }

  .search-row .search-btn {
    align-self: flex-start;
  }

  .featured-foot {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>

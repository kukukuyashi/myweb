<template>
  <div class="home">
    <NavBar />
    <main class="page-main">
      <div class="container">
        <div class="layout">
          <div class="main-col">
            <InkRevealPanel
              tag="section"
              root-class="hero hero--ink"
              image="img/关于/FrhwkwYaMAE2R6L.jfif"
              position="85% center"
              :r-end="128"
              :max-stamps="150"
            >
              <div class="hero-coord">ACG · LEARNING · AGENT · NOTES · <span class="ink-hint">hover 晕染</span></div>
              <div class="hero-row">
                <div class="hero-text">
                  <h1>写给自己的<br><em>技术学习</em>日志</h1>
                  <p class="hero-desc">前端笔记、Agent 探索、踩坑记录 — 追番听歌和技术一样认真。</p>
                </div>
                <router-link to="/about" class="hero-avatar-link" title="关于 Cyinc">
                  <div class="acg-frame acg-frame--avatar acg-frame--hero">
                    <img :src="avatarUrl" alt="Cyinc" width="80" height="80">
                  </div>
                </router-link>
              </div>
              <div class="hero-stats">
                <div>
                  <div class="stat-num">{{ totalPosts }}</div>
                  <div class="stat-label">Articles</div>
                </div>
                <div>
                  <div class="stat-num">{{ totalCategories }}</div>
                  <div class="stat-label">Categories</div>
                </div>
                <div>
                  <div class="stat-num">{{ totalTags }}</div>
                  <div class="stat-label">Tags</div>
                </div>
                <div>
                  <div class="stat-num">{{ siteAge }}</div>
                  <div class="stat-label">Online</div>
                </div>
              </div>
            </InkRevealPanel>

            <div class="filter-bar">
              <label>分类</label>
              <button
                v-for="category in categories"
                :key="category"
                :class="['filter-btn', { active: selectedCategory === category }]"
                @click="selectCategory(category)"
              >{{ category }}</button>
            </div>

            <TagBar v-if="allTags.length" v-model="selectedTag" :tags="allTags" @update:model-value="onTagChange" />

            <div class="search-row">
              <input
                type="text"
                placeholder="搜索标题或摘要..."
                class="search-input"
                v-model="searchQuery"
              >
              <button v-if="searchQuery" class="search-btn" @click="searchQuery = ''">清除</button>
            </div>

            <div class="section-head"><h2>精选</h2></div>
            <article v-if="featuredPost && !hasActiveFilter" class="featured">
              <span class="featured-dim">最新</span>
              <h3><router-link :to="featuredPost.url">{{ featuredPost.title }}</router-link></h3>
              <p>{{ featuredPost.excerpt }}</p>
              <div class="featured-meta">{{ featuredPost.date }} / {{ featuredPost.category }}</div>
            </article>

            <div class="section-head">
              <h2>全部文章</h2>
              <span class="result-count">{{ filteredPosts.length }} 篇</span>
            </div>
            <table v-if="paginatedPosts.length" class="post-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>标题</th>
                  <th class="hide-mobile">日期</th>
                  <th>分类</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(post, index) in paginatedPosts" :key="post.id">
                  <td class="idx">{{ String(listOffset + index + 1).padStart(2, '0') }}</td>
                  <td><router-link :to="post.url">{{ post.title }}</router-link></td>
                  <td class="hide-mobile">{{ post.date }}</td>
                  <td><span class="tag">{{ post.category }}</span></td>
                </tr>
              </tbody>
            </table>
            <div v-else class="no-posts">没有找到匹配的文章</div>

            <div v-if="totalPages > 1" class="pagination">
              <button :disabled="currentPage <= 1" @click="currentPage--">上一页</button>
              <span>{{ currentPage }} / {{ totalPages }}</span>
              <button :disabled="currentPage >= totalPages" @click="currentPage++">下一页</button>
            </div>
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
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsWithUrl, getLatestPost, getCategories, getTags, SITE_DESCRIPTION } from '../data/posts'
import { usePageMeta } from '../composables/usePageMeta'
import { profile, imgUrl } from '../data/profile'

usePageMeta({ title: '', description: SITE_DESCRIPTION })

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
const allTags = computed(() => getTags())
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

const filteredPosts = computed(() => {
  let list = allPosts
  if (!hasActiveFilter.value) {
    const latest = getLatestPost()
    list = list.filter(p => p.id !== latest.id)
  }
  return list.filter(post => {
    const cat = selectedCategory.value === '全部' || post.category === selectedCategory.value
    const tag = !selectedTag.value || (post.tags || []).includes(selectedTag.value)
    const q = searchQuery.value.toLowerCase()
    const search = !q || post.title.toLowerCase().includes(q) || post.excerpt.toLowerCase().includes(q)
    return cat && tag && search
  })
})

const featuredPost = computed(() => {
  const latest = getLatestPost()
  return allPosts.find(p => p.id === latest.id)
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredPosts.value.length / PAGE_SIZE)))

const listOffset = computed(() => (currentPage.value - 1) * PAGE_SIZE)

const paginatedPosts = computed(() =>
  filteredPosts.value.slice(listOffset.value, listOffset.value + PAGE_SIZE)
)

watch([selectedCategory, selectedTag, searchQuery], () => { currentPage.value = 1 })

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
}
</style>

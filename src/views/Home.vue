<template>
  <div class="home">
    <NavBar />
    <main class="page-main">
      <div class="container">
        <div class="layout">
          <div class="main-col">
            <section class="hero">
              <div class="hero-coord">LEARNING · AGENT · NOTES</div>
              <h1>写给自己的<br><em>技术学习</em>日志</h1>
              <p class="hero-desc">前端笔记、Agent 探索、踩坑记录。不追热点，只留真正用得上的东西。</p>
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
                  <div class="stat-num">{{ siteAge }}</div>
                  <div class="stat-label">Online</div>
                </div>
              </div>
            </section>

            <div class="filter-bar">
              <label>分类</label>
              <button
                v-for="category in categories"
                :key="category"
                :class="['filter-btn', { active: selectedCategory === category }]"
                @click="filterByCategory(category)"
              >{{ category }}</button>
              <div class="search-box">
                <input
                  type="text"
                  placeholder="搜索文章..."
                  class="search-input"
                  v-model="searchQuery"
                >
                <button class="search-btn" @click="searchQuery = ''">清除</button>
              </div>
            </div>

            <div class="section-head"><h2>精选</h2></div>
            <article v-if="featuredPost" class="featured">
              <span class="featured-dim">最新</span>
              <h3><router-link :to="featuredPost.url">{{ featuredPost.title }}</router-link></h3>
              <p>{{ featuredPost.excerpt }}</p>
              <div class="featured-meta">{{ featuredPost.date }} / {{ featuredPost.category }}</div>
            </article>

            <div class="section-head"><h2>全部文章</h2></div>
            <table v-if="listPosts.length" class="post-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>标题</th>
                  <th class="hide-mobile">日期</th>
                  <th>分类</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(post, index) in listPosts" :key="post.id">
                  <td class="idx">{{ String(index + 1).padStart(2, '0') }}</td>
                  <td><router-link :to="post.url">{{ post.title }}</router-link></td>
                  <td class="hide-mobile">{{ post.date }}</td>
                  <td><span class="tag">{{ post.category }}</span></td>
                </tr>
              </tbody>
            </table>
            <div v-else class="no-posts">没有找到匹配的文章</div>
          </div>

          <BlogAside
            :total-posts="totalPosts"
            :total-categories="totalCategories"
            :site-age="siteAge"
          />
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import BlogAside from '../components/BlogAside.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { ref, computed } from 'vue'
import { postsWithUrl, getLatestPost, getCategories } from '../data/posts'

const allPosts = postsWithUrl()
const selectedCategory = ref('全部')
const searchQuery = ref('')
const siteStartDate = new Date('2024-01-01')

const totalPosts = computed(() => allPosts.length)
const totalCategories = computed(() => getCategories().length)

const siteAge = computed(() => {
  const diffDays = Math.floor((Date.now() - siteStartDate) / (1000 * 60 * 60 * 24))
  if (diffDays < 30) return `${diffDays}d`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo`
  return `${Math.floor(diffDays / 365)}y`
})

const categories = computed(() => ['全部', ...getCategories()])

const filteredPosts = computed(() =>
  allPosts.filter(post => {
    const cat = selectedCategory.value === '全部' || post.category === selectedCategory.value
    const q = searchQuery.value.toLowerCase()
    const search = !q || post.title.toLowerCase().includes(q) || post.excerpt.toLowerCase().includes(q)
    return cat && search
  })
)

const featuredPost = computed(() => {
  const latest = getLatestPost()
  return allPosts.find(p => p.id === latest.id)
})

const listPosts = computed(() =>
  filteredPosts.value.filter(p => p.id !== featuredPost.value?.id)
)

function filterByCategory(category) {
  selectedCategory.value = category
}
</script>

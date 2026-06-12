<template>
  <div class="content-page">
    <NavBar />
    <main class="page-main">
      <div class="container">
        <div class="content-layout">
          <aside class="toc-sidebar" v-if="tocItems.length > 0">
            <div class="toc">
              <h3>Contents</h3>
              <ul>
                <li v-for="item in tocItems" :key="item.id" :class="'toc-level-' + item.level">
                  <a @click="scrollToSection(item.id)" :class="{ active: activeSection === item.id }">
                    {{ item.text }}
                  </a>
                </li>
              </ul>
            </div>
          </aside>

          <div class="article-wrap">
            <div class="article-content">
              <h1 class="article-title">{{ articleTitle }}</h1>
              <div class="article-meta">
                <span>{{ currentDate }}</span>
                <span> · {{ articleCategory }}</span>
                <span v-if="readingMinutes"> · 约 {{ readingMinutes }} 分钟</span>
              </div>
              <div v-if="articleTags.length" class="article-tags">
                <router-link
                  v-for="tag in articleTags"
                  :key="tag"
                  :to="{ path: '/', query: { tag } }"
                  class="tag-link"
                >#{{ tag }}</router-link>
              </div>
              <div class="article-body" ref="articleBodyRef">
                <p v-if="loading">加载中...</p>
                <p v-else-if="error">{{ error }}</p>
                <div v-else v-html="articleContent"></div>
              </div>

              <nav v-if="adjacent.newer || adjacent.older" class="article-nav">
                <router-link v-if="adjacent.newer" :to="adjacent.newer.url" class="nav-prev">
                  <span class="nav-label">← 较新</span>
                  <span class="nav-title">{{ adjacent.newer.title }}</span>
                </router-link>
                <router-link v-if="adjacent.older" :to="adjacent.older.url" class="nav-next">
                  <span class="nav-label">较旧 →</span>
                  <span class="nav-title">{{ adjacent.older.title }}</span>
                </router-link>
              </nav>

              <section v-if="relatedPosts.length" class="related-posts">
                <h3 class="related-head">相关文章</h3>
                <ul>
                  <li v-for="p in relatedPosts" :key="p.id">
                    <router-link :to="p.url">{{ p.title }}</router-link>
                    <span class="related-date">{{ p.date }}</span>
                  </li>
                </ul>
              </section>

              <section class="article-comments">
                <h3 class="comments-head">评论</h3>
                <p v-if="commentStatus === 'loading'" class="comments-hint">评论加载中…</p>
                <p v-if="commentStatus === 'error'" class="comments-hint error">评论暂不可用</p>
                <div id="article-tcomment"></div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { ref, computed, watch, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  getPostById,
  getAdjacentPosts,
  getRelatedPosts,
  SITE_URL,
} from '../data/posts'
import { usePageMeta } from '../composables/usePageMeta'
import { useTwikoo } from '../composables/useTwikoo'
import { highlightArticle, estimateReadingMinutes } from '../utils/highlightCode'

const route = useRoute()
const currentDate = ref('')
const articleCategory = ref('')
const articleTitle = ref('')
const articleTags = ref([])
const articleContent = ref('')
const loading = ref(true)
const error = ref('')
const readingMinutes = ref(0)
const tocItems = ref([])
const activeSection = ref('')
const articleBodyRef = ref(null)
const adjacent = ref({ newer: null, older: null })
const relatedPosts = ref([])
let observer = null

const postId = computed(() => route.params.id)
const currentPost = computed(() => getPostById(postId.value))

const pageMeta = computed(() => {
  const post = currentPost.value
  if (!post) return { title: '文章未找到' }
  return {
    title: post.title,
    description: post.excerpt,
    url: `${SITE_URL}${import.meta.env.BASE_URL}content/${post.id}`.replace(/([^:]\/)\/+/g, '$1'),
    type: 'article',
  }
})
usePageMeta(pageMeta)

const { status: commentStatus, init: initComments } = useTwikoo('article-tcomment', () => ({
  path: `/content/${postId.value}`,
}))

async function loadArticleContent() {
  loading.value = true
  error.value = ''
  articleContent.value = ''
  tocItems.value = []
  readingMinutes.value = 0
  relatedPosts.value = []
  adjacent.value = { newer: null, older: null }

  const post = currentPost.value

  if (!post) {
    loading.value = false
    error.value = '文章不存在或已被移除'
    articleTitle.value = '404'
    return
  }

  articleTitle.value = post.title
  currentDate.value = post.date
  articleCategory.value = post.category
  articleTags.value = post.tags || []
  adjacent.value = getAdjacentPosts(post.id)
  relatedPosts.value = getRelatedPosts(post.id)

  try {
    const base = import.meta.env.BASE_URL || '/'
    const response = await fetch(`${base}Content/${encodeURIComponent(post.file)}`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    let content = await response.text()
    content = content.replace(/href="\.\.\//g, `href="${base}`)
    content = content.replace(/href="\.\//g, `href="${base}`)
    content = content.replace(/src="\.\.\//g, `src="${base}`)
    content = content.replace(/src="\.\//g, `src="${base}`)
    articleContent.value = content
    readingMinutes.value = estimateReadingMinutes(content)
    loading.value = false
    await nextTick()
    highlightArticle(articleBodyRef.value)
    generateTOC()
    setupIntersectionObserver()
    await initComments()
  } catch (e) {
    console.error('加载文章失败:', e)
    loading.value = false
    error.value = `加载失败：${e.message}`
  }
}

function generateTOC() {
  if (!articleBodyRef.value) return
  const headings = articleBodyRef.value.querySelectorAll('h2, h3, h4')
  tocItems.value = Array.from(headings).map((heading, index) => {
    if (!heading.id) heading.id = `section-${index}`
    return {
      id: heading.id,
      text: heading.textContent.trim(),
      level: parseInt(heading.tagName.charAt(1)),
    }
  })
}

function scrollToSection(id) {
  const element = document.getElementById(id)
  if (element) {
    const offset = element.getBoundingClientRect().top + window.pageYOffset - 80
    window.scrollTo({ top: offset, behavior: 'smooth' })
    activeSection.value = id
  }
}

function setupIntersectionObserver() {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) activeSection.value = entry.target.id
    })
  }, { rootMargin: '-20% 0px -80% 0px', threshold: 0 })
  tocItems.value.forEach(item => {
    const el = document.getElementById(item.id)
    if (el) observer.observe(el)
  })
}

onMounted(() => loadArticleContent())
watch(postId, () => loadArticleContent())
onUnmounted(() => { if (observer) observer.disconnect() })
</script>

<style scoped>
.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
}

.tag-link {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--steel);
  text-decoration: none;
  padding: 0.15rem 0.45rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
}

.tag-link:hover {
  color: var(--orange);
  border-color: var(--orange);
}

.article-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 2.5rem 0 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border);
}

.nav-prev, .nav-next {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  text-decoration: none;
  color: var(--text);
  background: var(--bg-paper);
  transition: border-color 0.15s;
}

.nav-next { text-align: right; }

.nav-prev:hover, .nav-next:hover {
  border-color: var(--orange);
}

.nav-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.nav-title {
  font-size: 0.85rem;
  line-height: 1.4;
}

.related-posts {
  margin-bottom: 2rem;
}

.related-head, .comments-head {
  font-family: var(--mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.75rem;
  color: var(--text-muted);
}

.related-posts ul {
  list-style: none;
}

.related-posts li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.9rem;
}

.related-posts a {
  color: var(--text);
  text-decoration: none;
}

.related-posts a:hover { color: var(--orange); }

.related-date {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.article-comments {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border);
}

.comments-hint {
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.comments-hint.error { color: #c0392b; }

.content-page :deep(.tk-extras) { display: none; }

.article-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  font-size: 0.9rem;
}

.article-body :deep(th),
.article-body :deep(td) {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--border);
  text-align: left;
}

.article-body :deep(th) {
  background: var(--topbar-bg);
  color: #fff;
  font-family: var(--mono);
  font-size: 0.7rem;
  text-transform: uppercase;
}

.article-body :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
  border: 1px solid var(--border);
}

.article-body :deep(a) {
  color: var(--orange);
}

.article-body :deep(.article-intro) {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed var(--border);
}

.article-body :deep(blockquote) {
  border-left: 3px solid var(--orange);
  padding: 0.75rem 1rem;
  margin: 1rem 0;
  background: var(--orange-light);
  color: var(--text-muted);
}

@media (max-width: 640px) {
  .article-nav { grid-template-columns: 1fr; }
  .nav-next { text-align: left; }
}
</style>

<template>
  <div class="content-page">
    <div
      v-if="!loading && !error"
      class="read-progress"
      :style="{ width: readProgress + '%' }"
      aria-hidden="true"
    />
    <NavBar />
    <main class="page-main">
      <div class="container">
        <div class="content-layout">
          <aside class="toc-sidebar" v-if="tocItems.length > 0">
            <div class="toc">
              <h3>Contents</h3>
              <ul>
                <li v-for="item in tocItems" :key="item.id" :class="'toc-level-' + item.level">
                  <a
                    :href="`#${item.id}`"
                    :class="{ active: activeSection === item.id }"
                    @click.prevent="scrollToSection(item.id)"
                  >
                    {{ item.text }}
                  </a>
                </li>
              </ul>
            </div>
          </aside>

          <div class="article-wrap">
            <div v-if="tocItems.length" class="toc-mobile">
              <button type="button" class="toc-mobile-toggle" @click="tocOpen = !tocOpen">
                目录
                <span class="toc-mobile-icon">{{ tocOpen ? '▲' : '▼' }}</span>
              </button>
              <ul v-show="tocOpen" class="toc-mobile-list">
                <li v-for="item in tocItems" :key="item.id" :class="'toc-level-' + item.level">
                  <a
                    :href="`#${item.id}`"
                    :class="{ active: activeSection === item.id }"
                    @click.prevent="scrollToSection(item.id); tocOpen = false"
                  >
                    {{ item.text }}
                  </a>
                </li>
              </ul>
            </div>

            <div class="article-content">
              <template v-if="!loading && error">
                <SystemHaltPanel
                  :code="haltCode"
                  :message="haltMessage"
                  status="DOC_FAULT"
                  :lines="articleErrorLines"
                  home-label="← 返回首页"
                />
              </template>
              <template v-else>
              <TypewriterTitle :text="articleTitle" :active="!loading && !error" />
              <div class="article-meta-row">
                <div class="article-meta">
                  <span>{{ currentDate }}</span>
                  <span> · {{ articleCategory }}</span>
                  <span v-if="readingMinutes"> · 约 {{ readingMinutes }} 分钟</span>
                  <span v-if="readProgress > 0" class="read-percent"> · 已读 {{ readProgress }}%</span>
                </div>
                <button
                  v-if="!loading"
                  type="button"
                  class="article-copy-link"
                  :class="{ 'article-copy-link--done': copyDone }"
                  @click="copyArticleLink"
                >
                  {{ copyDone ? '已复制 ✓' : '复制链接' }}
                </button>
              </div>
              <div v-if="articleTags.length" class="article-tags">
                <router-link
                  v-for="tag in articleTags"
                  :key="tag"
                  :to="tagUrl(tag)"
                  class="tag-link"
                >#{{ tag }}</router-link>
              </div>
              <div class="article-body" ref="articleBodyRef">
                <p v-if="loading">加载中...</p>
                <div v-else v-html="articleContent"></div>
              </div>
              </template>

              <section v-if="!error && articleSeries.length" class="article-series">
                <h3 class="related-head">所属系列</h3>
                <div
                  v-for="series in articleSeries"
                  :key="series.slug"
                  class="series-inline"
                  :style="{ '--series-accent': series.accent }"
                >
                  <p class="series-inline-title">{{ series.title }} · {{ series.subtitle }}</p>
                  <ol class="series-inline-list">
                    <li
                      v-for="p in series.posts"
                      :key="p.id"
                      :class="{ 'series-inline-current': p.id === Number(postId) }"
                    >
                      <router-link :to="p.url">{{ p.title }}</router-link>
                    </li>
                  </ol>
                </div>
              </section>

              <nav v-if="!error && (adjacent.newer || adjacent.older)" class="article-nav">
                <router-link v-if="adjacent.newer" :to="adjacent.newer.url" class="nav-prev">
                  <span class="nav-label">← 较新</span>
                  <span class="nav-title">{{ adjacent.newer.title }}</span>
                </router-link>
                <router-link v-if="adjacent.older" :to="adjacent.older.url" class="nav-next">
                  <span class="nav-label">较旧 →</span>
                  <span class="nav-title">{{ adjacent.older.title }}</span>
                </router-link>
              </nav>

              <section v-if="!error && relatedPosts.length" class="related-posts">
                <h3 class="related-head">相关文章</h3>
                <ul>
                  <li v-for="p in relatedPosts" :key="p.id">
                    <router-link :to="p.url">{{ p.title }}</router-link>
                    <span class="related-date">{{ p.date }}</span>
                  </li>
                </ul>
              </section>

              <p v-if="!error && readProgress >= 95" class="read-complete">读完 · 100%</p>
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
import TypewriterTitle from '../components/TypewriterTitle.vue'
import SystemHaltPanel from '../components/SystemHaltPanel.vue'
import { ref, computed, watch, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import DOMPurify from 'dompurify'
import {
  getPostById,
  getAdjacentPosts,
  getRelatedPosts,
  getPostCover,
  tagUrl,
} from '../data/posts'
import { getSeriesForPost } from '../data/series'
import { usePageMeta, pageUrl, buildArticleJsonLd, absoluteAssetUrl } from '../composables/usePageMeta'
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
const tocOpen = ref(false)
const articleBodyRef = ref(null)
const adjacent = ref({ newer: null, older: null })
const relatedPosts = ref([])
const readProgress = ref(0)
const copyDone = ref(false)
let observer = null
let scrollHandler = null

const postId = computed(() => route.params.id)
const currentPost = computed(() => getPostById(postId.value))
const articleSeries = computed(() => getSeriesForPost(postId.value))

const articleErrorLines = computed(() => [
  `ERR:: ${error.value || 'DOCUMENT NOT FOUND'}`,
  `ID:: content/${postId.value}`,
  `NODE:: CYINC.LOG / HALT`,
])

const haltCode = computed(() => (error.value?.startsWith('加载失败') ? 'ERR' : '404'))
const haltMessage = computed(() =>
  error.value?.startsWith('加载失败') ? error.value : '文章不存在或已被移除。'
)

const pageMeta = computed(() => {
  const post = currentPost.value
  if (!post) return { title: '文章未找到' }
  const url = pageUrl(`content/${post.id}`)
  const cover = getPostCover(post)
  const image = absoluteAssetUrl(cover)
  return {
    title: post.title,
    description: post.excerpt,
    url,
    type: 'article',
    image,
    jsonLd: buildArticleJsonLd(post, { url, cover }),
  }
})
usePageMeta(pageMeta)

async function copyArticleLink() {
  const post = currentPost.value
  if (!post) return
  const url = pageUrl(`content/${post.id}`)
  try {
    await navigator.clipboard.writeText(url)
    copyDone.value = true
    setTimeout(() => { copyDone.value = false }, 2000)
  } catch {
    window.prompt('复制链接', url)
  }
}

async function loadArticleContent() {
  loading.value = true
  error.value = ''
  articleContent.value = ''
  tocItems.value = []
  readingMinutes.value = 0
  relatedPosts.value = []
  adjacent.value = { newer: null, older: null }
  readProgress.value = 0
  teardownScrollProgress()

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
    const url = `${base}Content/${encodeURIComponent(post.file)}`
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 15000)
    const response = await fetch(url, { signal: controller.signal, cache: 'no-store' })
    clearTimeout(timer)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    let content = await response.text()
    if (
      content.includes('id="loading-screen"')
      && content.includes('id="app"')
      && content.includes('/assets/index-')
    ) {
      throw new Error('HTTP 404')
    }
    content = content.replace(/href="\.\.\//g, `href="${base}`)
    content = content.replace(/href="\.\//g, `href="${base}`)
    content = content.replace(/src="\.\.\//g, `src="${base}`)
    content = content.replace(/src="\.\//g, `src="${base}`)
    articleContent.value = DOMPurify.sanitize(content)
    readingMinutes.value = estimateReadingMinutes(content)
    loading.value = false
    await nextTick()
    await highlightArticle(articleBodyRef.value)
    generateTOC()
    setupIntersectionObserver()
    setupScrollProgress()
    if (route.hash) {
      const id = decodeURIComponent(route.hash.slice(1))
      scrollToSection(id)
    }
    await nextTick()
  } catch (e) {
    console.error('加载文章失败:', e)
    loading.value = false
    const msg = String(e.message || '')
    if (msg.includes('404') || msg.includes('abort')) {
      error.value = '文章正文未找到：请重新上传 docs/Content/ 到 ECS 的 /var/www/cyinc/myweb/Content/'
    } else {
      error.value = `加载失败：${msg || '网络错误'}`
    }
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

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

function scrollToSection(id) {
  const element = document.getElementById(id)
  if (element) {
    const offset = element.getBoundingClientRect().top + window.pageYOffset - 80
    window.scrollTo({ top: offset, behavior: prefersReducedMotion() ? 'auto' : 'smooth' })
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

function setupScrollProgress() {
  teardownScrollProgress()
  scrollHandler = () => {
    const el = articleBodyRef.value
    if (!el) return
    const rect = el.getBoundingClientRect()
    const start = window.scrollY + rect.top - 80
    const end = start + el.offsetHeight - window.innerHeight * 0.35
    if (end <= start) {
      readProgress.value = 100
      return
    }
    const ratio = (window.scrollY - start) / (end - start)
    readProgress.value = Math.min(100, Math.max(0, Math.round(ratio * 100)))
  }
  scrollHandler()
  window.addEventListener('scroll', scrollHandler, { passive: true })
}

function teardownScrollProgress() {
  if (scrollHandler) {
    window.removeEventListener('scroll', scrollHandler)
    scrollHandler = null
  }
}

onMounted(() => loadArticleContent())
watch(postId, () => loadArticleContent())
onUnmounted(() => {
  if (observer) observer.disconnect()
  teardownScrollProgress()
})
</script>

<style scoped>
.read-progress {
  position: fixed;
  top: var(--topbar-height);
  left: 0;
  height: 2px;
  background: var(--orange);
  z-index: 200;
  transition: width 0.12s linear;
  pointer-events: none;
}

.read-percent {
  font-family: var(--mono);
  font-size: 0.75em;
  color: var(--steel);
}

.article-meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.article-copy-link {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.06em;
  padding: 0.3rem 0.65rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--steel);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.article-copy-link:hover,
.article-copy-link--done {
  border-color: var(--orange);
  color: var(--orange);
}

.article-series {
  margin: 2rem 0 1.5rem;
  padding: 1rem 1.1rem;
  border: 1px dashed var(--border);
  background: var(--bg-paper);
}

.series-inline + .series-inline {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--border);
}

.series-inline-title {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--series-accent, var(--orange));
  margin: 0 0 0.65rem;
  letter-spacing: 0.04em;
}

.series-inline-list {
  list-style: none;
  margin: 0;
  padding: 0;
  counter-reset: series-item;
}

.series-inline-list li {
  padding: 0.3rem 0;
  font-size: 0.85rem;
  counter-increment: series-item;
}

.series-inline-list li::before {
  content: counter(series-item, decimal-leading-zero) ' · ';
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
}

.series-inline-list a {
  color: var(--text);
  text-decoration: none;
}

.series-inline-list a:hover {
  color: var(--series-accent, var(--orange));
}

.series-inline-current a {
  color: var(--series-accent, var(--orange));
  font-weight: 500;
}

.read-complete {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--orange);
  letter-spacing: 0.08em;
  margin: 1.5rem 0 0;
  padding: 0.35rem 0.65rem;
  border: 1px dashed var(--orange);
  display: inline-block;
}

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

.related-head {
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

  .related-posts li {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .article-body :deep(table) {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}

.toc-mobile {
  display: none;
  margin-bottom: 1rem;
}

.toc-mobile-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.65rem 0.85rem;
  font-family: var(--mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: var(--topbar-bg);
  color: #fff;
  border: 1px solid var(--border);
  cursor: pointer;
}

.toc-mobile-icon {
  font-size: 0.6rem;
  opacity: 0.7;
}

.toc-mobile-list {
  list-style: none;
  background: var(--bg-paper);
  border: 1px solid var(--border);
  border-top: none;
  max-height: 50vh;
  overflow-y: auto;
}

.toc-mobile-list a {
  display: block;
  font-size: 0.8rem;
  color: var(--text-muted);
  text-decoration: none;
  padding: 0.45rem 0.85rem;
  border-left: 2px solid transparent;
}

.toc-mobile-list a.active,
.toc-mobile-list a:hover {
  color: var(--orange);
  border-left-color: var(--orange);
  background: var(--orange-light);
}

@media (max-width: 768px) {
  .toc-mobile { display: block; }
}
</style>

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
              </div>
              <div class="article-body" ref="articleBodyRef">
                <p v-if="loading">加载中...</p>
                <p v-else-if="error">{{ error }}</p>
                <div v-else v-html="articleContent"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { ref, computed, watch, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPostByTitle } from '../data/posts'

const route = useRoute()
const currentDate = ref('')
const articleCategory = ref('')
const articleTitle = ref('')
const articleContent = ref('')
const loading = ref(true)
const error = ref('')
const tocItems = ref([])
const activeSection = ref('')
const articleBodyRef = ref(null)
let observer = null

const routeTitle = computed(() => {
  try {
    return decodeURIComponent(route.params.id)
  } catch {
    return route.params.id
  }
})

async function loadArticleContent() {
  loading.value = true
  error.value = ''
  articleContent.value = ''
  tocItems.value = []

  const title = routeTitle.value
  const post = getPostByTitle(title)

  if (!post) {
    loading.value = false
    error.value = `文章不存在：${title}`
    articleTitle.value = title
    return
  }

  articleTitle.value = post.title
  currentDate.value = post.date
  articleCategory.value = post.category

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
    loading.value = false
    nextTick(() => {
      generateTOC()
      setupIntersectionObserver()
    })
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
      level: parseInt(heading.tagName.charAt(1))
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
watch(routeTitle, () => loadArticleContent())
onUnmounted(() => { if (observer) observer.disconnect() })
</script>

<style scoped>
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
</style>

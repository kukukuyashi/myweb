<template>
  <div class="content-page">
    <NavBar />
    <main>
      <div class="container">
        <div class="main-wrapper">
          <!-- 目录侧边栏 -->
          <aside class="toc-sidebar" v-if="tocItems.length > 0">
            <div class="toc">
              <h3>目录</h3>
              <ul>
                <li v-for="item in tocItems" :key="item.id" :class="'toc-level-' + item.level">
                  <a @click="scrollToSection(item.id)" :class="{ active: activeSection === item.id }">
                    {{ item.text }}
                  </a>
                </li>
              </ul>
            </div>
          </aside>
          
          <!-- 主内容 -->
          <div id="mainContent">
            <div class="article-content">
              <h1 class="article-title">{{ $route.params.id }}</h1>
              <div class="article-meta">
                <span class="article-date">{{ currentDate }}</span>
                <span class="article-category">技术</span>
              </div>
              <div class="article-body" ref="articleBodyRef">
                <p v-if="articleContent === ''">加载中...</p>
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
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentDate = ref('')
const articleContent = ref('')
const tocItems = ref([])
const activeSection = ref('')
const articleBodyRef = ref(null)
let observer = null



// 文章文件映射 - 键名必须与主页文章标题一致
const articleFiles = {
  '前端核心学习表': '前端核心学习表.html',
  'Vue.js,Three.js和Node.js的区别': 'Vue.js,Three.js和Node.js的区别.html',
  'RhinoWeb的常见问题': 'RhinoWeb的常见问题.html',
  'Vue3学习笔记': 'Vue3学习笔记.html',
  'JS进阶笔记（一）': 'JS进阶1.html',
  'JS进阶笔记（二）': 'JS进阶2.html',
  'JS基础笔记': 'JS基础.html',
  'Web API学习笔记': 'Web API.html',
  'Web API笔记（二）': 'Web API2.html',
  'Web API笔记（三）': 'Web API3.html',
  'Web API笔记（四）': 'Web API4.html'
}

// 加载文章内容
async function loadArticleContent() {
  let articleId = route.params.id
  
  // 解码URL编码的文章ID
  try {
    articleId = decodeURIComponent(articleId)
  } catch (e) {
    console.error('解码文章ID失败:', e)
  }
  
  console.log('文章ID:', articleId)
  
  // 设置当前日期
  const date = new Date()
  currentDate.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  
  // 获取对应的HTML文件名
  const htmlFile = articleFiles[articleId]
  
  if (!htmlFile) {
    articleContent.value = `<p>文章内容不存在</p><p>文章ID: ${articleId}</p><p>可用文章: ${Object.keys(articleFiles).join(', ')}</p>`
    return
  }
  
  try {
    // 从Content目录加载HTML文件
    const response = await fetch(`/myweb/Content/${htmlFile}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    let content = await response.text()
    
    // 修复相对路径链接
    content = content.replace(/href="\.\.\//g, 'href="/')
    content = content.replace(/href="\.\//g, 'href="/')
    content = content.replace(/src="\.\.\//g, 'src="/')
    content = content.replace(/src="\.\//g, 'src="/')
    
    articleContent.value = content
    
    // 等待DOM更新后生成目录
    nextTick(() => {
      generateTOC()
      setupIntersectionObserver()
    })
  } catch (error) {
    console.error('加载文章失败:', error)
    articleContent.value = `<p>加载文章失败: ${error.message}</p><p>文章ID: ${articleId}</p>`
  }
}

// 生成目录
function generateTOC() {
  if (!articleBodyRef.value) return
  
  const headings = articleBodyRef.value.querySelectorAll('h2, h3, h4')
  const items = []
  
  headings.forEach((heading, index) => {
    // 为没有id的标题添加id
    if (!heading.id) {
      heading.id = `section-${index}`
    }
    
    const level = parseInt(heading.tagName.charAt(1))
    items.push({
      id: heading.id,
      text: heading.textContent.trim(),
      level: level
    })
  })
  
  tocItems.value = items
}

// 滚动到指定章节
function scrollToSection(id) {
  const element = document.getElementById(id)
  if (element) {
    const navHeight = 80 // 导航栏高度
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    const offsetPosition = elementPosition - navHeight
    
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
    
    activeSection.value = id
  }
}

// 设置Intersection Observer来跟踪当前章节
function setupIntersectionObserver() {
  if (observer) {
    observer.disconnect()
  }
  
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        activeSection.value = entry.target.id
      }
    })
  }, {
    rootMargin: '-20% 0px -80% 0px',
    threshold: 0
  })
  
  // 观察所有标题
  tocItems.value.forEach(item => {
    const element = document.getElementById(item.id)
    if (element) {
      observer.observe(element)
    }
  })
}

// 初始化
onMounted(() => {
  loadArticleContent()
})

// 清理
onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style>
/* 主内容区样式 */
main {
  padding: 2.5rem 0;
  min-height: 100vh;
  flex: 1;
  background-image: url('../img/1.jfif');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  position: relative;
  margin-left: var(--sidebar-width);
  width: calc(100% - var(--sidebar-width));
  transition: all 0.3s ease;
}

main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 1;
  transition: all 0.3s ease;
}

/* 深色模式样式 */
[data-theme="dark"] main::before {
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

[data-theme="dark"] .sidebar-module {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .sidebar-title {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .stat-item {
  background: rgba(255,255,255,0.05);
}

[data-theme="dark"] .stat-label {
  color: #b0b0b0;
}

[data-theme="dark"] .stat-number {
  color: #4a90e2;
}

[data-theme="dark"] .calendar-nav-btn {
  background: #4a90e2;
}

[data-theme="dark"] .calendar-title {
  color: #ffffff;
}

[data-theme="dark"] .weekday {
  color: #b0b0b0;
}

[data-theme="dark"] .calendar-day {
  color: #ffffff;
}

[data-theme="dark"] .calendar-day:hover:not(.empty) {
  background: rgba(255,255,255,0.1);
}

[data-theme="dark"] #mainContent {
  color: #ffffff;
}

[data-theme="dark"] .article-content {
  background: #1a1a1a;
  box-shadow: 0 6px 24px rgba(0,0,0,0.3);
  border-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .article-content::before {
  background: linear-gradient(90deg, #4a90e2 0%, rgba(74, 144, 226, 0.6) 100%);
}

[data-theme="dark"] .article-title {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

[data-theme="dark"] .article-title::after {
  background: #4a90e2;
}

[data-theme="dark"] .article-meta {
  color: #b0b0b0;
  background: rgba(255,255,255,0.05);
  border-left-color: #4a90e2;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

[data-theme="dark"] .article-body {
  color: #e2e8f0;
}

[data-theme="dark"] .article-body h2 {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

[data-theme="dark"] .article-body h2::before {
  background: linear-gradient(180deg, #4a90e2 0%, rgba(74, 144, 226, 0.3) 100%);
}

[data-theme="dark"] .article-body h3 {
  color: #f39c12;
  background: linear-gradient(135deg, rgba(243,156,18,0.15) 0%, rgba(230,126,34,0.1) 100%);
  border-left-color: #f39c12;
  box-shadow: 0 2px 8px rgba(243,156,18,0.2);
}

[data-theme="dark"] .article-body h3:hover {
  box-shadow: 0 4px 12px rgba(243,156,18,0.3);
}

[data-theme="dark"] .article-body h4 {
  color: #e2e8f0;
  background: rgba(74, 144, 226, 0.05);
  border-left-color: rgba(74, 144, 226, 0.5);
}

[data-theme="dark"] .article-body h5 {
  color: #e2e8f0;
  background: rgba(255,255,255,0.02);
}

[data-theme="dark"] .article-body p {
  color: #e2e8f0;
}

[data-theme="dark"] .article-body ul li {
  color: #e2e8f0;
}

[data-theme="dark"] .article-body ul li::before {
  color: #4a90e2;
}

[data-theme="dark"] .article-body ol li {
  color: #e2e8f0;
}

[data-theme="dark"] .article-body pre {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 2px solid #334155;
  border-left: 4px solid #4a90e2;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .article-body pre:hover {
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
  border-color: #475569;
  border-left-color: #60a5fa;
  background: linear-gradient(135deg, #1e293b 0%, #1a202c 100%);
}

[data-theme="dark"] .article-body code {
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  color: #f687b3;
  border: 1px solid #4a5568;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

[data-theme="dark"] .article-body pre code {
  background: transparent;
  color: #abb2bf;
  border: none;
  box-shadow: none;
}

[data-theme="dark"] .article-body p code,
[data-theme="dark"] .article-body li code,
[data-theme="dark"] .article-body td code {
  background: linear-gradient(135deg, #3d2a32 0%, #2d1f26 100%);
  color: #f687b3;
  border: 1px solid #5a3d47;
  box-shadow: 0 1px 3px rgba(246,135,179,0.15);
}

[data-theme="dark"] .article-body table {
  background: #2d3748;
  border-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .article-body th {
  background: #4a5568;
  color: #e2e8f0;
}

[data-theme="dark"] .article-body td {
  border-bottom-color: #4a5568;
  color: #e2e8f0;
}

[data-theme="dark"] .article-body tr:hover td {
  background: rgba(255,255,255,0.05);
}

[data-theme="dark"] .article-body blockquote {
  background: rgba(45, 55, 72, 0.8);
  border-left-color: #4a90e2;
}

[data-theme="dark"] .article-body strong {
  color: #ffffff;
}

[data-theme="dark"] .article-body a {
  color: #4a90e2;
}

[data-theme="dark"] .article-body a:hover {
  border-bottom-color: #4a90e2;
}

[data-theme="dark"] .article-body .toc,
[data-theme="dark"] .article-body #toc,
[data-theme="dark"] .article-body nav.toc {
  background: rgba(74, 144, 226, 0.1);
  border-left-color: #4a90e2;
}

[data-theme="dark"] .article-body .toc h3,
[data-theme="dark"] .article-body #toc h3 {
  color: #ffffff;
}

[data-theme="dark"] .article-body .toc a,
[data-theme="dark"] .article-body #toc a {
  color: #e2e8f0;
}

[data-theme="dark"] .article-body .toc a:hover,
[data-theme="dark"] .article-body #toc a:hover {
  color: #4a90e2;
}

main > * {
  position: relative;
  z-index: 2;
}

.container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 20px;
}

.main-wrapper {
  margin: 2rem 0;
  display: flex;
  gap: 2rem;
}

/* 目录侧边栏样式 */
.toc-sidebar {
  width: 250px;
  flex-shrink: 0;
  position: sticky;
  top: 100px;
  height: fit-content;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.toc-sidebar .toc {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border: 1px solid rgba(0,0,0,0.05);
}

.toc-sidebar .toc h3 {
  margin: 0 0 1rem 0;
  color: var(--primary-darker);
  font-size: 1.1rem;
  font-weight: 600;
  padding-bottom: 0.8rem;
  border-bottom: 2px solid var(--primary-lighter);
}

.toc-sidebar .toc ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-sidebar .toc li {
  margin-bottom: 0.3rem;
}

.toc-sidebar .toc a {
  color: var(--text-color);
  text-decoration: none;
  display: block;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  cursor: pointer;
}

.toc-sidebar .toc a:hover {
  background: var(--primary-lighter);
  color: var(--primary-color);
}

.toc-sidebar .toc a.active {
  background: var(--primary-color);
  color: white;
}

/* 目录层级缩进 */
.toc-sidebar .toc .toc-level-2 {
  padding-left: 0;
}

.toc-sidebar .toc .toc-level-3 {
  padding-left: 1rem;
}

.toc-sidebar .toc .toc-level-4 {
  padding-left: 2rem;
}

/* 主内容样式 */
#mainContent {
  width: 100%;
}

/* 文章内容样式 */
.article-content {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
  border: 1px solid rgba(0,0,0,0.05);
  position: relative;
  overflow: hidden;
}

.article-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-lighter) 100%);
  border-radius: 16px 16px 0 0;
}

.article-title {
  color: var(--primary-darker);
  border-bottom: 4px solid var(--primary-lighter);
  padding-bottom: 1.5rem;
  margin-bottom: 2.5rem;
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.article-title::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 120px;
  height: 4px;
  background: var(--primary-color);
  border-radius: 2px;
}

.article-meta {
  font-size: 1rem;
  color: var(--text-muted);
  margin-bottom: 3rem;
  display: flex;
  gap: 2rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, var(--primary-lighter) 0%, rgba(100,181,246,0.1) 100%);
  border-radius: 10px;
  border-left: 4px solid var(--primary-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.article-body {
  line-height: 1.8;
  color: var(--text-color);
  font-size: 1.05rem;
  max-width: 800px;
  margin: 0 auto;
}

/* h2 - 主标题 */
.article-body h2 {
  color: var(--primary-color);
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 0.5rem;
}

/* h3 - 次级标题 */
.article-body h3 {
  color: #333;
  margin-top: 1.5rem;
  margin-bottom: 0.8rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.article-body h4 {
  color: var(--primary-color);
  margin-top: 1.2rem;
  margin-bottom: 0.6rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.article-body h5 {
  color: var(--text-color);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
}

.article-body p {
  margin-bottom: 1.2rem;
  line-height: 1.8;
  color: var(--text-color);
}

.article-body ul {
  margin-bottom: 1.2rem;
  padding-left: 1.5rem;
  list-style: disc;
}

.article-body ul li {
  margin-bottom: 0.5rem;
  line-height: 1.7;
  color: var(--text-color);
}

.article-body ol {
  margin-bottom: 1.2rem;
  padding-left: 1.5rem;
  list-style: decimal;
}

.article-body ol li {
  margin-bottom: 0.5rem;
  line-height: 1.7;
  color: var(--text-color);
}

/* 代码块样式 */
.article-body pre {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  overflow-x: auto;
  margin: 2rem auto;
  max-width: 90%;
  position: relative;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  border-left: 4px solid #4a90e2;
}

.article-body pre:hover {
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
  transform: translateY(-2px);
  border-color: #cbd5e1;
  border-left-color: #60a5fa;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.article-body pre::before {
  content: 'CODE';
  position: absolute;
  top: -14px;
  right: 20px;
  background: rgba(255,255,255,0.1);
  color: #94a3b8;
  font-size: 0.8rem;
  padding: 6px 16px;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: 1.5px;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  text-transform: uppercase;
}

.article-body code {
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
  background: linear-gradient(135deg, #f0f4f8 0%, #e8ecf0 100%);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  color: #d63384;
  border: 1px solid #dee2e6;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  font-weight: 500;
}

.article-body pre code {
  background: transparent;
  padding: 0;
  color: #abb2bf;
  font-weight: 400;
  font-size: 0.9rem;
  line-height: 1.6;
  border: none;
  box-shadow: none;
}

.article-body p code,
.article-body li code,
.article-body td code {
  background: linear-gradient(135deg, #fff5f7 0%, #ffe8ef 100%);
  color: #d63384;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: 600;
  border: 1px solid #f8d7da;
  box-shadow: 0 1px 3px rgba(214,51,132,0.1);
}

/* 表格样式 */
.article-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 2rem 0;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  border: 1px solid rgba(0,0,0,0.08);
}

.article-body th,
.article-body td {
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid var(--primary-lighter);
  vertical-align: top;
}

.article-body th {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-lighter) 100%);
  color: var(--primary-darker);
  font-weight: 700;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.article-body tr:last-child td {
  border-bottom: none;
}

.article-body tr:hover td {
  background: linear-gradient(135deg, var(--primary-lighter) 0%, rgba(100,181,246,0.05) 100%);
  transition: all 0.3s ease;
}

/* 引用块样式 */
.article-body blockquote {
  background: #f8fafc;
  border-left: 3px solid var(--primary-color);
  padding: 0.8rem 1rem;
  margin: 1rem 0;
  border-radius: 0 6px 6px 0;
}

.article-body blockquote::before {
  content: '"';
  position: absolute;
  left: -10px;
  top: -5px;
  font-size: 3rem;
  color: var(--primary-color);
  opacity: 0.2;
  font-family: Georgia, serif;
}

/* 图片样式 */
.article-body img {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  margin: 2rem 0;
  box-shadow: 0 6px 20px rgba(0,0,0,0.18);
  transition: all 0.3s ease;
  cursor: pointer;
}

.article-body img:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}

/* 强调文字 */
.article-body strong {
  color: var(--primary-darker);
  font-weight: 600;
}

/* 链接样式 */
.article-body a {
  color: var(--primary-color);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.3s ease;
}

.article-body a:hover {
  border-bottom-color: var(--primary-color);
}

/* 目录样式 */
.article-body .toc,
.article-body #toc,
.article-body nav.toc {
  background: var(--primary-lighter);
  padding: 1.5rem;
  border-radius: 8px;
  margin: 1.5rem 0;
  border-left: 4px solid var(--primary-color);
}

.article-body .toc h3,
.article-body #toc h3 {
  margin-top: 0;
  color: var(--primary-darker);
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.article-body .toc ul,
.article-body #toc ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.article-body .toc li,
.article-body #toc li {
  margin-bottom: 0.5rem;
}

.article-body .toc a,
.article-body #toc a {
  color: var(--text-color);
  text-decoration: none;
  display: block;
  padding: 0.3rem 0;
  transition: color 0.3s ease;
}

.article-body .toc a:hover,
.article-body #toc a:hover {
  color: var(--primary-color);
}

/* 深色模式适配 */
[data-theme="dark"] .article-body code {
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  color: #f687b3;
  border: 1px solid #4a5568;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

[data-theme="dark"] .article-body table {
  background: #2d3748;
}

[data-theme="dark"] .article-body th {
  background: #4a5568;
  color: #e2e8f0;
}

[data-theme="dark"] .article-body td {
  border-bottom-color: #4a5568;
  color: #e2e8f0;
}

[data-theme="dark"] .article-body tr:hover {
  background: #4a5568;
}

[data-theme="dark"] .article-body blockquote {
  background: rgba(45, 55, 72, 0.8);
  border-left-color: var(--primary-color);
}

/* 深色模式 - 目录样式 */
[data-theme="dark"] .toc-sidebar .toc {
  background: #2d3748;
  border-color: #4a5568;
}

[data-theme="dark"] .toc-sidebar .toc h3 {
  color: #e2e8f0;
  border-bottom-color: #4a5568;
}

[data-theme="dark"] .toc-sidebar .toc a {
  color: #e2e8f0;
}

[data-theme="dark"] .toc-sidebar .toc a:hover {
  background: #4a5568;
  color: var(--primary-color);
}

[data-theme="dark"] .toc-sidebar .toc a.active {
  background: var(--primary-color);
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-wrapper {
    flex-direction: column;
  }
  
  .toc-sidebar {
    display: none;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .stats-list {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .article-title {
    font-size: 1.5rem;
  }
  
  .article-content {
    padding: 1rem;
  }
}
</style>
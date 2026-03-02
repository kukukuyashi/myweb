<template>
  <div class="home">
    <NavBar />
    <main>
      <div class="container">
        <div class="main-wrapper">
          <!-- 左侧侧边栏 -->
          <aside class="sidebar">
            <!-- 站点统计模块 -->
            <div class="site-stats sidebar-module">
              <h2 class="sidebar-title">站点统计</h2>
              <div class="stats-list">
                <div class="stat-item">
                  <div class="stat-label">文章</div>
                  <div class="stat-number">{{ totalPosts }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">分类</div>
                  <div class="stat-number">{{ totalCategories }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">标签</div>
                  <div class="stat-number">{{ totalTags }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">总字数</div>
                  <div class="stat-number">{{ totalWords }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">运行时长</div>
                  <div class="stat-number">{{ siteAge }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">最后活动</div>
                  <div class="stat-number">{{ lastActivity }}</div>
                </div>
              </div>
            </div>
            
            <!-- 日历模块 -->
            <div class="calendar sidebar-module">
              <h2 class="sidebar-title">文章日历</h2>
              <div class="calendar-container">
                <div class="calendar-header">
                  <button class="calendar-nav-btn" @click="prevMonth">‹</button>
                  <h3 class="calendar-title">{{ currentMonthText }}</h3>
                  <button class="calendar-nav-btn" @click="nextMonth">›</button>
                </div>
                <div class="calendar-weekdays">
                  <div class="weekday">日</div>
                  <div class="weekday">一</div>
                  <div class="weekday">二</div>
                  <div class="weekday">三</div>
                  <div class="weekday">四</div>
                  <div class="weekday">五</div>
                  <div class="weekday">六</div>
                </div>
                <div class="calendar-days">
                  <div v-for="day in calendarDays" :key="day.id" :class="['calendar-day', { empty: day.empty, today: day.isToday }]">
                    {{ day.day }}
                  </div>
                </div>
              </div>
            </div>
          </aside>
          
          <!-- 右侧主内容 -->
          <div id="mainContent">
            <!-- 最新文章标题和筛选 -->
            <div class="content-header">
              <h1 class="section-title">最新文章</h1>
              <div class="content-filter">
                <div class="category-filter">
                  <span class="filter-label">分类：</span>
                  <button 
                    v-for="category in categories" 
                    :key="category"
                    :class="['filter-btn', { active: selectedCategory === category }]"
                    @click="filterByCategory(category)"
                  >
                    {{ category }}
                  </button>
                </div>
                <div class="search-box">
                  <input 
                    type="text" 
                    placeholder="搜索文章" 
                    class="search-input"
                    v-model="searchQuery"
                    @keyup.enter="searchPosts"
                  >
                  <button class="search-btn" @click="searchPosts">搜索</button>
                </div>
              </div>
            </div>
            
            <!-- 最新文章网格 -->
            <div class="posts-grid">
              <div v-for="post in filteredPosts" :key="post.id" class="post-card">
                <router-link :to="post.url" class="post-card-link">
                  <div class="post-image">
                    <img :src="post.image" :alt="post.title">
                  </div>
                  <div class="post-content">
                    <h3 class="post-title">{{ post.title }}</h3>
                    <div class="post-meta">
                      <span class="post-date">{{ post.date }}</span>
                      <span class="post-category">{{ post.category }}</span>
                    </div>
                    <p class="post-excerpt">{{ post.excerpt }}</p>
                    <div class="post-tags">
                      <span v-for="tag in post.tags" :key="tag" class="tag">{{ tag }}</span>
                    </div>
                  </div>
                </router-link>
              </div>
              <div v-if="filteredPosts.length === 0" class="no-posts">
                <p>没有找到匹配的文章</p>
              </div>
            </div>
            
            <!-- 热门文章 -->
            <div class="hot-posts">
              <h2 class="section-title">热门文章</h2>
              <div class="hot-posts-list">
                <div v-for="(post, index) in hotPosts" :key="post.id" class="hot-post-item">
                  <div class="hot-post-rank">{{ index + 1 }}</div>
                  <div class="hot-post-info">
                    <router-link :to="post.url" class="hot-post-title">{{ post.title }}</router-link>
                    <div class="hot-post-meta">{{ post.date }} · {{ post.category }}</div>
                  </div>
                </div>
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
import { ref, onMounted, computed } from 'vue'

// 图片路径 - 使用绝对路径引用public目录下的资源
const img1 = '/myweb/img/1.jfif'
const img2 = '/myweb/img/2.jfif'
const img3 = '/myweb/img/3.jfif'
const img4 = '/myweb/img/4.jfif'
const img5 = '/myweb/img/5.jfif'

// 日历数据
const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth())
const calendarDays = ref([])
const currentMonthText = ref('')

// 文章数据
const posts = ref([
  {
    id: 1,
    title: '前端核心学习表',
    date: '2026-01-30',
    category: '学习',
    excerpt: '前端开发核心知识点学习表，包含HTML、CSS、JavaScript等核心内容',
    tags: ['前端', '学习', 'HTML', 'CSS', 'JavaScript'],
    url: '/content/前端核心学习表',
    image: img1
  },
  {
    id: 2,
    title: 'Vue.js,Three.js和Node.js的区别',
    date: '2025-12-21',
    category: '技术',
    excerpt: '详细介绍Vue.js、Three.js和Node.js的区别和应用场景',
    tags: ['Vue.js', 'Three.js', 'Node.js', '前端', '技术'],
    url: '/content/Vue.js,Three.js和Node.js的区别',
    image: img2
  },
  {
    id: 3,
    title: 'RhinoWeb的常见问题',
    date: '2025-12-21',
    category: '小知识',
    excerpt: 'RhinoWeb使用过程中常见问题的解决方案',
    tags: ['Rhino', 'Web', '问题解决'],
    url: '/content/RhinoWeb的常见问题',
    image: img3
  },
  {
    id: 4,
    title: 'Vue3学习笔记',
    date: '2025-02-27',
    category: '技术',
    excerpt: 'Vue3核心知识点学习笔记，包含Composition API等新特性',
    tags: ['Vue3', '前端', '技术', '学习'],
    url: '/content/Vue3学习笔记',
    image: img4
  },
  {
    id: 5,
    title: 'JS进阶笔记（一）',
    date: '2025-12-17',
    category: '技术',
    excerpt: 'JavaScript进阶知识点学习笔记，包含闭包、原型链等内容',
    tags: ['JavaScript', '前端', '技术', '学习'],
    url: '/content/JS进阶笔记（一）',
    image: img5
  },
  {
    id: 6,
    title: 'JS进阶笔记（二）',
    date: '2025-12-17',
    category: '技术',
    excerpt: 'JavaScript进阶知识点学习笔记，包含异步编程、Promise等内容',
    tags: ['JavaScript', '前端', '技术', '学习'],
    url: '/content/JS进阶笔记（二）',
    image: '/myweb/img/1.jfif'
  },
  {
    id: 7,
    title: 'Web API学习笔记',
    date: '2025-12-15',
    category: '技术',
    excerpt: 'Web API核心知识点学习笔记，包含DOM操作、事件监听、定时器等内容',
    tags: ['JavaScript', 'Web API', 'DOM', '前端', '技术'],
    url: '/content/Web API学习笔记',
    image: '/myweb/img/2.jfif'
  },
  {
    id: 8,
    title: 'Web API笔记（二）',
    date: '2025-12-16',
    category: '技术',
    excerpt: 'Web API进阶学习笔记，包含事件流、事件委托、页面加载等内容',
    tags: ['JavaScript', 'Web API', '事件', '前端', '技术'],
    url: '/content/Web API笔记（二）',
    image: '/myweb/img/3.jfif'
  },
  {
    id: 9,
    title: 'Web API笔记（三）',
    date: '2025-12-17',
    category: '技术',
    excerpt: 'Web API进阶学习笔记，包含BOM操作、本地存储、正则表达式等内容',
    tags: ['JavaScript', 'Web API', 'BOM', '前端', '技术'],
    url: '/content/Web API笔记（三）',
    image: '/myweb/img/4.jfif'
  },
  {
    id: 10,
    title: 'Web API笔记（四）',
    date: '2025-12-18',
    category: '技术',
    excerpt: 'Web API进阶学习笔记，包含综合案例、实战练习等内容',
    tags: ['JavaScript', 'Web API', '实战', '前端', '技术'],
    url: '/content/Web API笔记（四）',
    image: '/myweb/img/5.jfif'
  },
  {
    id: 11,
    title: 'JS基础笔记',
    date: '2025-12-10',
    category: '技术',
    excerpt: 'JavaScript基础知识点学习笔记，包含变量、数据类型、运算符、流程控制等核心内容',
    tags: ['JavaScript', '前端', '技术', '学习', '基础'],
    url: '/content/JS基础笔记',
    image: '/myweb/img/1.jfif'
  }
])

// 热门文章数据
const hotPosts = ref([
  {
    id: 1,
    title: 'JS进阶笔记（一）',
    date: '2025-12-17',
    category: '技术',
    url: '/content/JS进阶笔记（一）'
  },
  {
    id: 2,
    title: 'Vue3学习笔记',
    date: '2025-02-27',
    category: '技术',
    url: '/content/Vue3学习笔记'
  },
  {
    id: 3,
    title: '前端核心学习表',
    date: '2026-01-30',
    category: '学习',
    url: '/content/前端核心学习表'
  }
])

// 筛选和搜索相关
const selectedCategory = ref('全部')
const searchQuery = ref('')

// 计算属性
const totalPosts = computed(() => posts.value.length)
const totalCategories = computed(() => {
  const categories = new Set()
  posts.value.forEach(post => categories.add(post.category))
  return categories.size
})
const totalTags = computed(() => {
  const tags = new Set()
  posts.value.forEach(post => post.tags.forEach(tag => tags.add(tag)))
  return tags.size
})
const totalWords = computed(() => {
  // 计算总字数（包括标题、摘要和标签）
  let count = 0
  posts.value.forEach(post => {
    // 标题字数
    count += post.title.length
    // 摘要字数
    count += post.excerpt.length
    // 标签字数
    post.tags.forEach(tag => {
      count += tag.length
    })
  })
  
  // 格式化为带千位分隔符的数字
  return count.toLocaleString()
})
// 站点创建日期（可以根据实际情况修改）
const siteStartDate = new Date('2024-01-01')

const siteAge = computed(() => {
  const now = new Date()
  const diffTime = now - siteStartDate
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 30) {
    return `${diffDays}天`
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    const days = diffDays % 30
    return days > 0 ? `${months}个月${days}天` : `${months}个月`
  } else {
    const years = Math.floor(diffDays / 365)
    const months = Math.floor((diffDays % 365) / 30)
    if (months > 0) {
      return `${years}年${months}个月`
    } else {
      return `${years}年`
    }
  }
})

const lastActivity = computed(() => {
  // 获取最后发布的文章日期
  if (posts.value.length === 0) return '暂无文章'
  
  const dates = posts.value.map(post => new Date(post.date))
  const lastDate = new Date(Math.max(...dates))
  const now = new Date()
  const diffTime = now - lastDate
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
    if (diffHours === 0) {
      const diffMinutes = Math.floor(diffTime / (1000 * 60))
      return diffMinutes === 0 ? '刚刚' : `${diffMinutes}分钟前`
    }
    return `${diffHours}小时前`
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks}周前`
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    return `${months}个月前`
  } else {
    const years = Math.floor(diffDays / 365)
    return `${years}年前`
  }
})
const categories = computed(() => {
  const uniqueCategories = new Set(['全部'])
  posts.value.forEach(post => uniqueCategories.add(post.category))
  return Array.from(uniqueCategories)
})
const filteredPosts = computed(() => {
  return posts.value.filter(post => {
    // 分类筛选
    const categoryMatch = selectedCategory.value === '全部' || post.category === selectedCategory.value
    // 搜索筛选
    const searchMatch = !searchQuery.value || 
      post.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      post.excerpt.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      post.tags.some(tag => tag.toLowerCase().includes(searchQuery.value.toLowerCase()))
    return categoryMatch && searchMatch
  })
})

// 方法
function filterByCategory(category) {
  selectedCategory.value = category
}

function searchPosts() {
  // 搜索功能已经通过computed属性实现
  // 这里可以添加额外的搜索逻辑，如排序等
}

// 生成日历
function generateCalendar(year, month) {
  const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  currentMonthText.value = `${year}年${monthNames[month]}`
  
  const days = []
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  
  // 添加空白日期
  for (let i = 0; i < firstDay; i++) {
    days.push({ id: `empty-${i}`, day: '', empty: true, isToday: false })
  }
  
  // 添加当月日期
  for (let day = 1; day <= daysInMonth; day++) {
    const isToday = year === currentDate.getFullYear() && month === currentDate.getMonth() && day === currentDate.getDate()
    days.push({ id: `day-${day}`, day: day, empty: false, isToday: isToday })
  }
  
  calendarDays.value = days
}

// 上一月
function prevMonth() {
  currentMonth.value--
  if (currentMonth.value < 0) {
    currentMonth.value = 11
    currentYear.value--
  }
  generateCalendar(currentYear.value, currentMonth.value)
}

// 下一月
function nextMonth() {
  currentMonth.value++
  if (currentMonth.value > 11) {
    currentMonth.value = 0
    currentYear.value++
  }
  generateCalendar(currentYear.value, currentMonth.value)
}

// 初始化
onMounted(() => {
  generateCalendar(currentYear.value, currentMonth.value)
})
</script>

<style scoped>
/* 主内容区样式 */
main {
  padding: 2.5rem 0;
  min-height: 100vh;
  flex: 1;
  background-image: url('..//myweb/img/1.jfif');
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

[data-theme="dark"] .section-title {
  color: #ffffff;
}

[data-theme="dark"] .filter-label {
  color: #b0b0b0;
}

[data-theme="dark"] .filter-btn {
  background: rgba(255,255,255,0.05);
  border-color: #4a90e2;
  color: #4a90e2;
}

[data-theme="dark"] .filter-btn:hover {
  background: #4a90e2;
  color: white;
}

[data-theme="dark"] .filter-btn.active {
  background: #4a90e2;
  color: white;
}

[data-theme="dark"] .search-input {
  border-color: rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05);
  color: #ffffff;
}

[data-theme="dark"] .search-input:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

[data-theme="dark"] .search-btn {
  background: #4a90e2;
}

[data-theme="dark"] .search-btn:hover {
  background: #3a7bc8;
}

[data-theme="dark"] .post-card {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .post-title {
  color: #ffffff;
}

[data-theme="dark"] .post-meta {
  color: #b0b0b0;
}

[data-theme="dark"] .post-excerpt {
  color: #b0b0b0;
}

[data-theme="dark"] .tag {
  background: rgba(74, 144, 226, 0.2);
  color: #4a90e2;
}

[data-theme="dark"] .hot-posts {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .hot-post-item {
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .hot-post-item:hover {
  background-color: rgba(255,255,255,0.05);
}

[data-theme="dark"] .hot-post-title {
  color: #ffffff;
}

[data-theme="dark"] .hot-post-title:hover {
  color: #4a90e2;
}

[data-theme="dark"] .hot-post-meta {
  color: #b0b0b0;
}

[data-theme="dark"] .no-posts {
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.1);
  color: #b0b0b0;
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
  display: flex;
  gap: 2rem;
}

/* 侧边栏样式 */
.sidebar {
  width: 300px;
  flex-shrink: 0;
}

.sidebar-module {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.sidebar-title {
  color: var(--primary-darker);
  border-bottom: 2px solid var(--primary-lighter);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
}

/* 站点统计样式 */
.stats-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 0.75rem;
  background: var(--primary-lighter);
  border-radius: 8px;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.stat-number {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--primary-color);
}

/* 日历样式 */
.calendar-container {
  width: 100%;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.calendar-nav-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calendar-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-darker);
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.weekday {
  text-align: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  padding: 0.5rem;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.2rem;
}

.calendar-day {
  text-align: center;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.calendar-day:hover:not(.empty) {
  background: var(--primary-lighter);
  transform: scale(1.05);
}

.calendar-day.empty {
  background: transparent;
  cursor: default;
}

.calendar-day.today {
  background: var(--primary-color);
  color: white;
  font-weight: bold;
}

/* 主内容样式 */
#mainContent {
  flex: 1;
}

/* 内容头部样式 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--primary-darker);
  margin: 0;
}

.content-filter {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.category-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.filter-btn {
  background: var(--primary-lighter);
  border: 1px solid var(--primary-color);
  border-radius: 16px;
  padding: 0.3rem 0.8rem;
  font-size: 0.8rem;
  color: var(--primary-darker);
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: var(--primary-color);
  color: white;
}

.filter-btn.active {
  background: var(--primary-color);
  color: white;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.search-input {
  border: 1px solid var(--primary-lighter);
  border-radius: 16px;
  padding: 0.3rem 0.8rem;
  font-size: 0.8rem;
  width: 200px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.search-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 16px;
  padding: 0.3rem 0.8rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: var(--primary-darker);
}

/* 文章列表网格 */
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 40px;
  align-items: start;
  margin-top: 2.5rem;
}

.post-card {
  background: var(--card-background);
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s;
  border: none;
  display: flex;
  flex-direction: column;
  height: 100%;
  animation: slideIn 0.5s ease-out;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
  border-color: var(--primary-lighter);
}

.post-card:nth-child(2) {
  animation-delay: 0.1s;
}

.post-card:nth-child(3) {
  animation-delay: 0.2s;
}

.post-card:nth-child(4) {
  animation-delay: 0.3s;
}

.post-image {
  overflow: hidden;
  display: block;
  margin: 0;
  padding: 0;
  height: 150px;
}

.post-image img {
  width: 100%;
  height: auto;
  object-fit: cover;
  transition: transform 0.3s ease;
  display: block;
  margin: 0;
  padding: 0;
}

.post-card:hover .post-image img {
  transform: scale(1.05);
}

.post-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.post-content {
  padding: 12px;
  width: 100%;
  box-sizing: border-box;
  display: block;
  margin: 0;
}

.post-title {
  font-size: 1.1em;
  margin-bottom: 6px;
  color: var(--primary-darker);
  line-height: 1.3;
}

.post-meta {
  font-size: 0.8em;
  color: var(--text-muted);
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.post-excerpt {
  font-size: 0.9em;
  margin-bottom: 10px;
  color: var(--text-secondary);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
}

/* 热门文章样式 */
.hot-posts {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  padding: 1.5rem;
  margin-top: 2rem;
}

.hot-posts-list {
  margin-top: 1rem;
}

.hot-post-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.hot-post-item:hover {
  background-color: #f9f9f9;
}

.hot-post-item:last-child {
  border-bottom: none;
}

.hot-post-rank {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--primary-color);
  margin-right: 1rem;
  min-width: 24px;
  text-align: center;
}

.hot-post-info {
  flex: 1;
}

.hot-post-title {
  text-decoration: none;
  color: var(--primary-darker);
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.hot-post-title:hover {
  color: var(--primary-color);
}

.hot-post-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

/* 无文章提示样式 */
.no-posts {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  background: #f9f9f9;
  border-radius: 10px;
  border: 2px dashed #e0e0e0;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.no-posts p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-wrapper {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .stats-list {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .content-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .content-filter {
    width: 100%;
    justify-content: space-between;
  }
  
  .category-filter {
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 150px;
  }
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}


</style>
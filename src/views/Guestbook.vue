<template>
  <div class="guestbook">
    <NavBar />
    <main>
      <div class="container">
        <div class="main-wrapper">
          <!-- 侧边栏 -->
          <aside class="sidebar">
            <!-- 站点统计模块 -->
            <div class="site-stats sidebar-module">
              <h2 class="sidebar-title">站点统计</h2>
              <div class="stats-list">
                <div class="stat-item">
                  <div class="stat-label">文章</div>
                  <div class="stat-number">11</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">分类</div>
                  <div class="stat-number">3</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">标签</div>
                  <div class="stat-number">19</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">总字数</div>
                  <div class="stat-number">25,163</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">运行时长</div>
                  <div class="stat-number">120天</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">最后活动</div>
                  <div class="stat-number">15天前</div>
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
          
          <!-- 主内容 -->
          <div id="mainContent">
            <div class="guestbook-content">
              <h1 class="page-title">💬 留言板</h1>
              
              <div class="guestbook-intro">
                <p>欢迎来到留言板！</p>
                <p>在这里你可以留下你的想法、建议、问题，或者只是想打个招呼。我会尽快回复每一条留言。</p>
              </div>

              <blockquote class="guestbook-quote">
                "交流是进步的桥梁，留言是友谊的开始。"
              </blockquote>

              <blockquote class="guestbook-quote">
                "还没做好，不好意思喵"
              </blockquote>

              <!-- Twikoo 评论系统容器 -->
              <div id="tcomment"></div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import NavBar from '../components/Navbar.vue'
import MusicPlayer from '../components/MusicPlayer.vue'

// 日历相关
const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth())

const currentMonthText = computed(() => {
  return `${currentYear.value}年${currentMonth.value + 1}月`
})

const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const startPadding = firstDay.getDay()
  
  // 填充空白
  for (let i = 0; i < startPadding; i++) {
    days.push({ id: `empty-${i}`, empty: true })
  }
  
  // 填充日期
  const today = new Date()
  for (let i = 1; i <= lastDay.getDate(); i++) {
    days.push({
      id: `day-${i}`,
      day: i,
      isToday: today.getFullYear() === currentYear.value && 
               today.getMonth() === currentMonth.value && 
               today.getDate() === i
    })
  }
  
  return days
})

const prevMonth = () => {
  currentMonth.value--
  if (currentMonth.value < 0) {
    currentMonth.value = 11
    currentYear.value--
  }
}

const nextMonth = () => {
  currentMonth.value++
  if (currentMonth.value > 11) {
    currentMonth.value = 0
    currentYear.value++
  }
}

// 加载 Twikoo 评论系统
onMounted(() => {
  // 动态加载 Twikoo JS
  const script = document.createElement('script')
  script.src = 'https://cdn.jsdelivr.net/npm/twikoo@1.6.32/dist/twikoo.all.min.js'
  script.async = true
  script.onload = () => {
    // 初始化 Twikoo
    window.twikoo.init({
      envId: 'your-env-id', // 这里需要替换为你的 Twikoo 环境 ID
      el: '#tcomment',
      lang: 'zh-CN',
    })
  }
  document.body.appendChild(script)
})
</script>

<style scoped>
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
  padding: 0.8rem;
  background: var(--primary-lighter);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
}

.stat-number {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--primary-darker);
}

/* 日历样式 */
.calendar-container {
  padding: 0.5rem;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.calendar-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-darker);
}

.calendar-nav-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--primary-color);
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.calendar-nav-btn:hover {
  background: var(--primary-lighter);
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

.guestbook-content {
  background: white;
  padding: 2.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.page-title {
  color: var(--primary-darker);
  border-bottom: 2px solid var(--primary-lighter);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 600;
}

.guestbook-intro {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--text-color);
  margin-bottom: 1.5rem;
}

.guestbook-intro p {
  margin-bottom: 0.8rem;
}

.guestbook-quote {
  border-left: 4px solid var(--primary-color);
  padding: 1rem 1.5rem;
  margin: 2rem 0;
  background: var(--primary-lighter);
  border-radius: 0 8px 8px 0;
  font-style: italic;
  font-size: 1.1rem;
  color: var(--text-color);
}

/* Twikoo 评论系统容器 */
#tcomment {
  margin-top: 2rem;
  min-height: 300px;
}

/* 深色模式样式 */
[data-theme="dark"] main::before {
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

[data-theme="dark"] .guestbook-content {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .page-title {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .guestbook-intro {
  color: #e2e8f0;
}

[data-theme="dark"] .guestbook-quote {
  border-left-color: #4a90e2;
  background: rgba(74, 144, 226, 0.1);
  color: #e2e8f0;
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
  background: rgba(74, 144, 226, 0.1);
}

[data-theme="dark"] .stat-label {
  color: #b0b0b0;
}

[data-theme="dark"] .stat-number {
  color: #4a90e2;
}

[data-theme="dark"] .calendar-title {
  color: #ffffff;
}

[data-theme="dark"] .calendar-nav-btn {
  color: #4a90e2;
}

[data-theme="dark"] .calendar-nav-btn:hover {
  background: rgba(74, 144, 226, 0.1);
}

[data-theme="dark"] .weekday {
  color: #b0b0b0;
}

[data-theme="dark"] .calendar-day {
  color: #e2e8f0;
}

[data-theme="dark"] .calendar-day:hover:not(.empty) {
  background: rgba(74, 144, 226, 0.1);
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
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .guestbook-content {
    padding: 1.5rem;
  }
}
</style>

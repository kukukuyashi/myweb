<template>
  <div class="archive">
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
            <div class="archive-content">
              <h1 class="page-title">文章归档</h1>
              
              <div class="archive-stats">
                <p>总共 11 篇文章</p>
                <p>最近更新: 2026-01-30</p>
              </div>
              
              <div class="archive-list">
                <h2>2026年</h2>
                <div class="year-group">
                  <h3>1月</h3>
                  <ul class="post-list">
                    <li class="post-item">
                      <router-link to="/content/前端核心学习表" class="post-link">
                        <span class="post-date">2026-01-30</span>
                        <span class="post-title">前端核心学习表</span>
                      </router-link>
                    </li>
                  </ul>
                </div>
                
                <h2>2025年</h2>
                <div class="year-group">
                  <h3>12月</h3>
                  <ul class="post-list">
                    <li class="post-item">
                      <router-link to="/content/Vue.js,Three.js和Node.js的区别" class="post-link">
                        <span class="post-date">2025-12-21</span>
                        <span class="post-title">Vue.js,Three.js和Node.js的区别</span>
                      </router-link>
                    </li>
                    <li class="post-item">
                      <router-link to="/content/RhinoWeb的常见问题" class="post-link">
                        <span class="post-date">2025-12-21</span>
                        <span class="post-title">RhinoWeb的常见问题</span>
                      </router-link>
                    </li>
                    <li class="post-item">
                      <router-link to="/content/JS进阶笔记（一）" class="post-link">
                        <span class="post-date">2025-12-17</span>
                        <span class="post-title">JS进阶笔记（一）</span>
                      </router-link>
                    </li>
                    <li class="post-item">
                      <router-link to="/content/JS进阶笔记（二）" class="post-link">
                        <span class="post-date">2025-12-17</span>
                        <span class="post-title">JS进阶笔记（二）</span>
                      </router-link>
                    </li>
                    <li class="post-item">
                      <router-link to="/content/Web API笔记（三）" class="post-link">
                        <span class="post-date">2025-12-17</span>
                        <span class="post-title">Web API笔记（三）</span>
                      </router-link>
                    </li>
                    <li class="post-item">
                      <router-link to="/content/Web API笔记（四）" class="post-link">
                        <span class="post-date">2025-12-18</span>
                        <span class="post-title">Web API笔记（四）</span>
                      </router-link>
                    </li>
                  </ul>
                </div>
                
                <div class="year-group">
                  <h3>12月</h3>
                  <ul class="post-list">
                    <li class="post-item">
                      <router-link to="/content/Web API学习笔记" class="post-link">
                        <span class="post-date">2025-12-15</span>
                        <span class="post-title">Web API学习笔记</span>
                      </router-link>
                    </li>
                    <li class="post-item">
                      <router-link to="/content/Web API笔记（二）" class="post-link">
                        <span class="post-date">2025-12-16</span>
                        <span class="post-title">Web API笔记（二）</span>
                      </router-link>
                    </li>
                    <li class="post-item">
                      <router-link to="/content/JS基础笔记" class="post-link">
                        <span class="post-date">2025-12-10</span>
                        <span class="post-title">JS基础笔记</span>
                      </router-link>
                    </li>
                  </ul>
                </div>
                
                <div class="year-group">
                  <h3>2月</h3>
                  <ul class="post-list">
                    <li class="post-item">
                      <router-link to="/content/Vue3学习笔记" class="post-link">
                        <span class="post-date">2025-02-27</span>
                        <span class="post-title">Vue3学习笔记</span>
                      </router-link>
                    </li>
                  </ul>
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
import { ref, onMounted } from 'vue'

// 日历数据
const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth())
const calendarDays = ref([])
const currentMonthText = ref('')

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
  background-image: url('/myweb/img/1.jfif');
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

[data-theme="dark"] .page-title {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .archive-content {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .archive-stats {
  background: rgba(74, 144, 226, 0.1);
  color: #b0b0b0;
}

[data-theme="dark"] .archive-list h2 {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .archive-list h3 {
  color: #4a90e2;
  border-left-color: rgba(74, 144, 226, 0.3);
}

[data-theme="dark"] .post-item {
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .post-item:hover {
  background-color: rgba(255,255,255,0.05);
}

[data-theme="dark"] .post-link {
  color: #e2e8f0;
}

[data-theme="dark"] .post-link:hover {
  color: #4a90e2;
}

[data-theme="dark"] .post-date {
  color: #b0b0b0;
}

[data-theme="dark"] .post-title {
  color: #e2e8f0;
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

.page-title {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #2c3e50;
  border-bottom: 2px solid var(--primary-lighter);
  padding-bottom: 1rem;
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--primary-darker);
  margin-bottom: 2.5rem;
}

/* 归档内容样式 */
.archive-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 2rem;
}

.archive-stats {
  background: var(--primary-lighter);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.archive-stats p {
  margin: 0.5rem 0;
}

.archive-list {
  margin-top: 2rem;
}

.archive-list h2 {
  color: var(--primary-darker);
  border-bottom: 2px solid var(--primary-lighter);
  padding-bottom: 0.5rem;
  margin-top: 2rem;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.archive-list h3 {
  color: var(--primary-color);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  padding-left: 1rem;
  border-left: 4px solid var(--primary-lighter);
}

.year-group {
  margin-bottom: 2rem;
}

.post-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.post-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.post-item:hover {
  background-color: #f9f9f9;
}

.post-item:last-child {
  border-bottom: none;
}

.post-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-decoration: none;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.post-link:hover {
  color: var(--primary-color);
}

.post-date {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-right: 1rem;
  min-width: 100px;
}

.post-title {
  font-size: 1rem;
  font-weight: 500;
  flex: 1;
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
  
  .archive-content {
    padding: 1rem;
  }
  
  .post-link {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .post-date {
    margin-bottom: 0.5rem;
  }
}
</style>
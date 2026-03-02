<template>
  <div class="about">
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
            <div class="about-content">
              <h1 class="page-title">关于我</h1>
              
              <h2>欢迎来到 Cyinc 的个人博客</h2>
              <p>这是一个专注于技术分享和个人成长的博客空间。在这里，我会分享我在编程、设计、学习等方面的思考和经验。我相信通过知识的分享和交流，我们能够共同进步，一起成长。</p>
              
              <h3>关于博主</h3>
              <p>我是一名热爱技术的开发者，对前端开发、人工智能和开源项目有着浓厚的兴趣。我相信技术能够改变世界，而分享能够让技术更有价值。</p>
              
              <blockquote>
                "学习是一生的旅程，分享是进步的阶梯。"
              </blockquote>
              
              <h3>技术栈</h3>
              <div class="skills-section">
                <div class="skills-grid">
                  <div class="skill-item">
                    <h4>前端开发</h4>
                    <p>HTML, CSS, JavaScript, Vue.js, React</p>
                  </div>
                  <div class="skill-item">
                    <h4>后端开发</h4>
                    <p>Node.js, Python, PHP</p>
                  </div>
                  <div class="skill-item">
                    <h4>3D图形</h4>
                    <p>Three.js, WebGL</p>
                  </div>
                  <div class="skill-item">
                    <h4>工具</h4>
                    <p>Git, VS Code, Rhino</p>
                  </div>
                </div>
              </div>
              
              <h3>博客特色</h3>
              <ul>
                <li>原创技术文章，分享最新的技术见解和实践经验</li>
                <li>学习笔记整理，帮助初学者快速入门和进阶</li>
                <li>项目经验分享，记录开发过程中的问题和解决方案</li>
                <li>读书心得记录，分享阅读技术书籍的感悟和收获</li>
                <li>代码示例丰富，理论与实践相结合</li>
                <li>持续更新内容，保持技术知识的时效性</li>
              </ul>
              
              <h3>个人理念</h3>
              <p>我相信开源精神，支持技术社区的共同发展。在这个快速变化的技术时代，保持学习的热情和好奇心是非常重要的。通过这个博客，我希望能够：</p>
              <ul>
                <li>记录自己的学习历程，巩固所学知识</li>
                <li>分享实用的技术方案，帮助遇到类似问题的开发者</li>
                <li>与同行交流思想，拓宽技术视野</li>
                <li>培养写作习惯，提升表达能力</li>
              </ul>
              
              <h3>联系方式</h3>
              <div class="contact-info">
                <p>如果您有任何问题、建议或合作意向，欢迎通过以下方式联系我：</p>
                <p>📧 邮箱：<a href="mailto:1344908013@qq.com">1344908013@qq.com</a></p>
                <p>🌐 博客：<a href="https://cyinc.github.io">https://cyinc.github.io</a></p>
              </div>
              
              <h3>未来规划</h3>
              <p>我计划在博客中增加更多内容，包括：</p>
              <ul>
                <li>更多实战项目案例和源码分析</li>
                <li>技术面试题库和解答</li>
                <li>开发工具使用技巧和效率提升方法</li>
                <li>个人成长感悟和职业发展思考</li>
                <li>开源项目介绍和贡献指南</li>
              </ul>
              
              <blockquote>
                "技术不仅仅是工具，更是一种思维方式。让我们一起在技术的道路上不断探索和成长。"
              </blockquote>
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

[data-theme="dark"] .about-content {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .about-content h2 {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .about-content h3 {
  color: #4a90e2;
}

[data-theme="dark"] .about-content p {
  color: #e2e8f0;
}

[data-theme="dark"] .about-content blockquote {
  background: rgba(74, 144, 226, 0.1);
  border-left-color: #4a90e2;
  color: #e2e8f0;
}

[data-theme="dark"] .about-content li {
  color: #e2e8f0;
}

[data-theme="dark"] .about-content li::before {
  color: #4a90e2;
}

[data-theme="dark"] .contact-info {
  background: rgba(74, 144, 226, 0.1);
}

[data-theme="dark"] .contact-info a {
  color: #4a90e2;
}

[data-theme="dark"] .skill-item {
  background: rgba(74, 144, 226, 0.1);
}

[data-theme="dark"] .skill-item h4 {
  color: #ffffff;
}

[data-theme="dark"] .skill-item p {
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
  gap: 0.5rem;
}

.calendar-day {
  text-align: center;
  padding: 0.2rem;
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

/* 关于内容样式 */
.about-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 2rem;
}

.about-content h2 {
  color: var(--primary-darker);
  border-bottom: 2px solid var(--primary-lighter);
  padding-bottom: 0.5rem;
  margin-top: 2rem;
}

.about-content h3 {
  color: var(--primary-color);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.about-content p {
  line-height: 1.8;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.about-content blockquote {
  background: var(--primary-lighter);
  border-left: 4px solid var(--primary-color);
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  font-style: italic;
  border-radius: 4px;
}

.about-content ul {
  list-style: none;
  padding-left: 0;
}

.about-content li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
  color: var(--text-color);
}

.about-content li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: var(--primary-color);
  font-weight: bold;
}

.contact-info {
  background: var(--primary-lighter);
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.contact-info a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
}

.contact-info a:hover {
  text-decoration: underline;
}

.skills-section {
  margin-top: 2rem;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.skill-item {
  background: var(--primary-lighter);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.skill-item h4 {
  color: var(--primary-darker);
  margin: 0 0 0.5rem 0;
}

.skill-item p {
  font-size: 0.9rem;
  color: var(--text-secondary);
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
  
  .skills-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .about-content {
    padding: 1rem;
  }
}
</style>
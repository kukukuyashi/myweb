<template>
  <div class="music">
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
            <div class="music-content">
              <h1 class="page-title">音乐室</h1>
              
              <div class="music-header">
                <h2>♪ 音乐放置处 (Music Room) ♪</h2>
                <p>收录《奇奇怪怪》Cyinc最喜欢的曲目</p>
              </div>
              
              <div class="music-player">
                <div class="player-screen">
                  <div class="player-status">{{ playerStatus }}</div>
                  <div class="player-system">{{ systemStatus }}</div>
                </div>
                
                <div class="player-controls">
                  <button class="control-btn" @click="togglePlay" :disabled="!currentTrack">
                    {{ musicStore.isPlaying ? 'PAUSE' : 'PLAY' }}
                  </button>
                  <button class="control-btn" @click="stopPlay" :disabled="!currentTrack">
                    STOP
                  </button>
                </div>
                
                <table class="music-tracklist">
                  <thead>
                    <tr>
                      <th>NO.</th>
                      <th>TRACK NAME</th>
                      <th>SOURCE</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="(track, index) in tracks" 
                      :key="index"
                      :class="['track-item', { active: currentTrackIndex === index }]"
                      @click="selectTrack(index)"
                    >
                      <td class="track-number">{{ String(index + 1).padStart(2, '0') }}</td>
                      <td class="track-name">{{ track.name }}</td>
                      <td class="track-source">{{ track.source }}</td>
                    </tr>
                  </tbody>
                </table>
                
                <div class="player-info">
                  {{ currentTrack ? 'Now Playing: ' + currentTrack.name : 'Select a track to start playback →' }}
                </div>
              </div>
              
              <div class="music-collection">
                <h3>音乐收藏</h3>
                <div class="collection-grid">
                  <div class="collection-item">
                    <h4>SANABI</h4>
                    <p>游戏原声音乐</p>
                    <p>格式: MP3</p>
                    <p>文件: SANBAI OST - Ending Means Starting Again.mp3</p>
                  </div>
                  <div class="collection-item">
                    <h4>らんま1／2</h4>
                    <p>动画ED主题曲</p>
                    <p>格式: FLAC (Hi-Res)</p>
                    <p>文件: あんたなんて。.flac</p>
                  </div>
                  <div class="collection-item">
                    <h4>小林家的龙女仆</h4>
                    <p>动画原声音乐</p>
                    <p>格式: FLAC</p>
                    <p>文件: 0018865633.flac</p>
                  </div>
                  <div class="collection-item">
                    <h4>超かぐや姫！</h4>
                    <p>动画原声音乐</p>
                    <p>格式: FLAC (Hi-Res)</p>
                    <p>文件: ヤチヨ絵巻.flac</p>
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
import { useMusicStore } from '../store'

const musicStore = useMusicStore()

// 音乐数据
const tracks = ref([
  { name: 'SANBAI OST - Ending Means Starting Again', source: 'Local', url: '/Music/SANABI/SANBAI OST  Ending Means Starting Again.mp3' },
  { name: 'りりあ。 - あんたなんて。', source: 'Local', url: '/Music/[Hi-Res][241013]TVアニメ『らんま1／2』EDテーマ「あんたなんて。」／りりあ。[48kHz／24bit][FLAC]/01.あんたなんて。.flac' },
  { name: '小林家的龙女仆 - 愛のシュプリーム!', source: 'Local', url: '/Music/小林家的龙女仆/0018865633.flac' },
  { name: '超かぐや姫！ - IROHA\'S Dancing All Night', source: 'Local', url: '/Music/[Hi-Res][260123]映画『超かぐや姫！』オリジナル・サウンドトラック[48kHz／24bit][FLAC]/33.ヤチヨ絵巻.flac' },
  { name: '超かぐや姫！ - ヤチヨ絵巻', source: 'Local', url: '/Music/[Hi-Res][260123]映画『超かぐや姫！』オリジナル・サウンドトラック[48kHz／24bit][FLAC]/33.ヤチヨ絵巻.flac' }
])

// 播放器状态
const currentTrackIndex = ref(-1)
const currentTrack = ref(null)
const isPlaying = computed(() => musicStore.isPlaying)
const playerStatus = ref('▶ STOPPED')
const systemStatus = ref('SYSTEM READY...')

// 日历数据
const currentDateObj = new Date()
const currentYear = ref(currentDateObj.getFullYear())
const currentMonth = ref(currentDateObj.getMonth())
const calendarDays = ref([])
const currentMonthText = ref('')

// 生成日历
function generateCalendar(year, month) {
  const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  currentMonthText.value = `${year}年${monthNames[month]}`
  
  const days = []
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  
  for (let i = 0; i < firstDay; i++) {
    days.push({ id: `empty-${i}`, day: '', empty: true, isToday: false })
  }
  
  for (let day = 1; day <= daysInMonth; day++) {
    const isToday = year === currentDateObj.getFullYear() && month === currentDateObj.getMonth() && day === currentDateObj.getDate()
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

// 选择音乐
function selectTrack(index) {
  currentTrackIndex.value = index
  currentTrack.value = tracks.value[index]
  systemStatus.value = 'LOADING TRACK...'
  
  // 设置到全局store
  musicStore.setCurrentSong({
    title: currentTrack.value.name,
    src: currentTrack.value.url
  })
  musicStore.setPlaying(true)
  
  playerStatus.value = '▶ PLAYING'
  systemStatus.value = `NOW PLAYING: ${currentTrack.value.name}`
}

// 播放/暂停
function togglePlay() {
  if (musicStore.isPlaying) {
    musicStore.setPlaying(false)
    playerStatus.value = '▶ PAUSED'
    systemStatus.value = 'PLAYBACK PAUSED'
  } else {
    musicStore.setPlaying(true)
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${currentTrack.value.name}`
  }
}

// 停止播放
function stopPlay() {
  musicStore.setPlaying(false)
  musicStore.setCurrentSong(null)
  playerStatus.value = '▶ STOPPED'
  systemStatus.value = 'PLAYBACK STOPPED'
}

// 初始化
onMounted(() => {
  generateCalendar(currentYear.value, currentMonth.value)
  
  // 如果有正在播放的音乐，更新UI
  if (musicStore.currentSong) {
    const trackIndex = tracks.value.findIndex(t => t.name === musicStore.currentSong.title)
    if (trackIndex !== -1) {
      currentTrackIndex.value = trackIndex
      currentTrack.value = tracks.value[trackIndex]
      playerStatus.value = musicStore.isPlaying ? '▶ PLAYING' : '▶ PAUSED'
      systemStatus.value = `NOW PLAYING: ${currentTrack.value.name}`
    }
  }
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

/* 音乐内容样式 */
.music-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 2rem;
}

.page-title {
  color: var(--primary-darker);
  border-bottom: 2px solid var(--primary-lighter);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
  font-size: 1.8rem;
  font-weight: 600;
}

.music-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--primary-lighter);
  border-radius: 8px;
}

.music-header h2 {
  color: var(--primary-darker);
  margin: 0;
  font-size: 1.5rem;
}

.music-header p {
  color: var(--text-secondary);
  margin: 0.5rem 0 0 0;
  font-style: italic;
}

.music-player {
  margin-bottom: 0;
  background: #f6f8fa;
  border: 2px solid var(--primary-color);
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.player-screen {
  background: #1a202c;
  color: #48bb78;
  font-family: 'Courier New', monospace;
  padding: 1.5rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.player-status {
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.player-system {
  font-size: 1.1rem;
  font-weight: bold;
}

.player-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.control-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover {
  background: var(--primary-darker);
  transform: translateY(-2px);
}

.control-btn:active {
  transform: translateY(0);
}

.control-btn:disabled {
  background: #a0aec0;
  cursor: not-allowed;
  transform: none;
}

.music-tracklist {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.music-tracklist th,
.music-tracklist td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.music-tracklist th {
  background: var(--primary-lighter);
  font-weight: 600;
  color: var(--primary-darker);
}

.music-tracklist tr:hover {
  background: var(--hover-bg);
}

.track-number {
  font-weight: 600;
  color: var(--primary-color);
  min-width: 50px;
}

.track-name {
  font-weight: 500;
  flex: 1;
}

.track-source {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.track-item {
  cursor: pointer;
  transition: all 0.2s ease;
}

.track-item:hover {
  transform: translateX(5px);
}

.track-item.active {
  background: var(--primary-lighter);
  font-weight: 600;
}

.player-info {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-style: italic;
}

.music-collection {
  margin-top: 3rem;
}

.music-collection h3 {
  color: var(--primary-darker);
  margin-bottom: 1rem;
  border-bottom: 2px solid var(--primary-lighter);
  padding-bottom: 0.5rem;
}

.collection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.collection-item {
  background: #f8f9fa;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.collection-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.collection-item h4 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.collection-item p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

/* 深色模式样式 */
[data-theme="dark"] main::before {
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

[data-theme="dark"] .music-content {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

[data-theme="dark"] .page-title {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .music-header {
  background: rgba(74, 144, 226, 0.1);
}

[data-theme="dark"] .music-header h2 {
  color: #ffffff;
}

[data-theme="dark"] .music-header p {
  color: #b0b0b0;
}

[data-theme="dark"] .music-player {
  background: #2d3748;
  border-color: #4a90e2;
}

[data-theme="dark"] .player-screen {
  background: #2d3748;
  color: #68d391;
}

[data-theme="dark"] .control-btn {
  background: #4a90e2;
}

[data-theme="dark"] .control-btn:hover {
  background: #357abd;
}

[data-theme="dark"] .control-btn:disabled {
  background: #4a5568;
}

[data-theme="dark"] .music-tracklist th {
  background: rgba(74, 144, 226, 0.1);
  color: #ffffff;
}

[data-theme="dark"] .music-tracklist td {
  border-bottom-color: rgba(255,255,255,0.1);
  color: #e2e8f0;
}

[data-theme="dark"] .music-tracklist tr:hover {
  background: rgba(74, 144, 226, 0.1);
}

[data-theme="dark"] .track-item.active {
  background: rgba(74, 144, 226, 0.1);
}

[data-theme="dark"] .player-info {
  color: #b0b0b0;
}

[data-theme="dark"] .music-collection h3 {
  color: #ffffff;
  border-bottom-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .collection-item {
  background: #2d3748;
  border-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .collection-item h4 {
  color: #4a90e2;
}

[data-theme="dark"] .collection-item p {
  color: #b0b0b0;
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
  
  .music-content {
    padding: 1rem;
  }
}
</style>

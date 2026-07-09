<template>
  <div class="container layout-single" :class="{ fullscreen: isFullscreen }">
    <header v-if="!isFullscreen" class="pomo-header">
      <p class="coord">POMODORO · V2</p>
      <h1 class="page-title">番茄钟</h1>
    </header>

    <section ref="focusArea" class="card pomo-core" :class="{ 'fs-mode': isFullscreen }">
      <div class="top-row">
        <p class="mode-label">{{ modeLabel }}</p>
        <div class="top-actions">
          <button type="button" class="icon-btn" title="设置" @click="showSettings = !showSettings">⚙</button>
          <button type="button" class="icon-btn" title="全屏专注" @click="toggleFullscreen">⛶</button>
        </div>
      </div>

      <div class="ring-wrap">
        <svg class="ring" viewBox="0 0 120 120" aria-hidden="true">
          <circle class="ring-bg" cx="60" cy="60" r="52" />
          <circle
            class="ring-progress"
            cx="60"
            cy="60"
            r="52"
            :style="{ strokeDashoffset: ringOffset }"
          />
        </svg>
        <div class="timer-display">{{ displayTime }}</div>
      </div>

      <label v-if="mode === 'focus'" class="task-label">
        任务（可选）
        <input v-model="taskLabel" placeholder="例如：写论坛 MVP" maxlength="200" :disabled="running" />
      </label>

      <div class="timer-actions">
        <button type="button" class="btn-primary" @click="toggleTimer">
          {{ running ? '暂停' : secondsLeft === totalSeconds ? '开始' : '继续' }}
        </button>
        <button type="button" class="btn-ghost" @click="resetTimer">重置</button>
        <button type="button" class="btn-ghost" @click="switchMode">
          切换{{ mode === 'focus' ? '休息' : '专注' }}
        </button>
      </div>

      <p v-if="!token" class="warn">
        未登录：专注完成后无法保存。
        <router-link to="/app/me">去登录</router-link>
      </p>
      <p v-if="message" class="success">{{ message }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section v-if="showSettings && !isFullscreen" class="card settings">
      <h2>计时设置</h2>
      <div class="settings-grid">
        <label>专注（分钟）<input v-model.number="settings.focusMin" type="number" min="1" max="120" /></label>
        <label>短休（分钟）<input v-model.number="settings.breakMin" type="number" min="1" max="60" /></label>
        <label>长休（分钟）<input v-model.number="settings.longBreakMin" type="number" min="1" max="60" /></label>
        <label>长休间隔（轮）<input v-model.number="settings.cyclesBeforeLongBreak" type="number" min="2" max="10" /></label>
      </div>
      <label class="notify-row">
        <input v-model="settings.notify" type="checkbox" />
        完成时浏览器通知
      </label>
      <button type="button" class="btn-ghost" @click="saveSettings">保存设置</button>
    </section>

    <section v-if="token && stats && !isFullscreen" class="card pomo-stats">
      <h2>统计</h2>
      <div class="stats-grid">
        <div><span class="stat-num">{{ stats.today_minutes }}</span><span class="stat-label">今日分钟</span></div>
        <div><span class="stat-num">{{ stats.today_sessions }}</span><span class="stat-label">今日次数</span></div>
        <div><span class="stat-num">{{ stats.week_minutes }}</span><span class="stat-label">本周分钟</span></div>
        <div><span class="stat-num">{{ stats.week_sessions }}</span><span class="stat-label">本周次数</span></div>
      </div>
    </section>

    <section v-if="token && !isFullscreen" class="card week-chart">
      <h2>本周专注</h2>
      <div class="chart-bars">
        <div v-for="bar in weekBars" :key="bar.label" class="bar-col">
          <div class="bar" :style="{ height: bar.height + '%' }" :title="`${bar.minutes} 分钟`" />
          <span class="bar-label">{{ bar.label }}</span>
        </div>
      </div>
    </section>

    <div v-if="showReflection" class="modal-overlay" @click.self="skipReflection">
      <div class="modal card">
        <h2>本段专注结束了</h2>
        <p class="modal-desc">这段时间你学了 / 做了什么？简单总结一下：</p>
        <textarea v-model="reflectionText" rows="4" maxlength="5000" placeholder="例如：完成了论坛 API 的 CRUD…" />
        <div class="modal-actions">
          <button type="button" class="btn-ghost" @click="skipReflection">跳过</button>
          <button type="button" class="btn-primary" :disabled="savingReflection" @click="submitReflection">
            保存并继续
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { usePageMeta } from '../composables/usePageMeta'
import {
  createPomodoroSession,
  fetchPomodoroSessions,
  fetchPomodoroStats,
  getPlatformToken,
} from '../api/platform.js'

usePageMeta({
  title: '番茄钟',
  description: 'CYINC 番茄钟 v2：圆环计时、反思总结与统计。',
})

const SETTINGS_KEY = 'cyinc_pomo_settings'
const RING_C = 2 * Math.PI * 52

const token = ref(getPlatformToken())
const mode = ref('focus')
const focusCount = ref(0)
const totalSeconds = ref(25 * 60)
const secondsLeft = ref(25 * 60)
const running = ref(false)
const taskLabel = ref('')
const stats = ref(null)
const sessions = ref([])
const error = ref('')
const message = ref('')
const showSettings = ref(false)
const isFullscreen = ref(false)
const focusArea = ref(null)
const showReflection = ref(false)
const reflectionText = ref('')
const savingReflection = ref(false)
const pendingSession = ref(null)
let tickId = null

const settings = ref(loadSettings())

function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY)
    const parsed = raw ? JSON.parse(raw) : {}
    return {
      focusMin: parsed.focusMin ?? 25,
      breakMin: parsed.breakMin ?? 5,
      longBreakMin: parsed.longBreakMin ?? 15,
      cyclesBeforeLongBreak: parsed.cyclesBeforeLongBreak ?? 4,
      notify: parsed.notify ?? false,
    }
  } catch {
    return { focusMin: 25, breakMin: 5, longBreakMin: 15, cyclesBeforeLongBreak: 4, notify: false }
  }
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings.value))
  if (!running.value) applyModeDuration()
  showSettings.value = false
  message.value = '设置已保存'
}

const modeLabel = computed(() => {
  if (mode.value === 'focus') return '专注中'
  return focusCount.value % settings.value.cyclesBeforeLongBreak === 0 ? '长休息' : '短休息'
})

const displayTime = computed(() => {
  const m = Math.floor(secondsLeft.value / 60)
  const s = secondsLeft.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const ringOffset = computed(() => {
  const progress = totalSeconds.value ? secondsLeft.value / totalSeconds.value : 0
  return `${RING_C * (1 - progress)}`
})

const weekBars = computed(() => {
  const labels = ['一', '二', '三', '四', '五', '六', '日']
  const now = new Date()
  const dayIdx = (now.getDay() + 6) % 7
  const start = new Date(now)
  start.setHours(0, 0, 0, 0)
  start.setDate(start.getDate() - dayIdx)

  const minsByDay = Array(7).fill(0)
  for (const s of sessions.value) {
    if (s.session_type !== 'focus') continue
    const d = new Date(s.completed_at)
    const diff = Math.floor((d - start) / 86400000)
    if (diff >= 0 && diff < 7) minsByDay[diff] += s.duration_sec / 60
  }
  const max = Math.max(...minsByDay, 1)
  return labels.map((label, i) => ({
    label,
    minutes: Math.round(minsByDay[i]),
    height: Math.round((minsByDay[i] / max) * 100),
  }))
})

function applyModeDuration() {
  if (mode.value === 'focus') {
    totalSeconds.value = settings.value.focusMin * 60
  } else if (focusCount.value > 0 && focusCount.value % settings.value.cyclesBeforeLongBreak === 0) {
    totalSeconds.value = settings.value.longBreakMin * 60
  } else {
    totalSeconds.value = settings.value.breakMin * 60
  }
  secondsLeft.value = totalSeconds.value
}

function clearTick() {
  if (tickId) {
    clearInterval(tickId)
    tickId = null
  }
}

function resetTimer() {
  clearTick()
  running.value = false
  applyModeDuration()
}

function switchMode() {
  clearTick()
  running.value = false
  mode.value = mode.value === 'focus' ? 'break' : 'focus'
  applyModeDuration()
}

function maybeNotify(title, body) {
  if (!settings.value.notify || !('Notification' in window)) return
  if (Notification.permission === 'granted') {
    new Notification(title, { body })
  }
}

async function requestNotifyPermission() {
  if (!settings.value.notify || !('Notification' in window)) return
  if (Notification.permission === 'default') {
    await Notification.requestPermission()
  }
}

function toggleTimer() {
  if (running.value) {
    clearTick()
    running.value = false
    return
  }
  requestNotifyPermission()
  running.value = true
  tickId = setInterval(async () => {
    if (secondsLeft.value <= 1) {
      clearTick()
      running.value = false
      const completedSec = totalSeconds.value
      secondsLeft.value = 0
      await onSessionComplete(completedSec)
      return
    }
    secondsLeft.value -= 1
  }, 1000)
}

async function onSessionComplete(durationSec) {
  if (mode.value === 'focus') {
    maybeNotify('专注完成', '休息一下，或填写本段反思。')
    focusCount.value += 1
    if (token.value) {
      pendingSession.value = {
        duration_sec: durationSec,
        task_label: taskLabel.value.trim() || null,
        session_type: 'focus',
      }
      reflectionText.value = ''
      showReflection.value = true
    } else {
      message.value = '专注完成！'
      enterBreak()
    }
  } else {
    maybeNotify('休息结束', '准备好开始下一段专注了吗？')
    message.value = '休息结束'
    mode.value = 'focus'
    applyModeDuration()
  }
}

function enterBreak() {
  mode.value = 'break'
  applyModeDuration()
}

async function submitReflection() {
  if (!pendingSession.value) {
    showReflection.value = false
    enterBreak()
    return
  }
  savingReflection.value = true
  error.value = ''
  try {
    await createPomodoroSession({
      ...pendingSession.value,
      reflection: reflectionText.value.trim() || null,
    })
    message.value = '专注完成，已保存记录与反思'
    taskLabel.value = ''
    pendingSession.value = null
    showReflection.value = false
    await loadData()
    enterBreak()
  } catch (e) {
    error.value = e.message
  } finally {
    savingReflection.value = false
  }
}

function skipReflection() {
  if (pendingSession.value && token.value) {
    createPomodoroSession(pendingSession.value).then(() => {
      message.value = '专注完成，已保存记录'
      loadData()
    }).catch((e) => { error.value = e.message })
  }
  pendingSession.value = null
  showReflection.value = false
  taskLabel.value = ''
  enterBreak()
}

async function toggleFullscreen() {
  if (!document.fullscreenElement) {
    await focusArea.value?.requestFullscreen?.()
    isFullscreen.value = true
  } else {
    await document.exitFullscreen()
    isFullscreen.value = false
  }
}

function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

async function loadData() {
  if (!token.value) return
  try {
    const [statsJson, sessionsJson] = await Promise.all([
      fetchPomodoroStats(),
      fetchPomodoroSessions(1, 50),
    ])
    stats.value = statsJson.data
    sessions.value = sessionsJson.data.items || []
  } catch (e) {
    error.value = e.message
  }
}

watch(settings, () => {
  if (settings.value.notify) requestNotifyPermission()
}, { deep: true })

onMounted(() => {
  applyModeDuration()
  loadData()
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onUnmounted(() => {
  clearTick()
  document.removeEventListener('fullscreenchange', onFullscreenChange)
})
</script>

<style scoped>
.coord {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  letter-spacing: 0.12em;
}

.card {
  margin-top: 1rem;
  border: 1px solid var(--border);
  background: var(--card-bg, #fff);
  padding: 1.25rem;
}

.pomo-core.fs-mode {
  min-height: 100vh;
  margin: 0;
  border: none;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.mode-label {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.top-actions { display: flex; gap: 0.35rem; }

.icon-btn {
  background: transparent;
  border: 1px solid var(--border);
  width: 32px;
  height: 32px;
  cursor: pointer;
}

.ring-wrap {
  position: relative;
  width: min(280px, 70vw);
  aspect-ratio: 1;
  margin: 1rem auto;
}

.ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: var(--border);
  stroke-width: 8;
}

.ring-progress {
  fill: none;
  stroke: var(--orange);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 326.73;
  transition: stroke-dashoffset 0.3s linear;
}

.timer-display {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  font-size: clamp(2.5rem, 10vw, 3.5rem);
  color: var(--orange);
}

.task-label {
  display: grid;
  gap: 0.35rem;
  font-family: var(--mono);
  font-size: 0.78rem;
  margin-bottom: 1rem;
  max-width: 360px;
  width: 100%;
}

.task-label input {
  border: 1px solid var(--border);
  padding: 0.55rem 0.65rem;
  font: inherit;
  background: var(--bg);
}

.timer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.btn-primary, .btn-ghost {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border: 1px solid var(--border);
}

.btn-primary {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.settings h2, .pomo-stats h2, .week-chart h2 {
  font-size: 0.95rem;
  margin: 0 0 0.75rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.settings-grid label, .notify-row {
  font-family: var(--mono);
  font-size: 0.75rem;
  display: grid;
  gap: 0.35rem;
}

.settings-grid input[type="number"] {
  border: 1px solid var(--border);
  padding: 0.45rem;
  font: inherit;
  background: var(--bg);
}

.notify-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.75rem 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  text-align: center;
}

.stat-num {
  display: block;
  font-family: var(--mono);
  font-size: 1.5rem;
  color: var(--orange);
}

.stat-label { font-size: 0.72rem; color: var(--text-muted); }

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  height: 120px;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar {
  width: 100%;
  max-width: 36px;
  margin-top: auto;
  background: var(--orange);
  min-height: 4px;
  border-radius: 2px 2px 0 0;
  transition: height 0.3s;
}

.bar-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal {
  width: min(480px, 100%);
  margin: 0;
}

.modal-desc {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.modal textarea {
  width: 100%;
  border: 1px solid var(--border);
  padding: 0.65rem;
  font: inherit;
  background: var(--bg);
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.warn { margin-top: 1rem; font-size: 0.82rem; color: #b45309; }
.warn a { color: var(--orange); }
.error { color: #c0392b; font-size: 0.82rem; margin-top: 0.5rem; }
.success { color: #2d6a4f; font-size: 0.82rem; margin-top: 0.5rem; }

@media (max-width: 560px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .settings-grid { grid-template-columns: 1fr; }
}
</style>

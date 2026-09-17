<template>
  <section
    class="focus-room"
    :class="[`focus-room--${currentMode}`, { 'focus-room--running': isRunning, 'focus-room--immersive': immersive }]"
  >
    <Transition name="focus-background-fade">
      <video
        :key="backgroundVideo"
        class="focus-background"
        :src="backgroundVideo"
        :poster="backgroundPoster"
        autoplay
        muted
        loop
        playsinline
        preload="auto"
        aria-hidden="true"
      ></video>
    </Transition>
    <div class="focus-overlay" aria-hidden="true"></div>
    <div class="focus-aura" aria-hidden="true"></div>

    <header class="focus-topbar">
      <div class="focus-brand">
        <span class="focus-brand__mark" aria-hidden="true">C</span>
        <div>
          <p>CYINC FOCUS · {{ backgroundLabel }}</p>
          <strong>{{ currentModeLabel }} · 第 {{ currentCycle }} 轮</strong>
        </div>
      </div>
      <div class="focus-top-actions">
        <button
          type="button"
          class="focus-presence"
          :title="`当前 ${onlineCount} 人在线${adminOnline ? '，站长也在' : ''} · 点击打开月读聊天`"
          aria-label="在线状态，点击打开聊天室"
          @click="chatWindowOpen = true"
        >
          <i class="focus-presence__dot" :class="{ live: onlineCount > 0 }" aria-hidden="true"></i>
          <span>{{ onlineCount }} 在线</span>
          <i class="focus-presence__dot" :class="{ live: adminOnline }" aria-hidden="true"></i>
          <span class="focus-presence__admin">站长</span>
        </button>
        <button
          v-if="!rhythmWindowOpen"
          type="button"
          class="focus-top-button"
          aria-label="打开专注节奏窗口"
          title="打开专注节奏窗口"
          @click="rhythmWindowOpen = true"
        >
          <span aria-hidden="true">◔</span>
        </button>
        <button
          type="button"
          class="focus-top-button"
          :class="{ active: chatWindowOpen }"
          :aria-label="chatWindowOpen ? '关闭月读聊天窗口' : '打开月读聊天窗口'"
          :title="chatWindowOpen ? '关闭月读聊天窗口' : '打开月读聊天窗口'"
          @click="chatWindowOpen = !chatWindowOpen"
        >
          <span aria-hidden="true">💬</span>
        </button>
        <button
          type="button"
          class="focus-top-button"
          aria-label="数据与设置"
          title="数据与设置"
          @click="settingsOpen = true"
        >
          <span aria-hidden="true">⚙</span>
        </button>
        <button
          type="button"
          class="focus-top-button"
          :class="{ active: musicWindowOpen }"
          :aria-label="musicWindowOpen ? '关闭音乐面板' : '打开音乐面板'"
          :title="musicWindowOpen ? '关闭音乐面板' : '音乐面板'"
          @click="musicWindowOpen = !musicWindowOpen"
        >
          <span aria-hidden="true">{{ musicStore.isPlaying ? '⏸' : '♪' }}</span>
        </button>
        <RouterLink class="focus-top-button" to="/app" aria-label="返回主站" title="返回主站">
          <span aria-hidden="true">↩</span>
        </RouterLink>
        <button
          type="button"
          class="focus-top-button"
          :aria-label="isFullscreen ? '退出全屏' : '进入全屏'"
          :title="isFullscreen ? '退出全屏' : '进入全屏'"
          @click="toggleFullscreen"
        >
          <span aria-hidden="true">⛶</span>
        </button>
      </div>
    </header>

    <main class="focus-shell">
      <section class="focus-primary">
        <div class="focus-timer" aria-label="专注计时器">
          <svg class="focus-ring" viewBox="0 0 300 300" aria-hidden="true">
            <circle class="focus-ring__aura" cx="150" cy="150" r="126" />
            <g class="focus-ring__ticks">
              <line
                v-for="tick in 60"
                :key="tick"
                x1="150"
                :y1="12 + (tick % 5 === 0 ? 0 : 5)"
                x2="150"
                :y2="12 + (tick % 5 === 0 ? 12 : 10)"
                :transform="`rotate(${(tick - 1) * 6} 150 150)`"
              />
            </g>
            <circle class="focus-ring__track" cx="150" cy="150" r="112" />
            <circle
              class="focus-ring__progress"
              cx="150"
              cy="150"
              r="112"
              :stroke-dasharray="ringCircumference"
              :stroke-dashoffset="ringOffset"
            />
          </svg>

          <div class="focus-time">
            <small>{{ isRunning ? 'FOCUSING' : 'READY' }}</small>
            <strong>{{ formattedTime }}</strong>
            <span>{{ currentModeLabel }} · {{ Math.round(progress * 100) }}%</span>
          </div>
        </div>

        <div class="focus-controls">
          <button
            type="button"
            class="focus-toggle"
            :aria-label="isRunning ? '暂停专注' : '开始专注'"
            @click="toggleTimer"
          >
            <span aria-hidden="true">{{ isRunning ? '⏸' : '▶' }}</span>
            {{ isRunning ? '暂停' : '开始' }}
          </button>
        </div>
      </section>

      <FloatingWindow
        v-if="rhythmWindowOpen"
        class="focus-rhythm-window"
        eyebrow="POMODORO RHYTHM"
        title="专注节奏"
        @close="rhythmWindowOpen = false"
      >
        <div class="focus-rhythm">
          <div class="focus-rhythm__summary">
            <span>当前</span>
            <strong>{{ currentModeLabel }}</strong>
            <small>第 {{ currentCycle }} 轮</small>
          </div>
          <div class="focus-modes" role="tablist" aria-label="专注节奏">
          <button
            v-for="mode in modes"
            :key="mode.key"
            type="button"
            :class="{ active: currentMode === mode.key }"
            @click="selectMode(mode.key)"
          >
            {{ mode.label }}
            <small>{{ settings[mode.key] }} 分钟</small>
          </button>
          </div>

          <div class="focus-task">
            <input
              v-model="taskLabel"
              maxlength="60"
              placeholder="这一轮要专注的一件事"
              aria-label="当前专注任务"
              @focus="taskFocused = true"
              @blur="taskFocused = false"
            >
            <p>{{ message }}</p>
          </div>
        </div>
      </FloatingWindow>

      <FloatingWindow
        v-if="chatWindowOpen"
        class="focus-chat-window"
        eyebrow="CHAT · CONNECTED"
        title="月读"
        :width="390"
        :height="480"
        :min-width="320"
        :min-height="320"
        @close="chatWindowOpen = false"
      >
        <StudyRoomChatPanel />
      </FloatingWindow>

      <FloatingWindow
        v-if="musicWindowOpen"
        class="focus-music-window"
        eyebrow="MUSIC"
        title="背景音乐"
        :width="340"
        :height="430"
        :min-width="300"
        :min-height="340"
        @close="musicWindowOpen = false"
      >
        <div class="focus-music-panel">
          <div class="focus-music-panel__now">
            <span class="focus-music-panel__state" :class="{ playing: musicStore.isPlaying }">
              {{ musicStore.isPlaying ? '▶' : '❚❚' }}
            </span>
            <p :title="musicStore.currentSong?.title">
              {{ musicStore.currentSong?.title || '未选曲 · 从下方列表挑一首' }}
            </p>
          </div>

          <div class="focus-music-panel__seek">
            <span>{{ fmtMusicTime(musicStore.currentTime) }}</span>
            <input
              type="range"
              min="0"
              :max="musicStore.duration || 0"
              step="0.1"
              :value="musicStore.currentTime"
              :disabled="!musicStore.duration"
              aria-label="播放进度"
              @input="onMusicSeekInput"
              @change="onMusicSeekEnd"
            >
            <span>{{ fmtMusicTime(musicStore.duration) }}</span>
          </div>

          <div class="focus-music-panel__controls">
            <button
              type="button"
              :disabled="!musicStore.hasPrev()"
              aria-label="上一首"
              @click="playPrevTrack"
            >⏮</button>
            <button
              type="button"
              class="focus-music-panel__play"
              :aria-label="musicStore.isPlaying ? '暂停' : '播放'"
              @click="toggleMusic"
            >{{ musicStore.isPlaying ? '⏸' : '▶' }}</button>
            <button
              type="button"
              :disabled="!musicStore.hasNext()"
              aria-label="下一首"
              @click="playNextTrack"
            >⏭</button>
          </div>

          <label class="focus-music-panel__vol">
            <span>音量 {{ musicVolumePercent }}%</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              :value="musicStore.volume"
              aria-label="音量"
              @input="setMusicVolume"
            >
          </label>

          <div class="focus-music-panel__list">
            <template v-for="group in musicGroups" :key="group.source">
              <p class="focus-music-panel__album">{{ group.source }}</p>
              <button
                v-for="track in group.tracks"
                :key="track.index"
                type="button"
                class="focus-music-panel__track"
                :class="{ active: track.index === musicStore.currentIndex }"
                @click="playMusicTrack(track.index)"
              >
                <span>{{ track.name }}</span>
                <i v-if="track.index === musicStore.currentIndex && musicStore.isPlaying" aria-hidden="true">▶</i>
              </button>
            </template>
          </div>
        </div>
      </FloatingWindow>
    </main>

    <button
      type="button"
      class="focus-bg-arrow focus-bg-arrow--prev"
      :aria-label="`上一张背景，当前：${backgroundLabel}`"
      title="上一张背景"
      @click="switchBackground(-1)"
    >
      <span aria-hidden="true">‹</span>
    </button>
    <button
      type="button"
      class="focus-bg-arrow focus-bg-arrow--next"
      :aria-label="`下一张背景，当前：${backgroundLabel}`"
      title="下一张背景"
      @click="switchBackground(1)"
    >
      <span aria-hidden="true">›</span>
    </button>

    <p v-if="immersive" class="focus-immersive-hint">移动鼠标显示控件</p>

    <div v-if="immersive" class="focus-immersive-capsule" aria-live="polite">
      <strong>{{ formattedTime }}</strong>
      <span>{{ currentModeLabel }}</span>
      <i><b :style="{ width: `${Math.round(progress * 100)}%` }"></b></i>
    </div>

    <Teleport to="body">
      <div v-if="settingsOpen" class="focus-modal-backdrop" @click.self="settingsOpen = false">
        <section class="focus-modal" aria-label="专注数据与设置">
          <header class="focus-modal__head">
            <div>
              <p>FOCUS DASHBOARD</p>
              <h2>数据与设置</h2>
            </div>
            <div class="focus-modal__actions">
              <button type="button" @click="resetTimer">重置计时</button>
              <button type="button" @click="skipPhase">跳过阶段</button>
              <button type="button" aria-label="关闭" title="关闭" @click="settingsOpen = false">
                <span aria-hidden="true">✕</span>
              </button>
            </div>
          </header>
          <div class="focus-modal__body">
            <section class="focus-panel focus-panel--wide">
              <h3>今日数据</h3>
              <div class="focus-stats">
                <div><strong>{{ stats.todayMinutes }}</strong><span>分钟</span></div>
                <div><strong>{{ stats.todaySessions }}</strong><span>番茄</span></div>
                <div><strong>{{ stats.weekMinutes }}</strong><span>本周分钟</span></div>
              </div>
              <p class="focus-hint">{{ isLoggedIn ? '数据已同步到账号' : '登录后可同步专注记录' }}</p>
            </section>

            <section class="focus-panel focus-panel--wide">
              <h3>专注热力图</h3>
              <div class="focus-heatmap">
                <span
                  v-for="day in heatmapDays"
                  :key="day.date"
                  class="focus-heatmap__cell"
                  :class="`level-${day.level}`"
                  :title="`${day.date} · ${day.minutes} 分钟`"
                ></span>
              </div>
              <p class="focus-hint">最近 12 周专注分布</p>
            </section>

            <section class="focus-panel">
              <h3>今日任务与目标</h3>
              <div class="focus-goal">
                <span>番茄目标</span>
                <strong>{{ stats.todaySessions }} / {{ dailyGoal }}</strong>
              </div>
              <div class="focus-progress"><i :style="{ width: goalProgressWidth }"></i></div>
              <div class="focus-task-list">
                <label v-for="task in tasks" :key="task.id" class="focus-task-item">
                  <input v-model="task.done" type="checkbox">
                  <span :class="{ done: task.done }">{{ task.label }}</span>
                  <button type="button" aria-label="删除任务" title="删除任务" @click="removeTask(task.id)">
                    <span aria-hidden="true">✕</span>
                  </button>
                </label>
              </div>
              <form class="focus-task-form" @submit.prevent="addTask">
                <input v-model="newTask" maxlength="60" placeholder="添加今日任务">
                <button type="submit" aria-label="添加任务" title="添加任务">
                  <span aria-hidden="true">＋</span>
                </button>
              </form>
            </section>

            <section class="focus-panel">
              <h3>本周专注</h3>
              <div class="focus-week">
                <div v-for="day in weeklyFocusDays" :key="day.date">
                  <i :style="{ height: day.barHeight }"></i>
                  <span>{{ day.label }}</span>
                  <small>{{ day.minutes }}m</small>
                </div>
              </div>
            </section>

            <section class="focus-panel">
              <h3>节奏设置</h3>
              <label class="focus-setting">
                <span>专注 {{ settings.focus }} 分钟</span>
                <input v-model.number="settings.focus" type="range" min="5" max="90" step="5" @change="resetTimer">
              </label>
              <label class="focus-setting">
                <span>短休息 {{ settings.short }} 分钟</span>
                <input v-model.number="settings.short" type="range" min="1" max="30" step="1" @change="resetTimer">
              </label>
              <label class="focus-setting">
                <span>长休息 {{ settings.long }} 分钟</span>
                <input v-model.number="settings.long" type="range" min="5" max="60" step="5" @change="resetTimer">
              </label>
              <label class="focus-setting">
                <span>每日目标 {{ dailyGoal }} 番茄</span>
                <input v-model.number="dailyGoal" type="range" min="1" max="16" step="1">
              </label>
              <label class="focus-switch">
                <input v-model="autoStart" type="checkbox">
                <span>自动进入下一阶段</span>
              </label>
              <label class="focus-switch">
                <input v-model="nativeCursor" type="checkbox" @change="onNativeCursorChange">
                <span>使用系统原生鼠标指针</span>
              </label>
            </section>

            <section class="focus-panel">
              <h3>正在播放</h3>
              <div class="focus-music">
                <div class="focus-music__row">
                  <span class="focus-music__state" :class="{ playing: musicStore.isPlaying }">
                    {{ musicStore.isPlaying ? '▶' : '❚❚' }}
                  </span>
                  <Transition name="focus-song-fade" mode="out-in">
                    <p :key="currentMusicTitle" class="focus-song" :title="currentMusicTitle">
                      {{ currentMusicTitle }}
                    </p>
                  </Transition>
                </div>
                <label class="focus-setting focus-setting--music">
                  <span>音量 {{ musicVolumePercent }}%</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    :value="musicStore.volume"
                    aria-label="音乐音量"
                    @input="setMusicVolume"
                  >
                </label>
              </div>
            </section>
          </div>
        </section>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import FloatingWindow from '../../components/platform/FloatingWindow.vue'
import StudyRoomChatPanel from '../../components/platform/StudyRoomChatPanel.vue'
import { useMusicStore } from '../../store'
import { playTrackAtIndex, pausePlayback } from '../../composables/useMusicPlayback'
import { getGlobalAudio } from '../../utils/musicAudio'
import { musicTracks } from '../../data/musicTracks'
import { buildTrackList, groupTracksByAlbum } from '../../utils/music'
import {
  createPomodoroSession,
  fetchPomodoroStats,
  fetchPomodoroTimeline,
  fetchStudyRoomOnline,
  getPlatformToken,
} from '../../api/platform'
import { imgUrl } from '../../data/profile'
import { prefersNativeCursor, setNativeCursor } from '../../utils/cursorPreference'
import { usePageMeta } from '../../composables/usePageMeta'

const modes = [
  { key: 'focus', label: '专注', minutes: settings => settings.focus },
  { key: 'short', label: '短休息', minutes: settings => settings.short },
  { key: 'long', label: '长休息', minutes: settings => settings.long },
]

const storageKey = 'cyinc-focus-state'
const musicStore = useMusicStore()
const currentMusicTitle = computed(() =>
  musicStore.currentSong?.title || '未选曲 · 点击顶部 ♪ 打开音乐面板'
)
const musicVolumePercent = computed(() => Math.round(musicStore.volume * 100))
const musicGroups = computed(() => groupTracksByAlbum(buildTrackList(musicTracks)))
const currentMode = ref('focus')
const isRunning = ref(false)
const remainingSeconds = ref(25 * 60)
const endsAt = ref(null)
const taskLabel = ref('')
const taskFocused = ref(false)
const completedFocusCount = ref(0)
const autoStart = ref(true)
const isFullscreen = ref(false)
const message = ref('选择一个节奏，开始你的第一轮专注。')
const stats = ref({ todayMinutes: 0, todaySessions: 0, weekMinutes: 0, weekSessions: 0 })
const settings = ref({ focus: 25, short: 5, long: 15 })
const settingsOpen = ref(false)
const nativeCursor = ref(prefersNativeCursor())

function onNativeCursorChange() {
  setNativeCursor(nativeCursor.value)
}
const rhythmWindowOpen = ref(true)
const chatWindowOpen = ref(false)
const musicWindowOpen = ref(false)
const newTask = ref('')
const dailyGoal = ref(8)
const tasks = ref([])
const historyRows = ref([])
const backgroundIndex = ref(0)
let tickTimer = null
let audioContext = null
const immersive = ref(false)
let immersiveIdleTimer = null
const onlineCount = ref(0)
const adminOnline = ref(false)
let onlinePollTimer = null

const backgrounds = [
  {
    label: '默认氛围',
    src: imgUrl('img/pomo-focus-background-2k.mp4'),
    poster: imgUrl('img/pomo-focus-poster.webp'),
  },
  {
    label: '动漫氛围',
    src: imgUrl('img/pomo-anime-background-2k.mp4'),
    poster: imgUrl('img/pomo-anime-poster.webp'),
  },
  {
    label: '书房氛围',
    src: imgUrl('img/pomo-programming-background-2k.mp4'),
    poster: imgUrl('img/pomo-programming-poster.webp'),
  },
]

const backgroundVideo = computed(() => backgrounds[backgroundIndex.value % backgrounds.length].src)
const backgroundPoster = computed(() => backgrounds[backgroundIndex.value % backgrounds.length].poster)
const backgroundLabel = computed(() => backgrounds[backgroundIndex.value % backgrounds.length].label)

const currentModeLabel = computed(() => modes.find(mode => mode.key === currentMode.value)?.label || '')
const currentCycle = computed(() =>
  Math.floor((completedFocusCount.value - (currentMode.value === 'focus' ? 0 : 1)) / 4) + 1
)
const totalSeconds = computed(() => settings.value[currentMode.value] * 60)
const progress = computed(() => 1 - remainingSeconds.value / Math.max(1, totalSeconds.value))
const ringCircumference = 2 * Math.PI * 112
const ringOffset = computed(() => ringCircumference * (1 - progress.value))
const formattedTime = computed(() => {
  const total = Math.max(0, Math.round(remainingSeconds.value))
  const minutes = Math.floor(total / 60).toString().padStart(2, '0')
  const seconds = Math.floor(total % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
})
const isLoggedIn = computed(() => !!getPlatformToken())
const goalProgressWidth = computed(() => `${Math.min(100, Math.round(stats.value.todaySessions / Math.max(1, dailyGoal.value) * 100))}%`)
const heatmapDays = computed(() => {
  const byDate = new Map()
  for (const row of historyRows.value) {
    byDate.set(row.date, (byDate.get(row.date) || 0) + Math.round(row.duration / 60))
  }
  return Array.from({ length: 84 }, (_, index) => {
    const date = new Date(Date.now() - (83 - index) * 86400000)
    const key = localDateKey(date)
    const minutes = byDate.get(key) || 0
    const level = minutes === 0 ? 0 : minutes < 25 ? 1 : minutes < 50 ? 2 : minutes < 90 ? 3 : minutes < 150 ? 4 : 5
    return { date: key, minutes, level }
  })
})
const weeklyFocusDays = computed(() => {
  const rows = heatmapDays.value.slice(-7)
  const max = Math.max(1, ...rows.map(row => row.minutes))
  return rows.map(row => ({
    ...row,
    label: new Date(`${row.date}T00:00:00`).toLocaleDateString('zh-CN', { weekday: 'narrow' }),
    barHeight: `${Math.max(4, Math.round(row.minutes / max * 100))}%`,
  }))
})

function readStoredState() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{}')
    if (saved.settings) settings.value = { ...settings.value, ...saved.settings }
    if (saved.taskLabel) taskLabel.value = saved.taskLabel
    if (typeof saved.autoStart === 'boolean') autoStart.value = saved.autoStart
    if (saved.completedFocusCount) completedFocusCount.value = saved.completedFocusCount
    if (saved.stats) stats.value = { ...stats.value, ...saved.stats }
    if (Array.isArray(saved.tasks)) tasks.value = saved.tasks
    if (saved.dailyGoal) dailyGoal.value = saved.dailyGoal
    if (typeof saved.backgroundIndex === 'number') {
      backgroundIndex.value = saved.backgroundIndex % backgrounds.length
    }
  } catch {}
}

function persistState() {
  const payload = {
    settings: settings.value,
    taskLabel: taskLabel.value,
    autoStart: autoStart.value,
    completedFocusCount: completedFocusCount.value,
    stats: stats.value,
    tasks: tasks.value,
    dailyGoal: dailyGoal.value,
    backgroundIndex: backgroundIndex.value,
  }
  localStorage.setItem(storageKey, JSON.stringify(payload))
}

function syncRemainingFromEnd() {
  if (!isRunning.value || !endsAt.value) return
  remainingSeconds.value = Math.max(0, (endsAt.value - Date.now()) / 1000)
}

function localDateKey(date = new Date()) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function startTimer() {
  if (remainingSeconds.value <= 0) remainingSeconds.value = totalSeconds.value
  endsAt.value = Date.now() + remainingSeconds.value * 1000
  isRunning.value = true
  message.value = currentMode.value === 'focus' ? '保持节奏，只处理当前这一件事。' : '离开屏幕，让眼睛和大脑休息。'
}

function pauseTimer() {
  syncRemainingFromEnd()
  isRunning.value = false
  endsAt.value = null
  message.value = '计时已暂停，随时可以继续。'
}

function toggleTimer() {
  if (isRunning.value) pauseTimer()
  else startTimer()
}

function resetTimer() {
  isRunning.value = false
  endsAt.value = null
  remainingSeconds.value = totalSeconds.value
  message.value = '计时已重置。'
}

function selectMode(mode) {
  if (currentMode.value === mode) return resetTimer()
  currentMode.value = mode
  resetTimer()
}

function nextMode(shouldCount = true) {
  if (currentMode.value === 'focus') {
    if (shouldCount) completedFocusCount.value += 1
    return (completedFocusCount.value % 4 === 0) ? 'long' : 'short'
  }
  return 'focus'
}

async function finishPhase() {
  const finishedMode = currentMode.value
  if (finishedMode === 'focus') {
    const duration = settings.value.focus * 60
    const localDay = localDateKey()
    const history = JSON.parse(localStorage.getItem('cyinc-focus-history') || '[]')
    history.push({ date: localDay, duration })
    historyRows.value.push({ date: localDay, duration })
    localStorage.setItem('cyinc-focus-history', JSON.stringify(history.slice(-500)))
    stats.value.todayMinutes += Math.round(duration / 60)
    stats.value.todaySessions += 1
    stats.value.weekMinutes += Math.round(duration / 60)
    stats.value.weekSessions += 1
    if (isLoggedIn.value) {
      try {
        await createPomodoroSession({
          duration_sec: duration,
          task_label: taskLabel.value.trim() || null,
          session_type: 'focus',
        })
      } catch {
        message.value = '计时完成，但云端记录保存失败。'
      }
    }
  }

  currentMode.value = nextMode(finishedMode === 'focus')
  remainingSeconds.value = totalSeconds.value
  endsAt.value = null
  isRunning.value = autoStart.value
  if (isRunning.value) endsAt.value = Date.now() + remainingSeconds.value * 1000
  message.value = autoStart.value
    ? `${finishedMode === 'focus' ? '专注完成' : '休息完成'}，已进入${currentModeLabel.value}。`
    : `${finishedMode === 'focus' ? '专注完成' : '休息完成'}，可以开始了。`
  persistState()
  playChime()
  notify(`${finishedMode === 'focus' ? '专注完成' : '休息完成'}：${currentModeLabel.value}开始`)
}

function skipPhase() {
  if (!window.confirm('确定跳过当前阶段吗？')) return
  currentMode.value = nextMode(false)
  resetTimer()
}

function addTask() {
  const label = newTask.value.trim()
  if (!label) return
  tasks.value.push({ id: Date.now(), label, done: false })
  newTask.value = ''
}

function removeTask(id) {
  tasks.value = tasks.value.filter(task => task.id !== id)
}

function ensureMusicPlaylist() {
  if (!musicStore.playlist.length) {
    musicStore.setPlaylist(buildTrackList(musicTracks))
  }
}

function toggleMusic() {
  if (musicStore.isPlaying) {
    pausePlayback()
    return
  }
  ensureMusicPlaylist()
  if (!musicStore.playlist.length) return
  const index = musicStore.currentIndex >= 0
    ? musicStore.currentIndex
    : Math.floor(Math.random() * musicStore.playlist.length)
  void playTrackAtIndex(index)
}

function setMusicVolume(event) {
  const volume = Number(event.target.value)
  if (!Number.isFinite(volume)) return
  musicStore.setVolume(volume)
  const audio = getGlobalAudio()
  if (audio) audio.volume = musicStore.volume
}

function playMusicTrack(index) {
  ensureMusicPlaylist()
  void playTrackAtIndex(index)
}

function playPrevTrack() {
  if (musicStore.hasPrev()) void playTrackAtIndex(musicStore.currentIndex - 1)
}

function playNextTrack() {
  if (musicStore.hasNext()) void playTrackAtIndex(musicStore.currentIndex + 1)
}

function onMusicSeekInput(event) {
  const t = Number(event.target.value)
  if (Number.isFinite(t)) musicStore.setCurrentTime(t)
}

function onMusicSeekEnd(event) {
  const t = Number(event.target.value)
  const audio = getGlobalAudio()
  if (!Number.isFinite(t) || !audio) return
  audio.currentTime = t
  musicStore.setCurrentTime(t)
  musicStore.saveState()
}

function fmtMusicTime(sec) {
  if (!sec || !Number.isFinite(sec)) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    void document.documentElement.requestFullscreen?.()
  } else {
    void document.exitFullscreen?.()
  }
}

function switchBackground(step) {
  backgroundIndex.value = (backgroundIndex.value + step + backgrounds.length) % backgrounds.length
}

// 计时运行中指针静置 ~3s 进入沉浸模式：隐藏界面只剩视频与计时环
function scheduleImmersive() {
  if (immersiveIdleTimer) window.clearTimeout(immersiveIdleTimer)
  immersiveIdleTimer = window.setTimeout(() => {
    if (isRunning.value && !settingsOpen.value) immersive.value = true
  }, 3200)
}

function wakeImmersive() {
  if (immersive.value) immersive.value = false
  scheduleImmersive()
}

function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

async function refreshOnlinePresence() {
  try {
    const response = await fetchStudyRoomOnline()
    onlineCount.value = Number(response?.data?.count) || 0
    adminOnline.value = !!response?.data?.admin_online
  } catch {}
}

function playChime() {
  try {
    audioContext = audioContext || new AudioContext()
    const now = audioContext.currentTime
    const gain = audioContext.createGain()
    gain.gain.setValueAtTime(0.001, now)
    gain.gain.exponentialRampToValueAtTime(0.12, now + 0.05)
    gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2)
    gain.connect(audioContext.destination)
    ;[523.25, 659.25, 783.99].forEach((frequency, index) => {
      const oscillator = audioContext.createOscillator()
      oscillator.type = 'sine'
      oscillator.frequency.value = frequency
      oscillator.connect(gain)
      oscillator.start(now + index * 0.12)
      oscillator.stop(now + 1.2)
    })
  } catch {}
}

function notify(text) {
  if (typeof Notification === 'undefined' || Notification.permission !== 'granted') return
  new Notification('CYINC 专注空间', { body: text })
}

function calculateLocalStats() {
  const history = JSON.parse(localStorage.getItem('cyinc-focus-history') || '[]')
  historyRows.value = history
  const today = localDateKey()
  const weekStart = localDateKey(new Date(Date.now() - 6 * 86400000))
  const todayRows = history.filter(row => row.date === today)
  const weekRows = history.filter(row => row.date >= weekStart)
  stats.value.todayMinutes = todayRows.reduce((sum, row) => sum + Math.round(row.duration / 60), 0)
  stats.value.todaySessions = todayRows.length
  stats.value.weekMinutes = weekRows.reduce((sum, row) => sum + Math.round(row.duration / 60), 0)
  stats.value.weekSessions = weekRows.length
}

async function loadStats() {
  if (!isLoggedIn.value) return calculateLocalStats()
  try {
    const json = await fetchPomodoroStats()
    stats.value = { ...stats.value, ...json.data }
    const timeline = await fetchPomodoroTimeline(90)
    historyRows.value = (timeline.data?.days || []).flatMap(day =>
      day.sessions.map(session => ({ date: day.date, duration: session.duration_sec }))
    )
  } catch {
    calculateLocalStats()
  }
}

function handleKeydown(event) {
  wakeImmersive()
  if (event.code === 'Escape') {
    settingsOpen.value = false
    chatWindowOpen.value = false
    rhythmWindowOpen.value = false
    return
  }
  if (settingsOpen.value) return
  if (taskFocused.value) return
  if (event.code !== 'Space') return
  event.preventDefault()
  toggleTimer()
}

watch(
  [settings, taskLabel, autoStart, completedFocusCount, stats, tasks, dailyGoal, backgroundIndex],
  persistState,
  { deep: true }
)
watch(settingsOpen, (open) => {
  document.body.classList.toggle('focus-modal-open', open)
  if (open) immersive.value = false
})
watch(isRunning, (running) => {
  if (running) {
    scheduleImmersive()
  } else {
    immersive.value = false
    if (immersiveIdleTimer) window.clearTimeout(immersiveIdleTimer)
  }
})

onMounted(async () => {
  readStoredState()
  remainingSeconds.value = totalSeconds.value
  document.addEventListener('fullscreenchange', onFullscreenChange)
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('pointermove', wakeImmersive, { passive: true })
  window.addEventListener('pointerdown', wakeImmersive, { passive: true })
  window.addEventListener('wheel', wakeImmersive, { passive: true })
  window.addEventListener('touchstart', wakeImmersive, { passive: true })
  tickTimer = window.setInterval(() => {
    if (!isRunning.value) return
    syncRemainingFromEnd()
    if (remainingSeconds.value <= 0) void finishPhase()
  }, 250)
  void refreshOnlinePresence()
  onlinePollTimer = window.setInterval(refreshOnlinePresence, 30000)
  await loadStats()
  if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
    void Notification.requestPermission()
  }
})

onBeforeUnmount(() => {
  document.body.classList.remove('focus-modal-open')
  window.clearInterval(tickTimer)
  if (onlinePollTimer) window.clearInterval(onlinePollTimer)
  if (immersiveIdleTimer) window.clearTimeout(immersiveIdleTimer)
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('pointermove', wakeImmersive)
  window.removeEventListener('pointerdown', wakeImmersive)
  window.removeEventListener('wheel', wakeImmersive)
  window.removeEventListener('touchstart', wakeImmersive)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
})

usePageMeta({
  title: '专注自习室',
  description: '沉浸式番茄钟专注空间，支持专注计时、休息节奏、全屏模式和背景音乐。',
})
</script>

<style scoped>
.focus-room {
  --focus-accent: #ffd166;
  --focus-accent-soft: rgba(255, 209, 102, 0.18);
  --focus-glass: rgba(18, 22, 28, 0.58);
  --focus-glass-strong: rgba(15, 18, 24, 0.82);
  --focus-border: rgba(255, 255, 255, 0.12);
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  color: #fff;
  background: #090b10;
}
.focus-room--short,
.focus-room--long {
  --focus-accent: #74c0fc;
  --focus-accent-soft: rgba(116, 192, 252, 0.16);
}
.focus-background,
.focus-overlay,
.focus-aura { position: absolute; inset: 0; }
.focus-background {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.focus-background-fade-enter-active,
.focus-background-fade-leave-active {
  transition: opacity 0.5s ease;
}
.focus-background-fade-enter-from,
.focus-background-fade-leave-to {
  opacity: 0;
}
.focus-overlay {
  background:
    radial-gradient(circle at 50% 42%, rgba(10, 12, 16, 0.05), rgba(8, 10, 14, 0.52)),
    linear-gradient(180deg, rgba(8, 10, 14, 0.22), rgba(7, 9, 13, 0.58));
  transition: opacity 0.9s ease;
}
.focus-aura {
  pointer-events: none;
  background:
    radial-gradient(circle at 50% 50%, var(--focus-accent-soft), transparent 38%),
    radial-gradient(circle at 78% 16%, rgba(116, 192, 252, 0.10), transparent 34%),
    radial-gradient(circle at 18% 82%, rgba(255, 158, 128, 0.09), transparent 32%);
  opacity: 0.92;
  transition: background 0.6s ease, opacity 0.9s ease;
}
/* 沉浸模式：计时运行 + 指针静置时，隐藏界面只剩视频与计时环 */
.focus-room--immersive,
.focus-room--immersive * { cursor: none !important; }
.focus-room--immersive .focus-topbar,
.focus-room--immersive .focus-controls,
.focus-room--immersive .focus-timer,
.focus-room--immersive .focus-rhythm-window,
.focus-room--immersive .focus-chat-window,
.focus-room--immersive .focus-music-window,
.focus-room--immersive .focus-bg-arrow {
  opacity: 0;
  pointer-events: none;
}
.focus-room--immersive .focus-overlay { opacity: 0.5; }
.focus-room--immersive .focus-aura { opacity: 0.45; }
.focus-topbar { transition: opacity 0.6s ease, transform 0.6s ease; }
.focus-controls { transition: opacity 0.6s ease; }
.focus-immersive-hint {
  position: fixed;
  left: 50%;
  bottom: 9vh;
  transform: translateX(-50%);
  z-index: 15;
  margin: 0;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  color: rgba(255, 255, 255, 0.55);
  pointer-events: none;
  animation: focusHintFade 3.6s ease forwards;
}
@keyframes focusHintFade {
  0% { opacity: 0; }
  15% { opacity: 1; }
  70% { opacity: 0.8; }
  100% { opacity: 0; }
}
.focus-immersive-capsule {
  position: fixed;
  left: 50%;
  bottom: 4vh;
  transform: translateX(-50%);
  z-index: 15;
  display: flex;
  align-items: center;
  gap: 0.6em;
  padding: 0.45em 1.1em;
  border-radius: 999px;
  background: rgba(10, 12, 18, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.14);
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.85);
  pointer-events: none;
  white-space: nowrap;
}
.focus-immersive-capsule strong {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.focus-immersive-capsule span {
  font-size: 0.72rem;
  opacity: 0.7;
}
.focus-immersive-capsule i {
  width: 56px;
  height: 2px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.15);
  overflow: hidden;
}
.focus-immersive-capsule i b {
  display: block;
  height: 100%;
  background: var(--focus-accent);
  transition: width 0.3s linear;
}
@media (max-width: 640px) {
  .focus-immersive-capsule {
    bottom: 12vh;
    font-size: 0.78rem;
  }
  .focus-immersive-capsule i { width: 40px; }
}
.focus-rhythm-window,
.focus-chat-window,
.focus-music-window { transition: opacity 0.6s ease; }
.focus-bg-arrow {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 14;
  width: 46px;
  height: 72px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 14px;
  background: rgba(10, 12, 18, 0.45);
  color: rgba(255, 255, 255, 0.55);
  font-size: 1.7rem;
  line-height: 1;
  cursor: pointer;
  transition: opacity 0.6s ease, background 0.25s ease, color 0.25s ease, border-color 0.25s ease;
}
.focus-bg-arrow:hover {
  background: rgba(10, 12, 18, 0.55);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}
.focus-bg-arrow--prev { left: 20px; }
.focus-bg-arrow--next { right: 20px; }
@media (max-width: 640px) {
  .focus-bg-arrow { width: 38px; height: 56px; font-size: 1.3rem; }
  .focus-bg-arrow--prev { left: 10px; }
  .focus-bg-arrow--next { right: 10px; }
}
.focus-topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem clamp(1rem, 3vw, 2rem);
  background: linear-gradient(180deg, rgba(8, 10, 14, 0.72), transparent);
}
.focus-brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  min-width: 0;
}
.focus-brand__mark {
  width: 2.7rem;
  height: 2.7rem;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.09);
  backdrop-filter: blur(12px);
  font-family: var(--mono);
  color: var(--focus-accent);
}
.focus-brand p {
  margin: 0 0 0.15rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.24em;
  color: rgba(255, 255, 255, 0.62);
}
.focus-brand strong {
  display: block;
  font-size: 0.92rem;
  font-weight: 500;
  white-space: nowrap;
}
.focus-top-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.focus-top-button,
.focus-modal__head button,
.focus-task-form button {
  border: 1px solid var(--focus-border);
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}
.focus-top-button {
  width: 2.7rem;
  height: 2.7rem;
  display: grid;
  place-items: center;
  padding: 0;
  border-radius: 50%;
  font-size: 0.95rem;
  text-decoration: none;
  backdrop-filter: blur(12px);
}
.focus-top-button.active {
  border-color: var(--focus-accent);
  color: var(--focus-accent);
}
.focus-top-button:hover,
.focus-modal__head button:hover,
.focus-task-form button:hover {
  border-color: rgba(255, 255, 255, 0.32);
  background: rgba(255, 255, 255, 0.14);
  transform: translateY(-1px);
}
.focus-presence {
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  height: 2.7rem;
  padding: 0 0.85rem;
  border: 1px solid var(--focus-border);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.82);
  font-family: inherit;
  font-size: 0.74rem;
  white-space: nowrap;
  cursor: pointer;
  backdrop-filter: blur(12px);
  transition: border-color 0.2s ease, background 0.2s ease;
}
.focus-presence:hover {
  border-color: rgba(255, 255, 255, 0.32);
  background: rgba(255, 255, 255, 0.14);
}
.focus-presence__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  transition: background 0.3s ease, box-shadow 0.3s ease;
}
.focus-presence__dot.live {
  background: #5ad07a;
  box-shadow: 0 0 8px rgba(90, 208, 122, 0.7);
}
.focus-presence__admin { color: rgba(255, 255, 255, 0.55); }
@media (max-width: 520px) {
  .focus-presence__admin,
  .focus-presence .focus-presence__dot:last-of-type { display: none; }
}
.focus-shell {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  align-items: center;
  gap: clamp(1.5rem, 4vw, 3.5rem);
  width: min(1120px, 100%);
  margin: 0 auto;
  padding: clamp(6rem, 12vh, 7rem) clamp(1rem, 3vw, 2rem) clamp(1.8rem, 4vh, 2.8rem);
}
.focus-primary {
  display: grid;
  justify-items: center;
  gap: clamp(1.1rem, 3vh, 1.7rem);
}
.focus-rhythm-window {
  top: clamp(7rem, 16vh, 9.5rem);
  right: clamp(1rem, 5vw, 4rem);
  width: min(360px, calc(100vw - 2rem));
}
.focus-rhythm-window :deep(.floating-window__header) {
  padding: 0.85rem 1rem;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.07), transparent);
}
.focus-rhythm-window :deep(.floating-window__body) {
  padding: 0.9rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), transparent 45%),
    rgba(9, 11, 16, 0.22);
}
.focus-rhythm {
  display: grid;
  gap: 0.85rem;
}
.focus-rhythm__summary {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.045);
  font-size: 0.72rem;
}
.focus-rhythm__summary span {
  color: rgba(255, 255, 255, 0.52);
}
.focus-rhythm__summary strong {
  color: var(--focus-accent);
  font-size: 0.86rem;
}
.focus-rhythm__summary small {
  color: rgba(255, 255, 255, 0.56);
  font-family: var(--mono);
}
.focus-chat-window {
  right: 1.1rem;
  bottom: 1.1rem;
  width: min(390px, calc(100vw - 2rem));
  max-width: calc(100vw - 2rem);
  max-height: min(70vh, 560px);
}
.focus-chat-window :deep(.study-chat-panel__list) {
  height: 100%;
  min-height: 0;
}
.focus-music-window {
  left: 1.1rem;
  bottom: 1.1rem;
  width: min(340px, calc(100vw - 2rem));
  max-width: calc(100vw - 2rem);
  max-height: min(72vh, 540px);
}
.focus-music-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
}
.focus-music-panel__now {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.8rem 0.9rem 0.6rem;
}
.focus-music-panel__state {
  width: 1.55rem;
  height: 1.55rem;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.05);
  font-size: 0.58rem;
}
.focus-music-panel__state.playing {
  border-color: rgba(255, 209, 102, 0.42);
  color: var(--focus-accent);
  background: rgba(255, 209, 102, 0.12);
}
.focus-music-panel__now p {
  margin: 0;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.78rem;
  color: #fff;
}
.focus-music-panel__seek {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.45rem;
  padding: 0 0.9rem 0.6rem;
}
.focus-music-panel__seek span {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: rgba(255, 255, 255, 0.58);
  min-width: 2rem;
  font-variant-numeric: tabular-nums;
}
.focus-music-panel input[type='range'] {
  width: 100%;
  height: 4px;
  appearance: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  outline: none;
  cursor: pointer;
}
.focus-music-panel input[type='range']::-webkit-slider-thumb {
  appearance: none;
  width: 13px;
  height: 13px;
  border: 2px solid #0b0e13;
  border-radius: 50%;
  background: var(--focus-accent);
  cursor: pointer;
}
.focus-music-panel__controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0 0.9rem 0.6rem;
}
.focus-music-panel__controls button {
  width: 2.15rem;
  height: 2.15rem;
  display: grid;
  place-items: center;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.78rem;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}
.focus-music-panel__controls button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.16);
  border-color: rgba(255, 255, 255, 0.3);
}
.focus-music-panel__controls button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.focus-music-panel__controls .focus-music-panel__play {
  width: 2.6rem;
  height: 2.6rem;
  background: var(--focus-accent);
  border-color: var(--focus-accent);
  color: #171207;
  font-size: 0.9rem;
}
.focus-music-panel__vol {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.9rem 0.75rem;
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.62);
}
.focus-music-panel__list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0.4rem 0.55rem 0.7rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.focus-music-panel__album {
  margin: 0.55rem 0.35rem 0.3rem;
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.14em;
  color: rgba(255, 255, 255, 0.45);
  text-transform: uppercase;
}
.focus-music-panel__track {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  width: 100%;
  padding: 0.42rem 0.55rem;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.76rem;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}
.focus-music-panel__track span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.focus-music-panel__track:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
.focus-music-panel__track.active {
  color: var(--focus-accent);
  background: rgba(255, 209, 102, 0.1);
}
.focus-music-panel__track i {
  font-style: normal;
  font-size: 0.6rem;
  flex: 0 0 auto;
}
.focus-modes {
  display: flex;
  gap: 0.4rem;
  padding: 0.25rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  background: rgba(8, 10, 14, 0.36);
}
.focus-modes button {
  display: grid;
  gap: 0.05rem;
  min-width: 0;
  padding: 0.52rem 0.35rem;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: rgba(255, 255, 255, 0.66);
  cursor: pointer;
  font-size: 0.82rem;
  transition: background 0.2s ease, color 0.2s ease;
}
.focus-modes button small {
  font-family: var(--mono);
  font-size: 0.62rem;
  opacity: 0.68;
}
.focus-modes button.active {
  color: #171207;
  background: var(--focus-accent);
  box-shadow: 0 8px 24px var(--focus-accent-soft);
}
.focus-modes button.active small { opacity: 0.76; }
.focus-timer {
  position: relative;
  width: min(370px, 38vw);
  aspect-ratio: 1;
  transition: opacity 0.6s ease;
}
.focus-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.focus-ring__aura { fill: rgba(255, 255, 255, 0.015); }
.focus-ring__ticks line {
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 1;
  stroke-linecap: round;
}
.focus-ring__ticks line:nth-child(5n) { stroke: rgba(255, 255, 255, 0.16); }
.focus-ring__track,
.focus-ring__progress {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
}
.focus-ring__track { stroke: rgba(255, 255, 255, 0.08); }
.focus-ring__progress {
  stroke: var(--focus-accent);
  filter: drop-shadow(0 0 6px var(--focus-accent-soft));
  transition: stroke-dashoffset 0.3s linear;
}.focus-time {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  align-content: center;
  text-align: center;
}
.focus-time small {
  margin-bottom: 0.5rem;
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 0.26em;
  color: rgba(255, 255, 255, 0.58);
}
.focus-time strong {
  font-family: var(--mono);
  font-size: clamp(3.4rem, 12vw, 5rem);
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.02em;
  text-shadow: 0 16px 44px rgba(0, 0, 0, 0.34);
}
.focus-time span {
  margin-top: 0.65rem;
  color: var(--focus-accent);
  font-size: 0.78rem;
}
.focus-task {
  width: 100%;
  display: grid;
  gap: 0.65rem;
}
.focus-task input {
  height: 2.6rem;
  padding: 0 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
  outline: none;
  transition: border-color 0.2s ease, background 0.2s ease;
}
.focus-task input::placeholder { color: rgba(255, 255, 255, 0.42); }
.focus-task input:focus {
  border-color: var(--focus-accent);
  background: rgba(255, 255, 255, 0.10);
}
.focus-task p {
  margin: 0;
  color: rgba(255, 255, 255, 0.64);
  font-size: 0.76rem;
  line-height: 1.5;
}
.focus-controls { display: grid; place-items: center; }
.focus-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  min-width: 9.4rem;
  height: 3.5rem;
  padding: 0 1.4rem;
  border: 1px solid rgba(255, 209, 102, 0.68);
  border-radius: 999px;
  background: var(--focus-accent);
  color: #171207;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  box-shadow: 0 18px 48px rgba(255, 209, 102, 0.20);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}
.focus-room--short .focus-toggle,
.focus-room--long .focus-toggle {
  border-color: rgba(116, 192, 252, 0.68);
  box-shadow: 0 18px 48px rgba(116, 192, 252, 0.16);
}
.focus-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 22px 58px var(--focus-accent-soft);
}
.focus-panel {
  padding: 1.15rem;
  border: 1px solid var(--focus-border);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.055);
  backdrop-filter: blur(18px);
}
.focus-panel--wide { grid-column: span 2; }
.focus-panel h3 {
  margin: 0 0 0.95rem;
  font-size: 0.92rem;
  font-weight: 500;
}
.focus-panel h3::after {
  content: '';
  display: block;
  width: 1.6rem;
  height: 2px;
  margin-top: 0.55rem;
  border-radius: 999px;
  background: var(--focus-accent);
}
.focus-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}
.focus-stats div {
  display: grid;
  gap: 0.25rem;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
}
.focus-stats strong {
  font-family: var(--mono);
  font-size: 1.2rem;
}
.focus-stats span,
.focus-hint,
.focus-song {
  color: rgba(255, 255, 255, 0.62);
  font-size: 0.74rem;
}
.focus-hint,
.focus-song {
  margin: 0.85rem 0 0;
  line-height: 1.5;
}
.focus-music {
  display: grid;
  gap: 0.75rem;
}
.focus-music__row {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-width: 0;
}
.focus-music__row .focus-song {
  flex: 1;
  min-width: 0;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.focus-music__state {
  width: 1.55rem;
  height: 1.55rem;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.05);
  font-size: 0.58rem;
}
.focus-music__state.playing {
  border-color: rgba(255, 209, 102, 0.42);
  color: var(--focus-accent);
  background: rgba(255, 209, 102, 0.12);
}
.focus-setting--music {
  margin-bottom: 0;
}
.focus-song-fade-enter-active,
.focus-song-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.focus-song-fade-enter-from,
.focus-song-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
.focus-setting,
.focus-switch {
  display: grid;
  gap: 0.55rem;
  margin-bottom: 0.95rem;
  color: rgba(255, 255, 255, 0.74);
  font-size: 0.78rem;
}
.focus-setting input[type='range'] {
  width: 100%;
  height: 4px;
  appearance: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  outline: none;
}
.focus-setting input[type='range']::-webkit-slider-thumb {
  width: 15px;
  height: 15px;
  border: 2px solid #0b0e13;
  border-radius: 50%;
  background: var(--focus-accent);
  appearance: none;
  cursor: pointer;
}
.focus-switch {
  grid-template-columns: auto 1fr;
  align-items: center;
  margin-bottom: 0;
}
.focus-switch input {
  width: 1rem;
  height: 1rem;
  accent-color: var(--focus-accent);
}
.focus-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  padding: clamp(0.7rem, 2vw, 1.2rem);
  background: rgba(7, 9, 12, 0.70);
  backdrop-filter: blur(8px);
}
.focus-modal {
  width: min(1060px, 96vw);
  max-height: min(90vh, 900px);
  display: grid;
  grid-template-rows: auto 1fr;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 20px;
  background: var(--focus-glass-strong);
  box-shadow: 0 28px 90px rgba(0, 0, 0, 0.46);
}
.focus-modal__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.10);
}
.focus-modal__head p {
  margin: 0 0 0.2rem;
  font-family: var(--mono);
  font-size: 0.64rem;
  letter-spacing: 0.22em;
  color: rgba(255, 255, 255, 0.55);
}
.focus-modal__head h2 {
  margin: 0;
  font-size: 1.2rem;
}
.focus-modal__head button {
  width: 2.4rem;
  height: 2.4rem;
  display: grid;
  place-items: center;
  padding: 0;
  border-radius: 50%;
}
.focus-modal__actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.focus-modal__actions button {
  height: 2.4rem;
  width: auto;
  min-width: 2.4rem;
  padding: 0 0.85rem;
  border-radius: 999px;
  font-size: 0.78rem;
  white-space: nowrap;
}
.focus-modal__actions button:last-child {
  width: 2.4rem;
  padding: 0;
  border-radius: 50%;
}
.focus-modal__body {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  padding: 1.1rem;
  overflow: auto;
}
.focus-heatmap {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 4px;
}
.focus-heatmap__cell {
  aspect-ratio: 1;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.08);
}
.focus-heatmap__cell.level-1 { background: rgba(255, 209, 102, 0.24); }
.focus-heatmap__cell.level-2 { background: rgba(255, 209, 102, 0.44); }
.focus-heatmap__cell.level-3 { background: rgba(255, 209, 102, 0.64); }
.focus-heatmap__cell.level-4 { background: rgba(255, 209, 102, 0.82); }
.focus-heatmap__cell.level-5 { background: #ffd166; }
.focus-goal {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: rgba(255, 255, 255, 0.74);
  font-size: 0.79rem;
}
.focus-goal strong {
  font-family: var(--mono);
  color: var(--focus-accent);
}
.focus-progress {
  height: 7px;
  margin: 0.55rem 0 0.95rem;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.10);
}
.focus-progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--focus-accent);
  transition: width 0.3s ease;
}
.focus-task-list {
  display: grid;
  gap: 0.45rem 0.6rem;
  max-height: 190px;
  overflow: auto;
}
.focus-task-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  font-size: 0.78rem;
}
.focus-task-item input {
  width: 0.95rem;
  height: 0.95rem;
  accent-color: var(--focus-accent);
}
.focus-task-item span.done {
  color: rgba(255, 255, 255, 0.42);
  text-decoration: line-through;
}
.focus-task-item button,
.focus-task-form button {
  border: 0;
  color: rgba(255, 255, 255, 0.55);
}
.focus-task-item button {
  background: transparent;
  cursor: pointer;
  font-size: 0.7rem;
}
.focus-task-item button:hover { color: #fff; }
.focus-task-form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.focus-task-form input {
  height: 2.35rem;
  min-width: 0;
  padding: 0 0.7rem;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
  outline: none;
  transition: border-color 0.2s ease;
}
.focus-task-form input:focus { border-color: var(--focus-accent); }
.focus-task-form button {
  width: 2.35rem;
  height: 2.35rem;
  display: grid;
  place-items: center;
  padding: 0;
  border-radius: 10px;
  color: #fff;
}
.focus-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.45rem;
  height: 150px;
  align-items: end;
  padding-bottom: 2.2rem;
}
.focus-week div {
  position: relative;
  height: calc(100% - 2.2rem);
  display: grid;
  align-items: end;
}
.focus-week i {
  display: block;
  min-height: 4px;
  border-radius: 5px 5px 0 0;
  background: linear-gradient(180deg, var(--focus-accent), rgba(255, 209, 102, 0.28));
}
.focus-week span,
.focus-week small {
  position: absolute;
  top: calc(100% + 0.35rem);
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.63rem;
}
.focus-week small { top: calc(100% + 1rem); }
@media (max-width: 980px) {
  .focus-shell {
    grid-template-columns: 1fr;
    gap: 1.4rem;
    align-content: center;
  }
  .focus-primary {
    width: 100%;
  }
  .focus-timer {
    width: min(350px, 72vw);
  }
  .focus-rhythm-window {
    top: auto;
    right: 0.75rem;
    bottom: 0.75rem;
    width: min(360px, calc(100vw - 1.5rem));
    max-height: min(58vh, 430px);
  }
}
@media (max-width: 760px) {
  .focus-topbar {
    align-items: flex-start;
    flex-direction: column;
  }
  .focus-top-actions {
    width: 100%;
    justify-content: flex-end;
  }
  .focus-shell {
    grid-template-columns: 1fr;
    align-content: start;
    justify-items: center;
    min-height: 100vh;
    padding-top: 8.4rem;
    overflow-y: auto;
  }
  .focus-primary {
    width: 100%;
  }
  .focus-timer {
    width: min(340px, 82vw);
  }
  .focus-rhythm-window,
  .focus-chat-window,
  .focus-music-window {
    right: 0.65rem;
    left: 0.65rem;
    width: auto;
  }
  .focus-modes {
    width: 100%;
  }
  .focus-task {
    width: 100%;
  }
  .focus-modal__body { grid-template-columns: 1fr; }
  .focus-panel--wide { grid-column: auto; }
  .focus-week { height: 130px; }
}
</style>

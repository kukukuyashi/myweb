<template>
  <div ref="pomoRef" class="pomo-page" :class="{ fullscreen: isFullscreen, 'pomo-page--minimal': minimalMode }">
    <PlatformPageShell
      :coord="minimalMode ? 'POMODORO · FOCUS' : 'POMODORO · 勉強部 · ACG'"
      title="番茄钟"
      :lead="minimalMode ? '能量格计时 · 全屏专注 · 反思写入时间线。' : '和碧蓝档案的伙伴们一起专注 — 弹匣计时、沉浸自习室、反思写入时间线。'"
      :ink-image="minimalMode ? '' : PLATFORM_POMO_INK_IMAGE"
      :ink-position="PLATFORM_POMO_INK_POSITION"
      :ink-r-end="120"
    >
      <template #actions>
        <button type="button" class="platform-btn-ghost" @click="toggleMinimalMode">
          {{ minimalMode ? 'ACG 模式' : '简约模式' }}
        </button>
        <button v-if="!minimalMode" type="button" class="platform-btn-primary pomo-enter-study" @click="openStudyRoom">
          进入自习室
        </button>
      </template>
      <div v-if="!isFullscreen" class="platform-stat-strip ink-panel pomo-strip reveal-item" data-reveal>
        <span v-if="!minimalMode">伴侶 · <strong>{{ activeCompanion.name }}</strong></span>
        <span>MODE · <strong>{{ mode === 'focus' ? '专注' : '休息' }}</strong></span>
        <span>ROUND · <strong>{{ focusCount }}</strong></span>
        <span>PROGRESS · <strong>{{ progressPct }}%</strong></span>
        <span v-if="token && stats">TODAY · <strong>{{ stats.today_minutes }}m</strong></span>
      </div>

      <section
        ref="focusArea"
        class="platform-panel ink-panel pomo-core pomo-cockpit reveal-item"
        data-reveal
        :class="{
          'fs-mode': isFullscreen,
          'pomo-core--minimal': minimalMode,
          'pomo-core--focus': mode === 'focus',
          'pomo-core--break': mode === 'break',
          'pomo-core--running': running,
        }"
        :style="minimalMode ? undefined : coreAccentStyle"
      >
        <template v-if="!minimalMode">
          <div class="pomo-deco-bg" :style="{ backgroundImage: `url('${thumbUrl(activeCompanion.img)}')` }" aria-hidden="true" />
          <div class="pomo-petals" aria-hidden="true" />
        </template>
        <div class="cockpit-grid" aria-hidden="true" />

        <div class="pomo-stage" :class="{ 'pomo-stage--solo': minimalMode }">
          <aside v-if="!minimalMode && !isFullscreen" class="pomo-companion">
            <div class="acg-frame acg-frame--profile pomo-portrait">
              <img
                :src="thumbUrl(activeCompanion.img)"
                :alt="activeCompanion.name"
                loading="lazy"
                @error="onThumbError($event, activeCompanion.img)"
              />
              <span class="frame-label">{{ activeCompanion.series }}</span>
            </div>
            <div class="pomo-bubble">
              <p class="pomo-bubble__tag">VOICE · {{ activeCompanion.name }}</p>
              <p class="pomo-bubble__line">{{ companionLine }}</p>
            </div>
            <div class="acg-chips pomo-chips">
              <span v-for="t in pomoAcgTags" :key="t" class="acg-chip">{{ t }}</span>
            </div>
            <div v-if="!isFullscreen" class="pomo-picker">
              <p class="pomo-picker__label">切换陪伴</p>
              <div class="pomo-picker__row">
                <button
                  v-for="c in pomoCompanions"
                  :key="c.id"
                  type="button"
                  class="pomo-picker__btn"
                  :class="{ active: c.id === activeCompanion.id }"
                  :title="c.name"
                  @click="selectCompanion(c.id)"
                >
                  <img
                    :src="thumbUrl(c.img)"
                    :alt="c.name"
                    @error="onThumbError($event, c.img)"
                  />
                </button>
              </div>
            </div>
          </aside>

          <div class="pomo-main" :class="{ 'pomo-main--centered': minimalMode }">
        <div class="top-row">
          <div class="mode-block">
            <p class="mode-tag">{{ mode === 'focus' ? (minimalMode ? 'FOCUS · 专注' : 'FOCUS · 专注段') : (minimalMode ? 'REST · 休息' : 'REST · 休息段') }}</p>
            <p class="mode-label">{{ minimalMode ? modeLabel : `${modeLabel} · ${activeCompanion.name} 监工中` }}</p>
          </div>
          <div class="top-actions">
            <button type="button" class="icon-btn" title="设置" @click="toggleSettings">⚙</button>
            <button type="button" class="icon-btn" title="全屏专注" @click="toggleFullscreen">⛶</button>
          </div>
        </div>

        <p v-if="focusQuote" class="focus-quote">{{ focusQuote }}</p>

        <div class="cycle-dots" :aria-label="`第 ${focusCount + 1} 轮专注周期`">
          <span
            v-for="(dot, i) in cycleDots"
            :key="i"
            class="cycle-dot"
            :class="{ 'cycle-dot--done': dot.done, 'cycle-dot--current': dot.current }"
          />
        </div>

        <PomoEnergyGrid
          v-if="minimalMode"
          :display-time="displayTime"
          :remaining-ratio="remainingRatio"
          :total-minutes="currentTotalMinutes"
          :elapsed-seconds="elapsedSeconds"
          :running="running"
          :mode="mode"
          :accent="timerAccent"
          :sub-text="mode === 'focus' ? '保持专注' : '放松一下'"
        />
        <PomoMagazine
          v-else
          :display-time="displayTime"
          :remaining-ratio="remainingRatio"
          :total-minutes="currentTotalMinutes"
          :elapsed-seconds="elapsedSeconds"
          :running="running"
          :mode="mode"
          :accent="timerAccent"
          :sub-text="mode === 'focus' ? '邪魔禁止 · STAY ON TASK' : 'お疲れ · BREATHE'"
        />

        <label v-if="mode === 'focus'" class="task-label">
          任务（可选）
          <input v-model="taskLabel" placeholder="例如：写论坛 MVP" maxlength="200" :disabled="running" />
        </label>

        <div class="timer-actions">
          <button type="button" class="platform-btn-primary" @click="toggleTimer">
            {{ running ? '暂停' : secondsLeft === totalSeconds ? '开始' : '继续' }}
          </button>
          <button type="button" class="platform-btn-ghost" @click="resetTimer">重置</button>
          <button type="button" class="platform-btn-ghost" @click="switchMode">
            切换{{ mode === 'focus' ? '休息' : '专注' }}
          </button>
        </div>

        <p v-if="!token" class="warn">
          未登录：专注完成后无法保存。
          <router-link to="/app/me">去登录</router-link>
        </p>
        <p v-if="message" class="success">{{ message }}</p>
        <p v-if="error" class="error">{{ error }}</p>
          </div>
        </div>

        <figure v-if="!minimalMode && isFullscreen" class="pomo-fs-companion">
          <img
            :src="thumbUrl(activeCompanion.img)"
            :alt="activeCompanion.name"
            @error="onThumbError($event, activeCompanion.img)"
          />
          <figcaption>{{ companionLine }}</figcaption>
        </figure>
      </section>

      <section v-if="showSettings && !isFullscreen" ref="settingsRef" class="platform-panel ink-panel settings reveal-item" data-reveal>
        <header class="panel-head">
          <h2>计时设置</h2>
          <p class="panel-sub">{{ minimalMode ? 'TIMER CONFIG' : 'タイマー設定 · CONFIG' }}</p>
        </header>
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
        <button type="button" class="platform-btn-ghost" @click="saveSettings">保存设置</button>
      </section>

      <section v-if="token && stats && !isFullscreen" class="platform-panel ink-panel pomo-stats reveal-item" data-reveal>
        <header class="panel-head">
          <h2>统计</h2>
          <p class="panel-sub">{{ minimalMode ? 'SESSION METRICS' : 'SESSION · 戦績' }}</p>
        </header>
        <div class="stats-grid">
          <div class="stat-cell"><span class="stat-num">{{ stats.today_minutes }}</span><span class="stat-label">今日分钟</span></div>
          <div class="stat-cell"><span class="stat-num">{{ stats.today_sessions }}</span><span class="stat-label">今日次数</span></div>
          <div class="stat-cell"><span class="stat-num">{{ stats.week_minutes }}</span><span class="stat-label">本周分钟</span></div>
          <div class="stat-cell"><span class="stat-num">{{ stats.week_sessions }}</span><span class="stat-label">本周次数</span></div>
        </div>
      </section>

      <section v-if="token && !isFullscreen" class="platform-panel ink-panel week-chart reveal-item" data-reveal>
        <header class="panel-head">
          <h2>本周专注</h2>
          <p class="panel-sub">{{ minimalMode ? 'WEEKLY CHART' : 'WEEKLY · ヒートマップ' }}</p>
        </header>
        <div class="chart-wrap">
          <div class="chart-grid" aria-hidden="true" />
          <div class="chart-bars">
            <div v-for="bar in weekBars" :key="bar.label" class="bar-col">
              <span class="bar-value">{{ bar.minutes }}m</span>
              <div class="bar" :style="{ height: bar.height + '%' }" :title="`${bar.minutes} 分钟`" />
              <span class="bar-label">{{ bar.label }}</span>
            </div>
          </div>
        </div>
      </section>

      <div
        v-if="showReflection"
        class="modal-overlay"
        :style="{ zIndex: studyRoomOpen ? 3100 : 2000 }"
        @click.self="skipReflection"
      >
        <div class="modal platform-panel ink-panel pomo-reflect-modal" :class="{ 'pomo-reflect-modal--minimal': minimalMode }">
          <div v-if="!minimalMode" class="reflect-hero">
            <div class="acg-frame acg-frame--profile reflect-portrait">
              <img
                :src="thumbUrl(activeCompanion.img)"
                :alt="activeCompanion.name"
                @error="onThumbError($event, activeCompanion.img)"
              />
              <span class="frame-label">MISSION CLEAR</span>
            </div>
            <div>
              <p class="modal-tag">REFLECTION · {{ activeCompanion.name }}</p>
              <h2>{{ reflectionTitle }}</h2>
              <p class="modal-desc">{{ activeCompanion.completeLines[focusCount % activeCompanion.completeLines.length] }}</p>
            </div>
          </div>
          <template v-else>
            <p class="modal-tag">REFLECTION</p>
            <h2>本段专注结束了</h2>
            <p class="modal-desc">简单记录一下这段专注的收获。</p>
          </template>
          <p class="reflect-prompt">这段专注里，你学了 / 做了什么？</p>
          <textarea v-model="reflectionText" rows="4" maxlength="5000" :placeholder="minimalMode ? '例如：完成了 API 联调…' : '例如：写完了论坛 API，还看了半集芙莉莲…'" />
          <div class="modal-actions">
            <button type="button" class="platform-btn-ghost" @click="skipReflection">跳过</button>
            <button type="button" class="platform-btn-primary" :disabled="savingReflection" @click="submitReflection">
              保存并继续
            </button>
          </div>
        </div>
      </div>
    </PlatformPageShell>

    <Teleport to="body">
      <PomoStudyRoom
        v-if="studyRoomOpen && !minimalMode"
        ref="studyRoomRef"
        :companion="activeCompanion"
        :companion-img="thumbUrl(activeCompanion.img)"
        :companion-line="companionLine"
        :display-time="displayTime"
        :mode="mode"
        :mode-label="modeLabel"
        :focus-count="focusCount"
        :running="running"
        :seconds-left="secondsLeft"
        :total-seconds="totalSeconds"
        :task-label="taskLabel"
        :ambient-label="ambientLabel"
        :ambient-playing="ambientPlaying"
        v-model:memo="studyMemo"
        @close="closeStudyRoom"
        @switch-scene="cycleStudyScene"
        @toggle-fullscreen="toggleStudyFullscreen"
        @toggle-timer="toggleTimer"
        @reset="resetTimer"
        @switch-mode="switchMode"
        @toggle-ambient="toggleStudyAmbient"
      />
    </Teleport>
  </div>
</template>
<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import PlatformPageShell from '../components/platform/PlatformPageShell.vue'
import PomoEnergyGrid from '../components/platform/PomoEnergyGrid.vue'
import PomoMagazine from '../components/platform/PomoMagazine.vue'
import PomoStudyRoom from '../components/platform/PomoStudyRoom.vue'
import { usePageMeta } from '../composables/usePageMeta'
import { useRevealOnScroll } from '../composables/useRevealOnScroll'
import { initMusicEngine, pausePlayback, playTrackAtIndex } from '../composables/useMusicPlayback.js'
import { musicTracks } from '../data/musicTracks.js'
import { buildTrackList } from '../utils/music.js'
import { useMusicStore } from '../store'
import { PLATFORM_POMO_INK_IMAGE, PLATFORM_POMO_INK_POSITION } from '../data/inkTheme.js'
import { thumbUrl, onThumbError } from '../utils/thumbs.js'
import {
  getDefaultCompanionId,
  normalizeCompanionId,
  pomoAcgTags,
  pomoBreakQuotes,
  pomoCompanions,
  pomoFocusQuotes,
  pomoMinimalBreakQuotes,
  pomoMinimalFocusQuotes,
  POMO_COMPANION_KEY,
  POMO_MINIMAL_KEY,
} from '../data/pomoAcg.js'
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

const pomoRef = ref(null)
const route = useRoute()
useRevealOnScroll(pomoRef)

const FOCUS_QUOTES = pomoFocusQuotes
const BREAK_QUOTES = pomoBreakQuotes
const MINIMAL_FOCUS_QUOTES = pomoMinimalFocusQuotes
const MINIMAL_BREAK_QUOTES = pomoMinimalBreakQuotes

const minimalMode = ref(loadMinimalMode())

const companionId = ref(loadCompanionId())
const lineTick = ref(0)
let lineTickId = null

function loadCompanionId() {
  try {
    const saved = localStorage.getItem(POMO_COMPANION_KEY)
    if (saved) return normalizeCompanionId(saved)
  } catch {
    /* ignore */
  }
  return getDefaultCompanionId()
}

function loadMinimalMode() {
  try {
    return localStorage.getItem(POMO_MINIMAL_KEY) === '1'
  } catch {
    return false
  }
}

function toggleMinimalMode() {
  minimalMode.value = !minimalMode.value
  try {
    if (minimalMode.value) localStorage.setItem(POMO_MINIMAL_KEY, '1')
    else localStorage.removeItem(POMO_MINIMAL_KEY)
  } catch {
    /* ignore */
  }
  if (minimalMode.value && studyRoomOpen.value) closeStudyRoom()
}

function selectCompanion(id) {
  companionId.value = id
  try {
    localStorage.setItem(POMO_COMPANION_KEY, id)
  } catch {
    /* ignore */
  }
}

const activeCompanion = computed(() => (
  pomoCompanions.find((c) => c.id === companionId.value) || pomoCompanions[0]
))

const coreAccentStyle = computed(() => ({
  '--pomo-accent': activeCompanion.value.accent,
}))

const companionLine = computed(() => {
  const c = activeCompanion.value
  const pool = running.value
    ? (mode.value === 'focus' ? c.runningLines : c.breakLines)
    : (mode.value === 'focus' ? c.idleLines : c.breakLines)
  return pool[(focusCount.value + lineTick.value) % pool.length]
})

const reflectionTitle = computed(() => {
  if (minimalMode.value) return '本段专注结束了'
  const labels = ['本段专注结束了', 'MISSION CLEAR · 任务完成', 'お疲れさま · 一段落']
  return labels[focusCount.value % labels.length]
})

const cycleDots = computed(() => {
  const total = settings.value.cyclesBeforeLongBreak
  const round = focusCount.value % total
  return Array.from({ length: total }, (_, i) => ({
    done: focusCount.value > 0 && i < round,
    current: mode.value === 'focus' && i === round,
  }))
})

const focusQuote = computed(() => {
  const pool = minimalMode.value
    ? (mode.value === 'focus' ? MINIMAL_FOCUS_QUOTES : MINIMAL_BREAK_QUOTES)
    : (mode.value === 'focus' ? FOCUS_QUOTES : BREAK_QUOTES)
  return pool[focusCount.value % pool.length]
})

const progressPct = computed(() => {
  if (!totalSeconds.value) return 0
  return Math.round((1 - secondsLeft.value / totalSeconds.value) * 100)
})

const remainingRatio = computed(() => {
  if (!totalSeconds.value) return 1
  return secondsLeft.value / totalSeconds.value
})

const currentTotalMinutes = computed(() => Math.max(1, Math.round(totalSeconds.value / 60)))

const elapsedSeconds = computed(() => Math.max(0, totalSeconds.value - secondsLeft.value))

const timerAccent = computed(() => {
  if (minimalMode.value) return mode.value === 'break' ? '#5a8fd4' : '#e85d04'
  return activeCompanion.value.accent || '#e85d04'
})

const SETTINGS_KEY = 'cyinc_pomo_settings'
const STUDY_MEMO_KEY = 'cyinc_pomo_study_memo'

const musicStore = useMusicStore()
const studyRoomOpen = ref(false)
const studyRoomRef = ref(null)
const studyMemo = ref(loadStudyMemo())

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
const settingsRef = ref(null)
const isFullscreen = ref(false)
const focusArea = ref(null)
const showReflection = ref(false)
const reflectionText = ref('')
const savingReflection = ref(false)
const pendingSession = ref(null)
let tickId = null
let deadline = 0

const settings = ref(loadSettings())

function loadStudyMemo() {
  try {
    return localStorage.getItem(STUDY_MEMO_KEY) || ''
  } catch {
    return ''
  }
}

const ambientPlaying = computed(() => studyRoomOpen.value && musicStore.isPlaying)

const ambientLabel = computed(() => {
  const fallback = activeCompanion.value.ambientTrack || '氛围音'
  if (!musicStore.currentSong) return `氛围音 · ${fallback}`
  return musicStore.isPlaying
    ? musicStore.currentSong.title
    : `氛围音 · ${musicStore.currentSong.title}`
})

function findAmbientIndex(name) {
  initMusicEngine()
  if (!musicStore.playlist.length) {
    musicStore.setPlaylist(buildTrackList(musicTracks))
  }
  return musicStore.playlist.findIndex((t) => t.title.includes(name))
}

function openStudyRoom() {
  if (minimalMode.value) return
  studyRoomOpen.value = true
  document.body.style.overflow = 'hidden'
}

function closeStudyRoom() {
  studyRoomOpen.value = false
  document.body.style.overflow = ''
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {})
  }
}

function cycleStudyScene() {
  const idx = pomoCompanions.findIndex((c) => c.id === companionId.value)
  const next = pomoCompanions[(idx + 1) % pomoCompanions.length]
  selectCompanion(next.id)
}

async function toggleStudyFullscreen() {
  const el = studyRoomRef.value?.roomRef
  if (!document.fullscreenElement) {
    await el?.requestFullscreen?.()
  } else {
    await document.exitFullscreen()
  }
}

async function toggleStudyAmbient() {
  initMusicEngine()
  if (musicStore.isPlaying) {
    pausePlayback()
    return
  }
  const idx = findAmbientIndex(activeCompanion.value.ambientTrack)
  if (idx >= 0) {
    await playTrackAtIndex(idx)
  } else {
    message.value = '未找到氛围曲目，请先在音乐室确认歌单'
  }
}

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

async function syncTimer() {
  if (!running.value) return
  const remaining = Math.round((deadline - Date.now()) / 1000)
  if (remaining <= 0) {
    clearTick()
    running.value = false
    const completedSec = totalSeconds.value
    secondsLeft.value = 0
    await onSessionComplete(completedSec)
    return
  }
  secondsLeft.value = remaining
}

function toggleTimer() {
  if (running.value) {
    clearTick()
    running.value = false
    return
  }
  requestNotifyPermission()
  running.value = true
  // 以截止时间戳为准，后台标签被节流也能算准剩余时间
  deadline = Date.now() + secondsLeft.value * 1000
  tickId = setInterval(syncTimer, 1000)
}

function onVisibilityChange() {
  if (!document.hidden) void syncTimer()
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

function toggleSettings() {
  showSettings.value = !showSettings.value
  // 移动端设置面板在下方，展开后滚动过去，避免看起来「点了没反应」。
  if (showSettings.value) {
    nextTick(() => {
      settingsRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
}

async function toggleFullscreen() {
  // 桌面端优先用原生全屏；移动端（尤其 iOS Safari）不支持元素全屏，
  // 原生调用可能不存在或直接 reject，这里统一兜底为纯 CSS 全屏，保证一定有反应。
  if (!isFullscreen.value) {
    isFullscreen.value = true
    try {
      await focusArea.value?.requestFullscreen?.()
    } catch {
      /* 移动端不支持原生全屏，退回 CSS 全屏即可 */
    }
  } else {
    isFullscreen.value = false
    try {
      if (document.fullscreenElement) await document.exitFullscreen()
    } catch {
      /* ignore */
    }
  }
}

function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

watch(isFullscreen, (on) => {
  // CSS 兜底全屏时锁定背景滚动；原生全屏由浏览器处理，这里也无副作用。
  document.body.style.overflow = on ? 'hidden' : ''
})

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

watch(studyMemo, (value) => {
  try {
    localStorage.setItem(STUDY_MEMO_KEY, value)
  } catch {
    /* ignore */
  }
})

watch(settings, () => {
  if (settings.value.notify) requestNotifyPermission()
}, { deep: true })

onMounted(() => {
  applyModeDuration()
  loadData()
  document.addEventListener('fullscreenchange', onFullscreenChange)
  document.addEventListener('visibilitychange', onVisibilityChange)
  lineTickId = setInterval(() => {
    if (running.value) lineTick.value += 1
  }, 12000)
  if (route.query.room === '1' && !minimalMode.value) openStudyRoom()
})

onUnmounted(() => {
  clearTick()
  if (lineTickId) clearInterval(lineTickId)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  document.removeEventListener('visibilitychange', onVisibilityChange)
  if (studyRoomOpen.value || isFullscreen.value) document.body.style.overflow = ''
})
</script>

<style scoped>
.pomo-page.fullscreen :deep(.platform-page__header) {
  display: none;
}

.pomo-page.fullscreen :deep(.platform-page) {
  padding-bottom: 0;
}

.pomo-strip {
  margin-bottom: 1rem;
}

.pomo-enter-study {
  white-space: nowrap;
}

.pomo-page--minimal :deep(.platform-page__header--ink) {
  display: none;
}

.pomo-core--minimal {
  border-left-color: var(--orange);
  min-height: min(68vh, 640px);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.pomo-main--centered {
  width: 100%;
  max-width: min(440px, 100%);
  margin-inline: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pomo-main--centered .top-row {
  width: 100%;
  justify-content: center;
  gap: 0.65rem;
}

.pomo-main--centered .mode-block {
  text-align: center;
  flex: 1 1 auto;
}

.pomo-main--centered .top-actions {
  flex-shrink: 0;
}

.pomo-main--centered .focus-quote,
.pomo-main--centered .cycle-dots,
.pomo-main--centered .timer-actions,
.pomo-main--centered .warn,
.pomo-main--centered .success,
.pomo-main--centered .error {
  width: 100%;
}

.pomo-main--centered .task-label {
  width: 100%;
  max-width: 360px;
}

.pomo-main--centered :deep(.pomo-energy) {
  width: min(320px, 88vw);
}

.pomo-reflect-modal--minimal {
  border-left-color: var(--orange);
}

.pomo-core {
  position: relative;
  text-align: center;
  overflow: hidden;
  --pomo-accent: var(--orange);
  border-left: 3px solid var(--pomo-accent);
}

.pomo-deco-bg {
  position: absolute;
  inset: -10%;
  background-size: cover;
  background-position: 70% center;
  opacity: 0.07;
  filter: saturate(1.1) blur(2px);
  pointer-events: none;
  transition: opacity 0.35s ease;
}

.pomo-core--break .pomo-deco-bg {
  opacity: 0.1;
  filter: saturate(0.95) blur(1px) hue-rotate(15deg);
}

.pomo-petals {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
  background-image:
    radial-gradient(circle at 12% 18%, color-mix(in srgb, var(--pomo-accent) 35%, transparent) 0 2px, transparent 3px),
    radial-gradient(circle at 78% 24%, color-mix(in srgb, var(--pomo-accent) 25%, transparent) 0 2px, transparent 3px),
    radial-gradient(circle at 44% 72%, color-mix(in srgb, var(--pomo-accent) 30%, transparent) 0 2px, transparent 3px);
  animation: pomo-sparkle 6s ease-in-out infinite;
}

.pomo-core--break .pomo-petals {
  opacity: 0.55;
}

.pomo-core--running.pomo-core--focus .pomo-petals {
  opacity: 0.35;
}

@keyframes pomo-sparkle {
  0%, 100% { transform: translateY(0); opacity: 0.25; }
  50% { transform: translateY(-4px); opacity: 0.5; }
}

.pomo-stage {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(180px, 240px) 1fr;
  gap: 1.25rem;
  align-items: start;
  text-align: left;
}

.pomo-stage.pomo-stage--solo {
  flex: 1;
  grid-template-columns: 1fr;
  justify-items: center;
  align-content: center;
  width: 100%;
}

.pomo-core--minimal .pomo-stage {
  flex: 1;
  align-content: center;
}

.pomo-main {
  text-align: center;
  min-width: 0;
}

.pomo-companion {
  display: grid;
  gap: 0.75rem;
}

.pomo-portrait {
  width: 100%;
  max-width: 200px;
  aspect-ratio: 1;
  height: auto;
}

.pomo-bubble {
  position: relative;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg-paper) 88%, var(--pomo-accent));
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
}

.pomo-bubble::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 8px;
  height: 8px;
  background: var(--pomo-accent);
  clip-path: polygon(100% 0, 0 100%, 100% 100%);
}

.pomo-bubble__tag {
  margin: 0 0 0.35rem;
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--pomo-accent);
}

.pomo-bubble__line {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.55;
  color: var(--text);
}

.pomo-chips {
  margin-top: 0.15rem;
}

.pomo-picker__label {
  margin: 0 0 0.35rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.pomo-picker__row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.pomo-picker__btn {
  width: 40px;
  height: 40px;
  padding: 0;
  border: 2px solid var(--border);
  background: var(--bg);
  cursor: pointer;
  overflow: hidden;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 6px), calc(100% - 6px) 100%, 0 100%);
  transition: border-color 0.15s, transform 0.15s;
}

.pomo-picker__btn img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.pomo-picker__btn:hover,
.pomo-picker__btn.active {
  border-color: var(--pomo-accent);
  transform: translateY(-1px);
}

.pomo-fs-companion {
  position: absolute;
  right: 1.25rem;
  bottom: 1.25rem;
  max-width: min(220px, 28vw);
  margin: 0;
  text-align: center;
  z-index: 2;
}

.pomo-fs-companion img {
  width: 100%;
  border: 2px solid var(--border);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%);
  filter: saturate(0.92);
}

.pomo-fs-companion figcaption {
  margin-top: 0.45rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.pomo-reflect-modal {
  border-left-color: var(--pomo-accent, var(--orange));
}

.reflect-hero {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 0.85rem;
  align-items: start;
  margin-bottom: 0.75rem;
}

.reflect-portrait {
  width: 100px;
  height: 100px;
}

.reflect-prompt {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 0.5rem;
}

.pomo-core.fs-mode {
  /* 兼顾原生全屏与移动端 CSS 兜底全屏：固定铺满视口。 */
  position: fixed;
  inset: 0;
  z-index: 1200;
  width: 100vw;
  height: 100vh;
  min-height: 100vh;
  margin: 0;
  border: none;
  background: var(--bg);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.pomo-core.fs-mode .pomo-stage {
  grid-template-columns: 1fr;
  width: 100%;
  max-width: 520px;
}

.cockpit-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.06;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 20px 20px;
}

.top-row {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  z-index: 1;
}

.mode-block { text-align: left; }

.mode-tag {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  color: var(--orange);
  margin: 0;
}

.mode-label {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0.2rem 0 0;
}

.top-actions { display: flex; gap: 0.35rem; }

.icon-btn {
  background: transparent;
  border: 1px solid var(--border);
  width: 32px;
  height: 32px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.icon-btn:hover {
  border-color: var(--orange);
  color: var(--orange);
}

.focus-quote {
  position: relative;
  z-index: 1;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin: 0.75rem 0 0.5rem;
  opacity: 0.85;
}

.cycle-dots {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  gap: 0.45rem;
  margin-bottom: 0.5rem;
}

.cycle-dot {
  width: 10px;
  height: 10px;
  border: 1px solid var(--border);
  background: transparent;
  transform: rotate(45deg);
  transition: background 0.2s, border-color 0.2s;
}

.cycle-dot--done {
  background: color-mix(in srgb, var(--orange) 45%, transparent);
  border-color: var(--orange);
}

.cycle-dot--current {
  background: var(--orange);
  border-color: var(--orange);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--orange) 25%, transparent);
}

.pomo-main :deep(.pomo-mag) {
  margin-bottom: 0.5rem;
}

.task-label {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 0.35rem;
  font-family: var(--mono);
  font-size: 0.78rem;
  margin-bottom: 1rem;
  max-width: 360px;
  width: 100%;
  margin-inline: auto;
}

.task-label input {
  border: 1px solid var(--border);
  padding: 0.55rem 0.65rem;
  font: inherit;
  background: var(--bg);
}

.timer-actions {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.panel-head {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.panel-head h2 {
  font-size: 0.95rem;
  margin: 0;
}

.panel-sub {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin: 0;
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
}

.stat-cell {
  text-align: center;
  padding: 0.65rem 0.35rem;
  border: 1px dashed var(--border);
  background: color-mix(in srgb, var(--bg) 70%, transparent);
}

.stat-num {
  display: block;
  font-family: var(--mono);
  font-size: 1.5rem;
  color: var(--orange);
}

.stat-label { font-size: 0.72rem; color: var(--text-muted); }

.chart-wrap {
  position: relative;
  height: 150px;
}

.chart-grid {
  position: absolute;
  inset: 0 0 1.5rem;
  background-image: linear-gradient(var(--border) 1px, transparent 1px);
  background-size: 100% 24px;
  opacity: 0.35;
  pointer-events: none;
}

.chart-bars {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  height: 100%;
  padding-bottom: 0;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-value {
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
  min-height: 0.85rem;
}

.bar {
  width: 100%;
  max-width: 36px;
  margin-top: auto;
  background: linear-gradient(to top, color-mix(in srgb, var(--orange) 55%, #fff), var(--orange));
  min-height: 4px;
  border-radius: 2px 2px 0 0;
  transition: height 0.3s, filter 0.15s;
}

.bar-col:hover .bar {
  filter: brightness(1.08);
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
  border-left: 3px solid var(--orange);
}

.modal-tag {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--orange);
  margin: 0 0 0.35rem;
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

@media (max-width: 860px) {
  .pomo-stage {
    grid-template-columns: 1fr;
  }

  .pomo-companion {
    grid-template-columns: 100px 1fr;
    grid-template-areas:
      'portrait bubble'
      'chips chips'
      'picker picker';
    align-items: start;
  }

  .pomo-portrait {
    grid-area: portrait;
    max-width: 100px;
  }

  .pomo-bubble { grid-area: bubble; }

  .pomo-chips { grid-area: chips; }

  .pomo-picker { grid-area: picker; }

  .reflect-hero {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .reflect-portrait {
    margin-inline: auto;
  }
}

@media (max-width: 560px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .settings-grid { grid-template-columns: 1fr; }
}
</style>
<template>
  <div
    ref="roomRef"
    class="pomo-study-room"
    :class="{
      'pomo-study-room--focus': mode === 'focus',
      'pomo-study-room--break': mode === 'break',
      'pomo-study-room--running': running,
    }"
    :style="roomStyle"
  >
    <div class="pomo-study-room__bg" :style="{ backgroundImage: `url(${companionImg})` }" aria-hidden="true" />
    <div class="pomo-study-room__dim" aria-hidden="true" />
    <div class="pomo-study-room__embers" aria-hidden="true" />
    <div class="pomo-study-room__vignette" aria-hidden="true" />

    <header class="pomo-study-room__head">
      <div class="pomo-study-room__brand">
        <p class="pomo-study-room__eyebrow">CYINC · STUDY ROOM</p>
        <h1 class="pomo-study-room__title">Study With {{ companion.name }}</h1>
        <p class="pomo-study-room__subtitle">{{ companion.series }}</p>
      </div>
      <div class="pomo-study-room__head-actions">
        <time class="pomo-study-room__clock" :datetime="clockIso">{{ wallClock }}</time>
        <button type="button" class="study-btn" @click="$emit('switch-scene')">切换</button>
        <button type="button" class="study-btn" @click="$emit('toggle-fullscreen')">全屏</button>
        <button type="button" class="study-btn study-btn--ghost" @click="$emit('close')">退出</button>
      </div>
    </header>

    <main class="pomo-study-room__stage">
      <div class="pomo-study-room__timer-zone">
        <span class="pomo-study-room__round" aria-label="已完成专注轮数">{{ focusCount }}</span>
        <button
          type="button"
          class="pomo-study-room__time"
          :class="{ 'is-running': running }"
          @click="$emit('toggle-timer')"
        >
          {{ displayTime }}
        </button>
        <p class="pomo-study-room__mode">{{ modeLabel }}</p>
        <p v-if="taskLabel" class="pomo-study-room__task">{{ taskLabel }}</p>
        <p class="pomo-study-room__hint">点击时间 · 开始 / 暂停</p>
        <div class="pomo-study-room__controls">
          <button type="button" class="study-btn study-btn--primary" @click="$emit('toggle-timer')">
            {{ running ? '暂停' : secondsLeft === totalSeconds ? '开始' : '继续' }}
          </button>
          <button type="button" class="study-btn study-btn--ghost" @click="$emit('reset')">重置</button>
          <button type="button" class="study-btn study-btn--ghost" @click="$emit('switch-mode')">
            {{ mode === 'focus' ? '休息' : '专注' }}
          </button>
        </div>
      </div>

      <section
        ref="chatSectionRef"
        class="pomo-study-room__chat study-chat"
        :class="{ 'is-dragging': isDragging, 'is-resizing': isResizing }"
        :style="chatStyle"
        aria-label="自习室聊天室"
      >
        <header
          class="study-chat__head study-chat__head--draggable"
          @mousedown.prevent="startDrag"
          @dblclick.prevent="resetChat"
          title="拖动改位置 · 双击重置"
        >
          <span class="study-chat__dot" :class="{ 'is-on': socketReady, 'is-flash': showCountFlash }"></span>
          <span class="study-chat__title" :class="{ 'is-flash': showCountFlash }">在线 {{ onlineCount }} 人 · 全局自习室</span>
          <span class="study-chat__status" v-if="chatError">{{ chatError }}</span>
          <button
            type="button"
            class="study-chat__emoji-btn"
            :aria-expanded="emojiOpen"
            title="表情包"
            @mousedown.stop
            @click="emojiOpen = !emojiOpen"
          >😀</button>
          <button
            type="button"
            class="study-chat__reset-btn"
            title="重置位置/大小"
            @mousedown.stop
            @click="resetChat"
          >↺</button>
        </header>
        <div v-if="emojiOpen" class="study-chat__emoji-panel" @mousedown.stop>
          <button
            v-for="st in chatStickers"
            :key="st.id"
            type="button"
            class="study-chat__emoji-item"
            :title="st.label"
            @click="sendSticker(st)"
          >
            <img :src="stickerUrl(st)" :alt="st.label" loading="lazy" />
          </button>
        </div>
        <ul ref="listRef" class="study-chat__list" @scroll.passive="onListScroll">
          <li v-if="messages.length === 0" class="study-chat__empty">还没有人发言,来聊一句吧 ☕</li>
          <li
            v-for="m in messages"
            :key="m.id"
            class="study-chat__item"
            :class="{ 'is-mine': m.user_id === myUserId }"
          >
            <span class="study-chat__avatar" :style="avatarStyle(m)" :title="m.nickname || m.username">
              {{ (m.nickname || m.username || '?').slice(0,1) }}
            </span>
            <div class="study-chat__body">
              <div class="study-chat__meta">
                <span class="study-chat__name">{{ m.nickname || m.username }}</span>
                <time class="study-chat__time" :datetime="m.created_at">{{ formatTime(m.created_at) }}</time>
              </div>
              <img
            v-if="m.message_type === 'sticker' && m.sticker_url"
            class="study-chat__sticker"
            :src="resolveMediaUrl(m.sticker_url)"
            :alt="m.content || 'sticker'"
            loading="lazy"
            @error="onStickerError($event)"
          />
          <p v-else class="study-chat__text">{{ m.content }}</p>
            </div>
          </li>
        </ul>
        <form class="study-chat__form" @submit.prevent="onSend">
          <input
            ref="inputRef"
            v-model="draft"
            class="study-chat__input"
            :class="{ 'is-shake': shake }"
            type="text"
            maxlength="500"
            placeholder="说点什么…(Enter 发送,Shift+Enter 换行)"
            :disabled="!canSend"
            @keydown.enter.exact.prevent="onSend"
          />
          <button
            type="submit"
            class="study-chat__send"
            :disabled="!canSend || !draft.trim()"
          >发送</button>
        </form>
        <!-- 8 方向 resize -->
        <div class="study-chat__handle study-chat__handle--n"  @mousedown.prevent.stop="startResize($event, 'n')"></div>
        <div class="study-chat__handle study-chat__handle--s"  @mousedown.prevent.stop="startResize($event, 's')"></div>
        <div class="study-chat__handle study-chat__handle--e"  @mousedown.prevent.stop="startResize($event, 'e')"></div>
        <div class="study-chat__handle study-chat__handle--w"  @mousedown.prevent.stop="startResize($event, 'w')"></div>
        <div class="study-chat__handle study-chat__handle--nw" @mousedown.prevent.stop="startResize($event, 'nw')"></div>
        <div class="study-chat__handle study-chat__handle--ne" @mousedown.prevent.stop="startResize($event, 'ne')"></div>
        <div class="study-chat__handle study-chat__handle--sw" @mousedown.prevent.stop="startResize($event, 'sw')"></div>
        <div class="study-chat__handle study-chat__handle--se" @mousedown.prevent.stop="startResize($event, 'se')"></div>
        <div v-if="isResizing" class="study-chat__size-badge">{{ resizeBadge }}</div>
      </section>
    
    </main>

    <aside class="pomo-study-room__side">
      <button
        type="button"
        class="pomo-study-room__side-toggle"
        :aria-expanded="memoOpen"
        @click="memoOpen = !memoOpen"
      >
        {{ memoOpen ? '收起备忘' : '自习备忘' }}
      </button>
      <div v-show="memoOpen" class="pomo-study-room__memo">
        <textarea
          :value="memo"
          rows="5"
          maxlength="500"
          placeholder="随手记一点…（仅保存在本机）"
          @input="$emit('update:memo', ($event.target).value)"
        />
      </div>
    </aside>

    <footer class="pomo-study-room__bar">
      <button type="button" class="pomo-study-room__music" @click="$emit('toggle-ambient')">
        <span class="pomo-study-room__music-icon">{{ ambientPlaying ? '❚❚' : '♫' }}</span>
        <span class="pomo-study-room__music-text">{{ ambientLabel }}</span>
      </button>
    </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import {
  fetchStudyRoomMessages,
  fetchStudyRoomOnline,
  fetchProfile,
  getPlatformToken,
  openStudyRoomSocket,
  resolveMediaUrl,
} from '../../api/platform.js'
import { chatStickers, stickerUrl } from '../../data/chatStickers.js'

const props = defineProps({
  companion: { type: Object, required: true },
  companionImg: { type: String, required: true },
  companionLine: { type: String, default: '' },
  displayTime: { type: String, required: true },
  mode: { type: String, required: true },
  modeLabel: { type: String, required: true },
  focusCount: { type: Number, default: 0 },
  running: { type: Boolean, default: false },
  secondsLeft: { type: Number, default: 0 },
  totalSeconds: { type: Number, default: 0 },
  taskLabel: { type: String, default: '' },
  ambientLabel: { type: String, default: '氛围音 · 关' },
  ambientPlaying: { type: Boolean, default: false },
  memo: { type: String, default: '' },
})

defineEmits([
  'close',
  'switch-scene',
  'toggle-fullscreen',
  'toggle-timer',
  'reset',
  'switch-mode',
  'toggle-ambient',
  'update:memo',
])

const roomRef = ref(null)
const chatSectionRef = ref(null)
const memoOpen = ref(false)
const wallClock = ref('--:--')
const clockIso = ref('')
let clockId = null

/* chat 位置(localStorage 记忆) */
const CHAT_POS_KEY = 'pomo:chat-pos'
const chatPos = ref({ x: 0, y: 0 })
const CHAT_DEFAULT_W = 360
const CHAT_DEFAULT_H = 480
const chatSize = ref({ width: CHAT_DEFAULT_W, height: CHAT_DEFAULT_H })
const dragState = ref(null)
const isDragging = ref(false)
const isResizing = ref(false)
const resizeBadge = ref('')
const showCountFlash = ref(false)
let countFlashTimer = 0
const emojiOpen = ref(false)
let chatPersistTimer = 0

const chatStyle = computed(() => ({
  transform: `translate(${chatPos.value.x}px, ${chatPos.value.y}px)`,
  width: chatSize.value.width + 'px',
  height: chatSize.value.height + 'px',
}))

const messages = ref([])
const draft = ref('')
const onlineCount = ref(0)
const socketReady = ref(false)
const chatError = ref('')
const myUserId = ref(null)
const shake = ref(false)
const listRef = ref(null)
const inputRef = ref(null)
const loadingHistory = ref(false)
const historyExhausted = ref(false)
let socket = null
let presenceTimer = null
let profileTimer = null
let profileRetry = 0
let stickToBottom = true

const roomStyle = computed(() => ({
  '--study-accent': props.companion.accent,
  '--study-bg': props.companion.sceneGradient || '#0a0a0c',
}))

function tickClock() {
  const now = new Date()
  wallClock.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
  clockIso.value = now.toISOString()
}

function relativeTime(iso) {
  if (!iso) return ''
  const t = new Date(iso).getTime()
  if (Number.isNaN(t)) return ''
  const diff = Math.max(0, Date.now() - t)
  if (diff < 45 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / 3600000)} 小时前`
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
function formatTime(iso) { return relativeTime(iso) }

function avatarStyle(m) {
  const url = m && m.avatar
  const full = url ? resolveMediaUrl(url) : ''
  if (!full) return {}
  return { backgroundImage: `url(${full})`, color: 'transparent' }
}

function scrollToBottom(force = false) {
  const el = listRef.value
  if (!el) return
  if (force || stickToBottom) {
    nextTick(() => { el.scrollTop = el.scrollHeight })
  }
}

function onListScroll(ev) {
  const el = ev.target
  const dist = el.scrollHeight - el.scrollTop - el.clientHeight
  stickToBottom = dist < 80
}

function pushIncoming(item) {
  if (!item || item.id == null) return
  // 已在就忽略
  if (messages.value.some((m) => m.id === item.id)) return
  messages.value.push(item)
  scrollToBottom()
}

function applyHistory(items) {
  if (!Array.isArray(items)) return
  // items 已是 desc 顺序
  for (const it of items) pushIncoming(it)
  historyExhausted.value = items.length < 50
  scrollToBottom(true)
}

async function loadMoreHistory() {
  if (loadingHistory.value || historyExhausted.value) return
  if (messages.value.length === 0) return
  loadingHistory.value = true
  try {
    const oldestId = messages.value[0].id
    const res = await fetchStudyRoomMessages({ before: oldestId, limit: 50 })
    const items = (res && res.data && res.data.items) || []
    const before = messages.value.length
    for (const it of items) pushIncoming(it)
    historyExhausted.value = items.length < 50 || messages.value.length === before
  } catch (e) {
    chatError.value = '加载历史失败'
  } finally {
    loadingHistory.value = false
  }
}

async function refreshOnline() {
  try {
    const res = await fetchStudyRoomOnline()
    const data = (res && res.data) || {}
    onlineCount.value = Number(data.count) || 0
  } catch (e) {
    // ignore
  }
}

function ensureProfile() {
  if (profileTimer) return
  profileTimer = setTimeout(async () => {
    profileTimer = null
    if (myUserId.value) return
    const token = getPlatformToken()
    if (!token) { profileRetry = Math.min(profileRetry + 1, 6); return }
    try {
      const res = await fetchProfile()
      const u = (res && res.data) || {}
      if (u && (u.id != null)) myUserId.value = u.id
    } catch (e) {
      profileRetry = Math.min(profileRetry + 1, 6)
    }
  }, 300)
}

watch(onlineCount, (n, old) => {
  if (old != null && n !== old) {
    showCountFlash.value = true
    if (countFlashTimer) clearTimeout(countFlashTimer)
    countFlashTimer = window.setTimeout(() => { showCountFlash.value = false }, 600)
  }
})

function connectChat() {
  if (socket) return
  const token = getPlatformToken()
  if (!token) {
    chatError.value = '登录后即可发言'
    socketReady.value = false
    return
  }
  socket = openStudyRoomSocket({
    token,
    onOpen: () => {
      socketReady.value = true
      chatError.value = ''
    },
    onClose: () => {
      socketReady.value = false
    },
    onError: () => {
      socketReady.value = false
    },
    onMessage: (data) => {
      if (data.type === 'history') {
        messages.value = []
        applyHistory(data.items || [])
      } else if (data.type === 'msg') {
        pushIncoming(data)
      } else if (data.type === 'err') {
        if (data.reason === 'rate') {
          chatError.value = '发言太快,稍等再发'
        } else if (data.reason === 'too_long') {
          chatError.value = '消息过长(<=500 字)'
        } else {
          chatError.value = '发送失败'
        }
        shake.value = true
        setTimeout(() => { shake.value = false }, 400)
        setTimeout(() => { if (chatError.value && chatError.value.indexOf('太快') >= 0) chatError.value = '' }, 2500)
      }
    },
    onPresence: (data) => {
      // presence 事件直接带 count,实时更新(不靠 10s 轮询)
      const c = data && typeof data.count === 'number' ? data.count : null
      if (c != null) {
        onlineCount.value = c
      } else {
        refreshOnline()
      }
    },
  })
}

function clampChatPos(x, y) {
  const stage = document.querySelector('.pomo-study-room')
  const el = chatSectionRef.value
  if (!stage || !el) return { x, y }
  const sr = stage.getBoundingClientRect()
  const er = el.getBoundingClientRect()
  const minX = 24 - er.left + sr.left
  const maxX = sr.right - er.right - 24
  const minY = 60 - er.top + sr.top
  const maxY = sr.bottom - er.bottom - 24
  return {
    x: Math.max(minX, Math.min(maxX, x)),
    y: Math.max(minY, Math.min(maxY, y)),
  }
}

function clampChatSize(w, h) {
  const stage = document.querySelector('.pomo-study-room')
  const MIN_W = 240
  const MIN_H = 280
  if (!stage) return { width: Math.max(MIN_W, w), height: Math.max(MIN_H, h) }
  const sr = stage.getBoundingClientRect()
  const maxW = Math.max(MIN_W, sr.width - 48)
  const maxH = Math.max(MIN_H, sr.height - 120)
  return {
    width: Math.max(MIN_W, Math.min(maxW, w)),
    height: Math.max(MIN_H, Math.min(maxH, h)),
  }
}

function startResize(ev, dir = 'br') {
  if (ev.button !== 0) return
  ev.stopPropagation()
  ev.preventDefault()
  const el = chatSectionRef.value
  if (!el) return
  isResizing.value = true
  const startW = el.offsetWidth
  const startH = el.offsetHeight
  const startX = ev.clientX
  const startY = ev.clientY
  const onMove = (e) => {
    const dw = e.clientX - startX
    const dh = e.clientY - startY
    let nw = startW
    let nh = startH
    let nx = chatPos.value.x
    let ny = chatPos.value.y
    if (dir.includes('e')) nw = startW + dw
    if (dir.includes('s')) nh = startH + dh
    if (dir.includes('w')) { nw = startW - dw; nx = chatPos.value.x + (startW - nw) }
    if (dir.includes('n')) { nh = startH - dh; ny = chatPos.value.y + (startH - nh) }
    const clamped = clampChatSize(nw, nh)
    // 如果被夹住,补偿位置避免视觉跳
    if (clamped.width !== nw && dir.includes('w')) nx += (nw - clamped.width)
    if (clamped.height !== nh && dir.includes('n')) ny += (nh - clamped.height)
    chatSize.value = clamped
    chatPos.value = clampChatPos(nx, ny)
    resizeBadge.value = `${clamped.width} × ${clamped.height}`
  }
  const onUp = () => {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
    isResizing.value = false
    resizeBadge.value = ''
    chatPos.value = clampChatPos(chatPos.value.x, chatPos.value.y)
    persistChatPos()
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function startDrag(ev) {
  if (ev.button !== 0) return
  const el = chatSectionRef.value
  if (!el) return
  isDragging.value = true
  dragState.value = {
    startX: ev.clientX,
    startY: ev.clientY,
    baseX: chatPos.value.x,
    baseY: chatPos.value.y,
  }
  const onMove = (e) => {
    if (!dragState.value) return
    const dx = e.clientX - dragState.value.startX
    const dy = e.clientY - dragState.value.startY
    let nx = dragState.value.baseX + dx
    let ny = dragState.value.baseY + dy
    // 边缘吸附:离边 18px 内时夹到 12px
    const stage = document.querySelector('.pomo-study-room')
    if (stage && el) {
      const sr = stage.getBoundingClientRect()
      const er = el.getBoundingClientRect()
      if (er.left - sr.left < 18) nx = 24 - (er.left - sr.left)
      if (sr.right - er.right < 18) nx = (sr.right - er.right) - 24
      if (er.top - sr.top < 18) ny = 60 - (er.top - sr.top)
      if (sr.bottom - er.bottom < 18) ny = (sr.bottom - er.bottom) - 24
    }
    chatPos.value = clampChatPos(nx, ny)
  }
  const onUp = () => {
    dragState.value = null
    isDragging.value = false
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
    persistChatPos()
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function persistChatPos() {
  if (chatPersistTimer) return
  chatPersistTimer = window.setTimeout(() => {
    chatPersistTimer = 0
    try {
      localStorage.setItem(CHAT_POS_KEY, JSON.stringify({ ...chatPos.value, ...chatSize.value }))
    } catch (e) {}
  }, 400)
}

function resetChat() {
  chatPos.value = { x: 0, y: 0 }
  chatSize.value = { width: CHAT_DEFAULT_W, height: CHAT_DEFAULT_H }
  persistChatPos()
}

function centerChat() {
  chatPos.value = { x: 0, y: 0 }
  persistChatPos()
}

function loadChatPos() {
  try {
    const raw = localStorage.getItem(CHAT_POS_KEY)
    if (!raw) return
    const data = JSON.parse(raw)
    if (data && typeof data.x === 'number' && typeof data.y === 'number') {
      chatPos.value = { x: data.x, y: data.y }
    }
    if (data && typeof data.width === 'number' && typeof data.height === 'number') {
      chatSize.value = { width: data.width, height: data.height }
    }
  } catch (e) {}
}

function sendSticker(s) {
  if (!canSend.value) return
  const url = stickerUrl(s)
  const ok = socket && socket.send(JSON.stringify({ type: 'msg', content: null, sticker_url: url }))
  if (ok) emojiOpen.value = false
}

function onStickerError(ev) {
  const el = ev && ev.target
  if (!el) return
  el.classList.add('is-broken')
  el.alt = '[图片加载失败]'
}

function disconnectChat() {
  if (socket) {
    try { socket.close() } catch (e) {}
    socket = null
  }
  socketReady.value = false
}

const canSend = computed(() => !!getPlatformToken() && socketReady.value)

function onSend() {
  const text = draft.value.trim()
  if (!text) return
  if (!canSend.value) {
    if (!getPlatformToken()) chatError.value = '请先登录再发言'
    else chatError.value = '正在连接…'
    shake.value = true
    setTimeout(() => { shake.value = false }, 400)
    return
  }
  if (text.length > 500) {
    chatError.value = '消息过长(<=500 字)'
    shake.value = true
    setTimeout(() => { shake.value = false }, 400)
    return
  }
  const ok = socket && socket.send(text)
  if (ok) {
    draft.value = ''
    chatError.value = ''
  } else {
    chatError.value = '发送失败,请重试'
    shake.value = true
    setTimeout(() => { shake.value = false }, 400)
  }
}

onMounted(() => {
  tickClock()
  clockId = setInterval(tickClock, 1000)
  loadChatPos()
  // 点击 chat 区域外关闭 emoji 面板
  const onDocClick = (e) => {
    const root = chatSectionRef.value
    if (!root) return
    if (!root.contains(e.target)) emojiOpen.value = false
  }
  document.addEventListener('mousedown', onDocClick)
  if (chatSectionRef.value) chatSectionRef.value.__onDocClick = onDocClick
  // 初始拉历史 + 在线 + 试连 WS
  refreshOnline()
  presenceTimer = setInterval(refreshOnline, 5000)
  // 拉一次历史(无需登录)
  fetchStudyRoomMessages({ limit: 50 })
    .then((res) => applyHistory((res && res.data && res.data.items) || []))
    .catch(() => {})
  // 拿 profile 识别"我"
  ensureProfile()
  // 连 WS(有 token 时)
  connectChat()
})

onUnmounted(() => {
  if (clockId) clearInterval(clockId)
  if (chatPersistTimer) { clearTimeout(chatPersistTimer); chatPersistTimer = 0 }
  try {
    const fn = chatSectionRef.value && chatSectionRef.value.__onDocClick
    if (fn) document.removeEventListener('mousedown', fn)
  } catch (e) {}
  try { localStorage.setItem(CHAT_POS_KEY, JSON.stringify({ ...chatPos.value, ...chatSize.value })) } catch (e) {}
  if (presenceTimer) clearInterval(presenceTimer)
  if (profileTimer) clearTimeout(profileTimer)
  disconnectChat()
})

defineExpose({ roomRef })
</script>

<style scoped>
.pomo-study-room {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 1fr auto;
  background: var(--study-bg, #0a0a0c);
  color: #f2f2f2;
  overflow: hidden;
  font-family: var(--mono, ui-monospace, monospace);
}

.pomo-study-room__bg {
  position: absolute;
  inset: -8%;
  background-size: cover;
  background-position: 70% bottom;
  opacity: 1;
  filter: none;
  pointer-events: none;
}

.pomo-study-room__dim {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.32);
  pointer-events: none;
  z-index: 1;
}

.pomo-study-room__embers {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(circle at 18% 82%, color-mix(in srgb, var(--study-accent) 45%, transparent) 0 2px, transparent 3px),
    radial-gradient(circle at 72% 68%, color-mix(in srgb, var(--study-accent) 35%, transparent) 0 2px, transparent 3px),
    radial-gradient(circle at 44% 90%, rgba(255, 180, 100, 0.35) 0 1px, transparent 2px),
    radial-gradient(circle at 88% 42%, color-mix(in srgb, var(--study-accent) 25%, transparent) 0 2px, transparent 3px);
  animation: study-ember 8s ease-in-out infinite;
}

.pomo-study-room--running .pomo-study-room__embers {
  animation-duration: 5s;
  opacity: 0.9;
}

@keyframes study-ember {
  0%, 100% { transform: translateY(0); opacity: 0.55; }
  50% { transform: translateY(-6px); opacity: 0.85; }
}

.pomo-study-room__vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(ellipse 90% 80% at 50% 50%, transparent 40%, rgba(0, 0, 0, 0.65) 100%);
}

.pomo-study-room__head {
  position: relative;
  z-index: 2;
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem clamp(1rem, 3vw, 2rem) 0.5rem;
}

.pomo-study-room__eyebrow {
  margin: 0;
  font-size: 0.62rem;
  letter-spacing: 0.16em;
  color: color-mix(in srgb, var(--study-accent) 80%, #fff);
  opacity: 0.85;
}

.pomo-study-room__title {
  margin: 0.25rem 0 0;
  font-size: clamp(1.35rem, 3vw, 1.85rem);
  font-weight: 600;
  letter-spacing: 0.04em;
}

.pomo-study-room__subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.55);
}

.pomo-study-room__head-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  justify-content: flex-end;
  align-items: center;
}

.pomo-study-room__clock {
  font-size: clamp(1rem, 2vw, 1.25rem);
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.72);
  margin-right: 0.35rem;
}

.pomo-study-room__stage {
  position: relative;
  z-index: 2;
  grid-column: 1;
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(320px, 38vw);
  align-items: end;
  gap: clamp(0.5rem, 4vw, 2rem);
  padding: 0 clamp(1rem, 4vw, 3rem) clamp(1rem, 3vh, 2rem);
  min-height: 0;
}

.pomo-study-room__timer-zone {
  align-self: center;
  text-align: left;
  padding-bottom: 8vh;
}

.pomo-study-room__round {
  display: block;
  font-size: clamp(1.5rem, 4vw, 2.25rem);
  color: rgba(255, 255, 255, 0.45);
  line-height: 1;
  margin-bottom: 0.35rem;
}

.pomo-study-room__time {
  display: block;
  margin: 0;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  font: inherit;
  font-size: clamp(3.5rem, 14vw, 7.5rem);
  font-weight: 300;
  letter-spacing: 0.06em;
  line-height: 1;
  color: #fff;
  text-shadow: 0 0 40px color-mix(in srgb, var(--study-accent) 35%, transparent);
  transition: transform 0.15s ease, color 0.15s ease;
}

.pomo-study-room__time:hover {
  transform: scale(1.02);
  color: color-mix(in srgb, var(--study-accent) 30%, #fff);
}

.pomo-study-room__time.is-running {
  color: color-mix(in srgb, var(--study-accent) 25%, #fff);
}

.pomo-study-room__mode {
  margin: 0.5rem 0 0;
  font-size: clamp(0.95rem, 2vw, 1.15rem);
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.7);
}

.pomo-study-room__task {
  margin: 0.45rem 0 0;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.5);
  max-width: 28ch;
}

.pomo-study-room__hint {
  margin: 0.65rem 0 0;
  font-size: 0.62rem;
  color: rgba(255, 255, 255, 0.35);
  letter-spacing: 0.06em;
}

.pomo-study-room__controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 1.25rem;
}

.pomo-study-room__side {
  position: relative;
  z-index: 2;
  grid-column: 2;
  grid-row: 3;
  align-self: end;
  padding: 0 1rem 5rem 0;
  max-width: 220px;
}

.pomo-study-room__chat {
  position: absolute;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 360px;
  height: 480px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: rgba(8, 10, 14, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.pomo-study-room__chat.is-dragging,
.pomo-study-room__chat.is-resizing {
  border-color: var(--orange, #ff7a45);
  box-shadow: 0 0 0 2px rgba(255, 122, 69, 0.18), 0 12px 32px rgba(0, 0, 0, 0.55);
  user-select: none;
}

.study-chat__head {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.65rem 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(0, 0, 0, 0.25);
  cursor: move;
  user-select: none;
}

/* 8 方向 resize 把手 */
.study-chat__handle {
  position: absolute;
  z-index: 3;
  user-select: none;
  touch-action: none;
  transition: background 0.15s;
}
.study-chat__handle--n  { top: 0; left: 12px; right: 12px; height: 6px; cursor: ns-resize; }
.study-chat__handle--s  { bottom: 0; left: 12px; right: 12px; height: 6px; cursor: ns-resize; }
.study-chat__handle--e  { top: 12px; bottom: 12px; right: 0; width: 6px; cursor: ew-resize; }
.study-chat__handle--w  { top: 12px; bottom: 12px; left: 0; width: 6px; cursor: ew-resize; }
.study-chat__handle--nw { top: 0; left: 0; width: 14px; height: 14px; cursor: nwse-resize; }
.study-chat__handle--ne { top: 0; right: 0; width: 14px; height: 14px; cursor: nesw-resize; }
.study-chat__handle--sw { bottom: 0; left: 0; width: 14px; height: 14px; cursor: nesw-resize; }
.study-chat__handle--se { bottom: 0; right: 0; width: 14px; height: 14px; cursor: nwse-resize; }
.study-chat__handle:hover {
  background: rgba(255, 122, 69, 0.18);
}
.study-chat__handle--nw:hover, .study-chat__handle--se:hover {
  background: linear-gradient(135deg, transparent 45%, rgba(255, 122, 69, 0.25) 50%, transparent 55%);
}
.study-chat__handle--ne:hover, .study-chat__handle--sw:hover {
  background: linear-gradient(225deg, transparent 45%, rgba(255, 122, 69, 0.25) 50%, transparent 55%);
}

.study-chat__size-badge {
  position: absolute;
  bottom: 8px;
  right: 24px;
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.75);
  border: 1px solid var(--orange, #ff7a45);
  color: #fff;
  font-size: 0.7rem;
  font-family: var(--mono, monospace);
  border-radius: 4px;
  z-index: 4;
  pointer-events: none;
}

.study-chat__reset-btn {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.15s;
}
.study-chat__reset-btn:hover {
  background: var(--orange, #ff7a45);
  color: #fff;
  border-color: var(--orange, #ff7a45);
}

.study-chat__title.is-flash,
.study-chat__dot.is-flash {
  animation: count-flash 0.6s ease;
}
@keyframes count-flash {
  0%   { color: var(--orange, #ff7a45); transform: scale(1.15); }
  100% { color: inherit; transform: scale(1); }
}

.study-chat__emoji-btn {
  margin-left: auto;
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  transition: background 0.15s, border-color 0.15s;
}

.study-chat__emoji-btn:hover {
  background: rgba(255, 255, 255, 0.16);
  border-color: color-mix(in srgb, var(--study-accent) 50%, transparent);
}

.study-chat__emoji-panel {
  position: absolute;
  top: 100%;
  right: 0.5rem;
  margin-top: 0.4rem;
  z-index: 12;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.35rem;
  padding: 0.5rem;
  background: rgba(10, 14, 22, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  max-width: 320px;
}

.study-chat__emoji-item {
  width: 52px;
  height: 52px;
  padding: 4px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.12s, border-color 0.12s, transform 0.1s;
}

.study-chat__emoji-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: color-mix(in srgb, var(--study-accent) 40%, transparent);
  transform: translateY(-1px);
}

.study-chat__emoji-item img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
}

.study-chat__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.08);
}

.study-chat__dot.is-on {
  background: #4ade80;
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.18);
  animation: study-chat-pulse 2s ease-in-out infinite;
}

@keyframes study-chat-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.18); }
}

.study-chat__title {
  font-weight: 500;
  letter-spacing: 0.04em;
}

.study-chat__status {
  margin-left: auto;
  font-size: 0.7rem;
  color: rgba(255, 180, 100, 0.85);
}

.study-chat__list {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0.75rem;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  scroll-behavior: smooth;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.study-chat__list::-webkit-scrollbar { width: 6px; }
.study-chat__list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 3px;
}

.study-chat__empty {
  margin: auto;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.85rem;
  text-align: center;
  padding: 2rem 0;
}

.study-chat__item {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  padding: 0.25rem 0;
  animation: study-chat-in 0.25s ease-out;
}

@keyframes study-chat-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.study-chat__item.is-mine { flex-direction: row-reverse; }
.study-chat__item.is-mine .study-chat__body { align-items: flex-end; }
.study-chat__item.is-mine .study-chat__text {
  background: color-mix(in srgb, var(--study-accent) 28%, rgba(255, 255, 255, 0.08));
  border-color: color-mix(in srgb, var(--study-accent) 35%, transparent);
}

.study-chat__avatar {
  flex: 0 0 auto;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #6b7280, #374151);
  background-size: cover;
  background-position: center;
  border: 1px solid rgba(255, 255, 255, 0.12);
  user-select: none;
}

.study-chat__body {
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
  max-width: min(72%, 28rem);
  min-width: 0;
}

.study-chat__meta {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.55);
}

.study-chat__name { color: rgba(255, 255, 255, 0.78); }
.study-chat__time { color: rgba(255, 255, 255, 0.35); font-variant-numeric: tabular-nums; }

.study-chat__text {
  margin: 0;
  padding: 0.5rem 0.7rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  font-size: 0.85rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.92);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.study-chat__sticker {
  display: block;
  max-width: 120px;
  max-height: 120px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  padding: 4px;
  object-fit: contain;
}

.study-chat__sticker.is-broken {
  outline: 1px dashed rgba(255, 100, 100, 0.6);
  background: rgba(255, 100, 100, 0.08);
  min-width: 80px;
  min-height: 60px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 100, 100, 0.7);
  font-size: 0.7rem;
}

.study-chat__form {
  display: flex;
  gap: 0.5rem;
  padding: 0.6rem 0.7rem 0.7rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(0, 0, 0, 0.3);
}

.study-chat__input {
  flex: 1 1 auto;
  min-width: 0;
  padding: 0.55rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(0, 0, 0, 0.35);
  color: #fff;
  font: inherit;
  font-size: 0.85rem;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.15s, background 0.15s;
}

.study-chat__input:focus {
  border-color: color-mix(in srgb, var(--study-accent) 55%, transparent);
  background: rgba(0, 0, 0, 0.5);
}

.study-chat__input:disabled { opacity: 0.45; cursor: not-allowed; }

.study-chat__input.is-shake {
  animation: study-chat-shake 0.35s ease-in-out;
  border-color: #f87171;
}

@keyframes study-chat-shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-4px); }
  40% { transform: translateX(4px); }
  60% { transform: translateX(-3px); }
  80% { transform: translateX(2px); }
}

.study-chat__send {
  flex: 0 0 auto;
  padding: 0.5rem 0.95rem;
  border: 1px solid color-mix(in srgb, var(--study-accent) 55%, transparent);
  background: color-mix(in srgb, var(--study-accent) 35%, rgba(255, 255, 255, 0.05));
  color: #fff;
  font: inherit;
  font-size: 0.8rem;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.study-chat__send:hover:not(:disabled) {
  background: color-mix(in srgb, var(--study-accent) 50%, rgba(255, 255, 255, 0.1));
}

.study-chat__send:active:not(:disabled) { transform: scale(0.97); }
.study-chat__send:disabled { opacity: 0.4; cursor: not-allowed; }

@media (prefers-reduced-motion: reduce) {
  .study-chat__dot.is-on,
  .study-chat__input.is-shake,
  .study-chat__item { animation: none; }
}


.pomo-study-room__side-toggle {
  width: 100%;
  padding: 0.45rem 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.35);
  color: rgba(255, 255, 255, 0.75);
  font: inherit;
  font-size: 0.68rem;
  cursor: pointer;
}

.pomo-study-room__side-toggle:hover {
  border-color: color-mix(in srgb, var(--study-accent) 50%, transparent);
  color: #fff;
}

.pomo-study-room__memo {
  margin-top: 0.45rem;
}

.pomo-study-room__memo textarea {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(0, 0, 0, 0.45);
  color: rgba(255, 255, 255, 0.85);
  padding: 0.55rem;
  font: inherit;
  font-size: 0.72rem;
  resize: vertical;
}

.pomo-study-room__bar {
  position: relative;
  z-index: 2;
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.65rem clamp(1rem, 3vw, 2rem) 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.35);
}

.pomo-study-room__music {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.35rem 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.85);
  font: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  max-width: min(420px, 70vw);
}

.pomo-study-room__music:hover {
  border-color: color-mix(in srgb, var(--study-accent) 45%, transparent);
}

.pomo-study-room__music-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pomo-study-room__credit {
  margin: 0;
  font-size: 0.58rem;
  color: rgba(255, 255, 255, 0.35);
  letter-spacing: 0.04em;
}

.study-btn {
  padding: 0.4rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  font: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.study-btn:hover {
  border-color: color-mix(in srgb, var(--study-accent) 55%, transparent);
  background: rgba(255, 255, 255, 0.1);
}

.study-btn--primary {
  background: color-mix(in srgb, var(--study-accent) 35%, rgba(255, 255, 255, 0.08));
  border-color: color-mix(in srgb, var(--study-accent) 50%, transparent);
}

.study-btn--ghost {
  background: transparent;
}

@media (max-width: 820px) {
  .pomo-study-room {
    grid-template-columns: 1fr;
  }

  .pomo-study-room__head {
    padding-top: 0.85rem;
  }

  .pomo-study-room__head-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .pomo-study-room__clock {
    width: 100%;
    margin: 0 0 0.25rem;
  }

  .pomo-study-room__stage {
    grid-template-columns: 1fr;
    text-align: center;
    padding-bottom: 0.5rem;
  }

  .pomo-study-room__timer-zone {
    text-align: center;
    padding-bottom: 0.5rem;
  }

  .pomo-study-room__controls {
    justify-content: center;
  }

  .pomo-study-room__chat {
    grid-column: 1;
    max-height: 46vh;
  }

  .pomo-study-room__side {
    grid-column: 1;
    grid-row: auto;
    max-width: none;
    padding: 0 1rem 0.75rem;
  }

  .pomo-study-room__bar {
    flex-direction: column;
    align-items: stretch;
  }

  .pomo-study-room__credit {
    text-align: center;
  }
}
</style>

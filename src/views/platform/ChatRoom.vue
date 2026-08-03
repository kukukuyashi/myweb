<template>
  <div class="chat-room-page">
    <PlatformPageShell
      coord="CHAT · 聊天室"
      title="自习室聊天室"
      lead="全站同学一起专注、灌水、发疯的地方。发言留痕，违规会被请出。"
    >
      <template #actions>
        <span class="chat-status" :class="{ 'is-on': socketReady, 'is-err': !!chatError }">
          <span class="chat-status__dot" />
          <span class="chat-status__label">
            {{ chatError ? chatError : (socketReady ? `LIVE · ${onlineCount} 人在聊` : `OFFLINE · ${onlineCount} 人在聊`) }}
          </span>
        </span>
      </template>

      <div class="chat-room-grid">
        <!-- 主聊天区 -->
        <section class="chat-main platform-panel ink-panel">
          <div ref="listRef" class="chat-main__list" @scroll.passive="onListScroll">
            <p v-if="loadingHistory" class="chat-main__hint">加载中…</p>
            <p v-else-if="historyExhausted && !messages.length" class="chat-main__empty">
              还没有人发言,来聊一句吧 ☕
            </p>
            <article
              v-for="m in messages"
              :key="m.id"
              class="chat-msg"
              :class="{ 'is-mine': m.user_id === myUserId }"
            >
              <span class="chat-msg__avatar" :style="avatarStyle(m)">
                {{ (m.nickname || m.username || '?').slice(0, 1) }}
              </span>
              <div class="chat-msg__body">
                <div class="chat-msg__meta">
                  <strong class="chat-msg__name">{{ m.nickname || m.username || '匿名' }}</strong>
                  <time class="chat-msg__time" :datetime="m.created_at">{{ formatTime(m.created_at) }}</time>
                </div>
                <img
                  v-if="m.message_type === 'sticker' && m.sticker_url"
                  class="chat-msg__sticker"
                  :src="resolveMediaUrl(m.sticker_url)"
                  :alt="m.content || 'sticker'"
                  loading="lazy"
                />
                <p v-else class="chat-msg__text">{{ m.content }}</p>
              </div>
            </article>
          </div>

          <form class="chat-input" :class="{ 'is-shake': shake }" @submit.prevent="onSend">
            <button
              type="button"
              class="chat-input__emoji-btn"
              :aria-expanded="emojiOpen"
              :title="emojiOpen ? '收起表情' : '打开表情'"
              @mousedown.stop
              @click="emojiOpen = !emojiOpen"
            >☺</button>
            <input
              ref="inputRef"
              v-model="draft"
              class="chat-input__field"
              type="text"
              maxlength="500"
              :placeholder="canSend ? '说点什么…  (Enter 发送 / Shift+Enter 换行)' : '登录后即可发言'"
              :disabled="!canSend"
              @keydown.enter.exact.prevent="onSend"
            />
            <button
              type="submit"
              class="chat-input__send"
              :disabled="!canSend || !draft.trim()"
            >发送</button>

            <div v-if="emojiOpen" class="chat-input__emoji-panel" @mousedown.stop @click.stop>
              <button
                v-for="st in chatStickers"
                :key="st.id"
                type="button"
                class="chat-input__emoji-item"
                :title="st.label"
                :disabled="!canSend"
                @mousedown.stop
                @click="sendSticker(st)"
              >
                <img :src="stickerUrl(st)" :alt="st.label" loading="lazy" />
              </button>
            </div>
          </form>
        </section>

        <!-- 侧栏:在线 + 表情 + 提示 -->
        <aside class="chat-side">
          <section class="chat-side__card platform-panel ink-panel">
            <header class="chat-side__head">
              <h3>在线 · <strong>{{ onlineCount }}</strong></h3>
            </header>
            <ul class="chat-side__users">
              <li v-if="!onlineUsers.length" class="chat-side__empty">当前只有你</li>
              <li
                v-for="u in onlineUsers"
                :key="u.id"
                class="chat-side__user"
                :class="{ 'is-mine': u.id === myUserId }"
              >
                <span class="chat-side__avatar" :style="avatarStyle({ avatar: u.avatar })">
                  {{ (u.nickname || u.username || '?').slice(0, 1) }}
                </span>
                <span class="chat-side__name">{{ u.nickname || u.username }}</span>
                <span v-if="u.id === myUserId" class="chat-side__tag">你</span>
              </li>
            </ul>
          </section>

          <section class="chat-side__card platform-panel ink-panel">
            <header class="chat-side__head">
              <h3>常用表情</h3>
              <span class="chat-side__hint">点击直接发送</span>
            </header>
            <div class="chat-side__stickers">
              <button
                v-for="st in chatStickers"
                :key="st.id"
                type="button"
                class="chat-side__sticker"
                :title="st.label"
                :disabled="!canSend"
                @click="sendSticker(st)"
              >
                <img :src="stickerUrl(st)" :alt="st.label" loading="lazy" />
              </button>
            </div>
          </section>

          <p class="chat-side__note">
            聊天内容会留存 30 天;违规发言会被管理员请出,严重者封号。
          </p>
        </aside>
      </div>
    </PlatformPageShell>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import PlatformPageShell from '../../components/platform/PlatformPageShell.vue'
import {
  fetchStudyRoomMessages,
  fetchStudyRoomOnline,
  fetchProfile,
  getPlatformToken,
  openStudyRoomSocket,
  resolveMediaUrl,
} from '../../api/platform.js'
import { chatStickers, stickerUrl } from '../../data/chatStickers.js'
import { usePageMeta } from '../../composables/usePageMeta'

usePageMeta({ title: '聊天室', description: 'CYINC 平台聊天室 —— 跟全站同学一起聊天、灌水、自习。' })

const messages = ref([])
const draft = ref('')
const onlineCount = ref(0)
const onlineUsers = ref([])
const socketReady = ref(false)
const chatError = ref('')
const myUserId = ref(null)
const myUsername = ref('')
const shake = ref(false)
const emojiOpen = ref(false)
const loadingHistory = ref(false)
const historyExhausted = ref(false)

const listRef = ref(null)
const inputRef = ref(null)

let socket = null
let profileTimer = null
let profileRetry = 0
let onlineTimer = null
let stickToBottom = true
let onlineUsersSeq = 0

const canSend = computed(() => !!getPlatformToken() && socketReady.value)

function avatarStyle(m) {
  const url = m && m.avatar
  const full = url ? resolveMediaUrl(url) : ''
  if (!full) return {}
  return { backgroundImage: `url(${full})`, color: 'transparent' }
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
  if (el.scrollTop < 60 && !loadingHistory.value && !historyExhausted.value && messages.value.length) {
    loadMoreHistory()
  }
}

function pushIncoming(item) {
  if (!item || item.id == null) return
  if (item.is_deleted) return
  if (messages.value.some((m) => m.id === item.id)) return
  messages.value.push(item)
  scrollToBottom()
}

function applyHistory(items) {
  if (!Array.isArray(items)) return
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
  } catch (e) { /* ignore */ }
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
      if (u && (u.id != null)) {
        myUserId.value = u.id
        myUsername.value = u.username || u.nickname || ''
      }
    } catch (e) {
      profileRetry = Math.min(profileRetry + 1, 6)
    }
  }, 300)
}

function flashError(msg, ms = 2500) {
  chatError.value = msg
  shake.value = true
  setTimeout(() => { shake.value = false }, 400)
  if (ms > 0) {
    setTimeout(() => { if (chatError.value === msg) chatError.value = '' }, ms)
  }
}

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
      ensureProfile()
      refreshOnlineUsers()
    },
    onClose: () => { socketReady.value = false },
    onError: () => { socketReady.value = false },
    onMessage: (data) => {
      if (data.type === 'history') {
        messages.value = []
        applyHistory(data.items || [])
      } else if (data.type === 'msg') {
        pushIncoming(data)
      } else if (data.type === 'delete') {
        const id = data.id
        if (id != null) {
          messages.value = messages.value.filter((m) => m.id !== id)
        }
      } else if (data.type === 'restore') {
        pushIncoming(data)
      } else if (data.type === 'kick') {
        const myId = myUserId.value
        if (!myId || data.user_id === myId) {
          flashError(data.reason || '你已被管理员请出聊天室', 0)
          if (socket) { try { socket.close() } catch (e) {} }
        }
      } else if (data.type === 'err') {
        if (data.reason === 'rate') flashError('发言太快,稍等再发')
        else if (data.reason === 'too_long') flashError('消息过长(<=500 字)')
        else flashError('发送失败')
      }
    },
    onPresence: (data) => {
      const c = data && typeof data.count === 'number' ? data.count : null
      if (c != null) onlineCount.value = c
      else refreshOnline()
      // 在线用户列表做轻量轮询 (presence 事件不带列表)
      scheduleOnlineUsers()
    },
  })
}

function scheduleOnlineUsers() {
  if (onlineTimer) return
  const mySeq = ++onlineUsersSeq
  onlineTimer = setTimeout(async () => {
    onlineTimer = null
    if (mySeq !== onlineUsersSeq) return
    await refreshOnlineUsers()
  }, 1500)
}

async function refreshOnlineUsers() {
  // 后端没暴露在线用户列表,这里用最近发言者去重作为近似
  const map = new Map()
  for (const m of messages.value) {
    if (m.user_id != null && m.username) {
      map.set(m.user_id, { id: m.user_id, username: m.username, nickname: m.nickname, avatar: m.avatar })
    }
  }
  if (myUserId.value) {
    const me = { id: myUserId.value, username: myUsername.value, nickname: myUsername.value }
    map.set(myUserId.value, me)
  }
  onlineUsers.value = Array.from(map.values()).slice(0, 20)
}

function onSend() {
  if (!canSend.value) return
  const text = draft.value.trim()
  if (!text) return
  if (text.length > 500) { flashError('消息过长(<=500 字)'); return }
  if (socket && socket.send) {
    const ok = socket.send({ type: 'msg', content: text })
    if (ok !== false) {
      draft.value = ''
      emojiOpen.value = false
    } else {
      flashError('发送失败,稍后再试')
    }
  } else {
    flashError('连接已断开,正在重连…')
  }
}

function sendSticker(st) {
  if (!canSend.value) { flashError('登录后即可发言'); return }
  if (socket && socket.send) {
    const ok = socket.send({ type: 'msg', content: null, sticker_url: stickerUrl(st) })
    if (ok === false) flashError('发送失败')
  }
  emojiOpen.value = false
}

onMounted(() => {
  refreshOnline()
  connectChat()
  setTimeout(() => { if (inputRef.value && canSend.value) inputRef.value.focus() }, 200)
})

onBeforeUnmount(() => {
  if (socket) { try { socket.close() } catch (e) {} socket = null }
  if (profileTimer) { clearTimeout(profileTimer); profileTimer = null }
  if (onlineTimer) { clearTimeout(onlineTimer); onlineTimer = null }
})
</script>

<style scoped>
.chat-room-page { display: block; }

.chat-status {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-family: var(--mono);
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: 0.35rem 0.7rem;
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--bg-paper) 60%, transparent);
}
.chat-status.is-on { color: #1d8a4a; border-color: color-mix(in srgb, #1d8a4a 35%, transparent); }
.chat-status.is-err { color: #c0392b; border-color: color-mix(in srgb, #c0392b 40%, transparent); }
.chat-status__dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--text-muted);
}
.chat-status.is-on .chat-status__dot {
  background: #1d8a4a;
  box-shadow: 0 0 0 0 color-mix(in srgb, #1d8a4a 60%, transparent);
  animation: chat-pulse 2.2s ease-in-out infinite;
}
@keyframes chat-pulse {
  0%, 100% { box-shadow: 0 0 0 0 color-mix(in srgb, #1d8a4a 60%, transparent); }
  50% { box-shadow: 0 0 0 6px color-mix(in srgb, #1d8a4a 0%, transparent); }
}

.chat-room-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 1.25rem;
  align-items: start;
}
@media (max-width: 960px) {
  .chat-room-grid { grid-template-columns: 1fr; }
}

/* 主聊天区 */
.chat-main {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  min-height: 60vh;
  max-height: calc(100vh - 240px);
}
.chat-main__list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.1rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  scroll-behavior: smooth;
}
.chat-main__hint, .chat-main__empty {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 1.25rem 0;
}

.chat-msg {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 0.65rem;
  align-items: flex-start;
}
.chat-msg.is-mine { grid-template-columns: 1fr 36px; }
.chat-msg.is-mine .chat-msg__avatar { order: 2; }
.chat-msg.is-mine .chat-msg__body { order: 1; align-items: flex-end; }
.chat-msg.is-mine .chat-msg__meta { justify-content: flex-end; }
.chat-msg.is-mine .chat-msg__text { background: color-mix(in srgb, var(--orange) 16%, var(--bg-paper)); border-color: color-mix(in srgb, var(--orange) 30%, transparent); }
.chat-msg.is-mine .chat-msg__text::after { display: none; }

.chat-msg__avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--primary-color) 18%, var(--bg-paper));
  color: var(--primary-color);
  display: grid; place-items: center;
  font-weight: 600; font-size: 0.95rem;
  background-size: cover; background-position: center;
  flex-shrink: 0;
}
.chat-msg__body { display: flex; flex-direction: column; min-width: 0; }
.chat-msg__meta {
  display: flex; gap: 0.5rem; align-items: baseline;
  font-size: 0.75rem; color: var(--text-muted);
  margin-bottom: 0.2rem;
}
.chat-msg__name { color: var(--text); font-size: 0.85rem; font-weight: 600; }
.chat-msg__time { font-family: var(--mono); font-size: 0.7rem; }
.chat-msg__text {
  margin: 0;
  display: inline-block;
  max-width: 75%;
  padding: 0.55rem 0.75rem;
  background: var(--bg-paper);
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  border-radius: 12px;
  border-top-left-radius: 4px;
  color: var(--text);
  font-size: 0.9rem;
  line-height: 1.5;
  word-break: break-word;
  position: relative;
}
.chat-msg__sticker {
  max-width: 140px; max-height: 140px;
  border-radius: 8px;
  background: transparent;
}

/* 输入区 */
.chat-input {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 0.85rem;
  border-top: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
  background: color-mix(in srgb, var(--bg-paper) 75%, transparent);
}
.chat-input.is-shake { animation: chat-shake 0.4s; }
@keyframes chat-shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-4px); }
  40%, 80% { transform: translateX(4px); }
}
.chat-input__emoji-btn {
  appearance: none;
  width: 36px; height: 36px;
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  background: var(--bg);
  color: var(--text);
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.chat-input__emoji-btn:hover { border-color: var(--primary-color); color: var(--primary-color); }
.chat-input__field {
  flex: 1; min-width: 0;
  padding: 0.55rem 0.75rem;
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  background: var(--bg);
  color: var(--text);
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
}
.chat-input__field:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary-color) 18%, transparent); }
.chat-input__send {
  appearance: none;
  padding: 0.55rem 1.1rem;
  border: none;
  background: var(--primary-color);
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  flex-shrink: 0;
}
.chat-input__send:disabled { opacity: 0.45; cursor: not-allowed; }
.chat-input__send:hover:not(:disabled) { background: var(--primary-darker, #c44900); }

.chat-input__emoji-panel {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 0.5rem;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 4px;
  padding: 0.5rem;
  background: var(--bg-paper);
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  border-radius: 10px;
  box-shadow: 0 -4px 16px rgba(0,0,0,0.08);
  z-index: 5;
  max-width: 380px;
}
.chat-input__emoji-item {
  appearance: none;
  background: transparent;
  border: 1px solid transparent;
  padding: 0;
  border-radius: 6px;
  cursor: pointer;
  width: 32px; height: 32px;
  display: grid; place-items: center;
}
.chat-input__emoji-item:hover { border-color: var(--primary-color); background: color-mix(in srgb, var(--primary-color) 8%, transparent); }
.chat-input__emoji-item img { width: 100%; height: 100%; object-fit: cover; border-radius: 4px; }
@media (max-width: 600px) {
  .chat-input__emoji-panel { grid-template-columns: repeat(5, 1fr); max-width: 220px; }
}

/* 侧栏 */
.chat-side { display: flex; flex-direction: column; gap: 1rem; }
.chat-side__card { padding: 0.85rem 1rem; }
.chat-side__head { display: flex; align-items: baseline; justify-content: space-between; gap: 0.5rem; margin-bottom: 0.6rem; }
.chat-side__head h3 { margin: 0; font-size: 0.92rem; font-weight: 600; color: var(--text); }
.chat-side__head h3 strong { color: var(--primary-color); font-family: var(--mono); }
.chat-side__hint { font-size: 0.7rem; color: var(--text-muted); }
.chat-side__users { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.3rem; max-height: 240px; overflow-y: auto; }
.chat-side__empty { font-size: 0.78rem; color: var(--text-muted); text-align: center; padding: 0.6rem 0; }
.chat-side__user {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.3rem 0.4rem; border-radius: 6px;
  font-size: 0.82rem;
}
.chat-side__user.is-mine { background: color-mix(in srgb, var(--primary-color) 10%, transparent); }
.chat-side__avatar {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--primary-color) 18%, var(--bg-paper));
  color: var(--primary-color);
  display: grid; place-items: center;
  font-weight: 600; font-size: 0.7rem;
  background-size: cover; background-position: center;
  flex-shrink: 0;
}
.chat-side__name { color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chat-side__tag {
  margin-left: auto;
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  background: var(--primary-color);
  color: #fff;
  border-radius: 999px;
  font-family: var(--mono);
}
.chat-side__stickers {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
}
.chat-side__sticker {
  appearance: none;
  background: var(--bg);
  border: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
  border-radius: 6px;
  padding: 0;
  cursor: pointer;
  aspect-ratio: 1;
  display: grid; place-items: center;
}
.chat-side__sticker:hover:not(:disabled) { border-color: var(--primary-color); transform: translateY(-1px); }
.chat-side__sticker:disabled { opacity: 0.4; cursor: not-allowed; }
.chat-side__sticker img { width: 100%; height: 100%; object-fit: cover; border-radius: 5px; }
.chat-side__note {
  margin: 0;
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.55;
  padding: 0.6rem 0.85rem;
  background: color-mix(in srgb, var(--bg-paper) 60%, transparent);
  border-left: 2px solid color-mix(in srgb, var(--primary-color) 40%, transparent);
  border-radius: 0 6px 6px 0;
}
</style>
<template>
  <div class="study-chat-panel">
    <div class="study-chat-panel__status">
      <span :class="{ live: socketReady }"></span>
      <strong>{{ socketReady ? 'LIVE' : 'OFFLINE' }}</strong>
      <small>{{ onlineCount }} 人在线</small>
      <em v-if="chatError">{{ chatError }}</em>
    </div>

    <div ref="listRef" class="study-chat-panel__list">
      <p v-if="loading" class="study-chat-panel__hint">加载中…</p>
      <p v-else-if="!messages.length" class="study-chat-panel__hint">还没有人发言，来聊一句吧</p>
      <article
        v-for="message in messages"
        :key="message.id"
        class="study-chat-panel__message"
        :class="{ mine: message.user_id === myUserId }"
      >
        <span class="study-chat-panel__avatar" :style="avatarStyle(message)">
          {{ (message.nickname || message.username || '?').slice(0, 1) }}
        </span>
        <div>
          <div class="study-chat-panel__meta">
            <strong>{{ message.nickname || message.username || '匿名' }}</strong>
            <time>{{ formatTime(message.created_at) }}</time>
          </div>
          <img
            v-if="message.message_type === 'sticker' && message.sticker_url"
            :src="messageStickerUrl(message.sticker_url)"
            alt="表情"
            loading="lazy"
          >
          <p v-else>{{ message.content }}</p>
        </div>
      </article>
    </div>

    <form class="study-chat-panel__form" @submit.prevent="sendMessage">
      <input
        v-model="draft"
        type="text"
        maxlength="500"
        :placeholder="canSend ? '说点什么…' : '登录后即可发言'"
        :disabled="!canSend"
        @keydown.enter.exact.prevent="sendMessage"
      >
      <button
        type="button"
        class="study-chat-panel__sticker"
        :aria-expanded="emojiOpen"
        title="表情"
        @click="emojiOpen = !emojiOpen"
      >☺</button>
      <button type="submit" :disabled="!canSend || !draft.trim()">发送</button>
      <div
        v-if="emojiOpen"
        class="study-chat-panel__stickers"
        @pointerenter="emojiOpen = true"
        @pointerdown.stop
        @click.stop
      >
        <button
          v-for="sticker in chatStickers"
          :key="sticker.id"
          type="button"
          :title="sticker.label"
          :disabled="!canSend"
          @pointerdown.stop
          @click="sendSticker(sticker)"
        >
          <img :src="stickerUrl(sticker)" :alt="sticker.label" loading="lazy">
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  fetchProfile,
  fetchStudyRoomMessages,
  fetchStudyRoomOnline,
  getPlatformToken,
  openStudyRoomSocket,
  resolveMediaUrl,
} from '../../api/platform.js'
import { chatStickers, stickerUrl } from '../../data/chatStickers.js'

const messages = ref([])
const draft = ref('')
const onlineCount = ref(0)
const socketReady = ref(false)
const chatError = ref('')
const myUserId = ref(null)
const loading = ref(false)
const emojiOpen = ref(false)
const listRef = ref(null)

let socket = null
let historyRetryTimer = null

const canSend = computed(() => !!getPlatformToken() && socketReady.value)

function avatarStyle(message) {
  const url = message?.avatar ? resolveMediaUrl(message.avatar) : ''
  return url ? { backgroundImage: `url(${url})`, color: 'transparent' } : {}
}

function formatTime(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function messageStickerUrl(url) {
  return url?.startsWith('/myweb/') ? url : resolveMediaUrl(url)
}

function scrollToBottom() {
  nextTick(() => {
    if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
  })
}

function pushMessage(message) {
  if (!message || message.id == null || message.is_deleted) return
  if (messages.value.some(item => item.id === message.id)) return
  messages.value.push(message)
  scrollToBottom()
}

function flashError(text) {
  chatError.value = text
  setTimeout(() => {
    if (chatError.value === text) chatError.value = ''
  }, 2500)
}

async function loadHistory() {
  loading.value = true
  try {
    const response = await fetchStudyRoomMessages({ limit: 50 })
    messages.value = response?.data?.items || []
    chatError.value = ''
    scrollToBottom()
  } catch {
    chatError.value = '聊天服务未连接，自动重试中'
    scheduleHistoryRetry()
  } finally {
    loading.value = false
  }
}

function scheduleHistoryRetry() {
  if (historyRetryTimer) return
  historyRetryTimer = setTimeout(() => {
    historyRetryTimer = null
    void loadHistory()
  }, 5000)
}

async function loadProfile() {
  if (myUserId.value || !getPlatformToken()) return
  try {
    const response = await fetchProfile()
    myUserId.value = response?.data?.id ?? null
  } catch {}
}

async function refreshOnline() {
  try {
    const response = await fetchStudyRoomOnline()
    onlineCount.value = Number(response?.data?.count) || 0
  } catch {}
}

function connectChat() {
  const token = getPlatformToken()
  if (!token) {
    chatError.value = '登录后即可发言'
    return
  }
  socket = openStudyRoomSocket({
    token,
    onOpen: () => {
      socketReady.value = true
      chatError.value = ''
      void loadProfile()
      void refreshOnline()
    },
    onClose: () => { socketReady.value = false },
    onError: () => { socketReady.value = false },
    onMessage: (data) => {
      if (data.type === 'history') {
        messages.value = data.items || []
        scrollToBottom()
      } else if (data.type === 'msg' || data.type === 'restore') {
        pushMessage(data)
      } else if (data.type === 'delete') {
        messages.value = messages.value.filter(item => item.id !== data.id)
      } else if (data.type === 'err') {
        flashError(data.reason === 'rate' ? '发言太快，稍等再发' : '发送失败')
      }
    },
    onPresence: (data) => {
      if (typeof data.count === 'number') onlineCount.value = data.count
    },
  })
}

function sendMessage() {
  if (!canSend.value) return
  const text = draft.value.trim()
  if (!text) return
  if (socket?.send({ type: 'msg', content: text }) !== false) {
    draft.value = ''
    emojiOpen.value = false
  } else {
    flashError('发送失败')
  }
}

function sendSticker(sticker) {
  if (!canSend.value) return
  if (socket?.send({ type: 'msg', content: null, sticker_url: stickerUrl(sticker) }) === false) {
    flashError('发送失败')
  }
  emojiOpen.value = false
}

onMounted(() => {
  void loadHistory()
  void loadProfile()
  void refreshOnline()
  connectChat()
})

onBeforeUnmount(() => {
  socket?.close()
  socket = null
  if (historyRetryTimer) {
    clearTimeout(historyRetryTimer)
    historyRetryTimer = null
  }
})
</script>

<style scoped>
.study-chat-panel {
  --chat-accent: #ffd166;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  min-height: 0;
  height: 100%;
  color: #fff;
}

.study-chat-panel__status {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.65rem 0.8rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.62);
  font-size: 0.68rem;
}

.study-chat-panel__status span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.42);
}

.study-chat-panel__status span.live {
  background: #5ad07a;
  box-shadow: 0 0 10px rgba(90, 208, 122, 0.55);
}

.study-chat-panel__status strong {
  font-family: var(--mono);
  color: #fff;
}

.study-chat-panel__status em {
  margin-left: auto;
  color: #ff8f8f;
  font-style: normal;
}

.study-chat-panel__list {
  display: grid;
  align-content: start;
  gap: 0.7rem;
  height: 260px;
  overflow-y: auto;
  padding: 0.8rem;
}

.study-chat-panel__hint {
  margin: auto;
  color: rgba(255, 255, 255, 0.54);
  font-size: 0.75rem;
}

.study-chat-panel__message {
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr);
  gap: 0.5rem;
}

.study-chat-panel__message.mine {
  grid-template-columns: minmax(0, 1fr) 30px;
}

.study-chat-panel__message.mine .study-chat-panel__avatar {
  order: 2;
}

.study-chat-panel__message.mine > div {
  text-align: right;
}

.study-chat-panel__avatar {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 209, 102, 0.18);
  color: var(--chat-accent);
  background-size: cover;
  background-position: center;
  font-size: 0.8rem;
}

.study-chat-panel__meta {
  display: flex;
  gap: 0.35rem;
  align-items: baseline;
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.62rem;
}

.study-chat-panel__message.mine .study-chat-panel__meta {
  justify-content: flex-end;
}

.study-chat-panel__message p {
  display: inline-block;
  max-width: 100%;
  margin: 0.2rem 0 0;
  padding: 0.45rem 0.6rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  text-align: left;
  word-break: break-word;
  font-size: 0.76rem;
  line-height: 1.45;
}

.study-chat-panel__message.mine p {
  border-color: rgba(255, 209, 102, 0.24);
  background: rgba(255, 209, 102, 0.14);
}

.study-chat-panel__message img {
  display: block;
  width: 72px;
  height: 72px;
  margin-top: 0.25rem;
  object-fit: cover;
  border-radius: 10px;
}

.study-chat-panel__message.mine img {
  margin-left: auto;
}

.study-chat-panel__form {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 0.35rem;
  padding: 0.65rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.study-chat-panel__form input {
  height: 2.2rem;
  min-width: 0;
  padding: 0 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  outline: none;
}

.study-chat-panel__form input:focus {
  border-color: var(--chat-accent);
}

.study-chat-panel__form button {
  height: 2.2rem;
  padding: 0 0.65rem;
  border: 0;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  cursor: pointer;
}

.study-chat-panel__form button[type='submit'] {
  background: var(--chat-accent);
  color: #171207;
}

.study-chat-panel__form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.study-chat-panel__stickers {
  position: absolute;
  right: 0;
  bottom: calc(100% - 0.3rem);
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.35rem;
  width: 184px;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  background: rgba(15, 18, 24, 0.96);
  box-shadow: 0 -14px 34px rgba(0, 0, 0, 0.32);
  pointer-events: auto;
  z-index: 20;
}

.study-chat-panel__stickers button {
  height: auto;
  padding: 0.25rem;
  background: rgba(255, 255, 255, 0.05);
}

.study-chat-panel__stickers img {
  width: 100%;
  height: 34px;
  object-fit: cover;
}
</style>

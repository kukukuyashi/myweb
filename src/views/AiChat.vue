<template>
  <div class="ai-page">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content ai-shell">
          <header class="ai-header">
            <p class="ai-coord">AI · DIFY · CHATFLOW</p>
            <h1 class="page-title">站内 AI 助手</h1>
            <p class="ai-desc">基于自建 Dify 知识库，可询问本站博客与技术笔记相关问题。</p>
            <p v-if="statusText" class="ai-status" :class="{ warn: !chatReady }">{{ statusText }}</p>
          </header>

          <section v-if="!token" class="ai-login card">
            <h2>登录后使用</h2>
            <form @submit.prevent="handleLogin">
              <label>
                用户名
                <input v-model="loginForm.username" required autocomplete="username" />
              </label>
              <label>
                密码
                <input v-model="loginForm.password" type="password" required autocomplete="current-password" />
              </label>
              <p v-if="error" class="error">{{ error }}</p>
              <button type="submit" class="btn-primary" :disabled="loading">登录</button>
            </form>
          </section>

          <section v-else class="ai-chat card">
            <div class="chat-log" ref="logRef">
              <div v-for="(msg, i) in messages" :key="i" class="chat-row" :class="msg.role">
                <span class="role">{{ msg.role === 'user' ? '你' : 'CYINC AI' }}</span>
                <div class="bubble">{{ msg.text }}</div>
              </div>
              <p v-if="!messages.length" class="chat-empty">输入问题开始对话，例如：「这个博客用了哪些技术栈？」</p>
            </div>
            <form class="chat-input" @submit.prevent="handleSend">
              <textarea
                v-model="input"
                rows="2"
                placeholder="输入问题…"
                :disabled="loading || !chatReady"
              />
              <div class="chat-actions">
                <button type="button" class="btn-ghost" @click="logout">退出</button>
                <button type="submit" class="btn-primary" :disabled="loading || !input.trim() || !chatReady">
                  {{ loading ? '思考中…' : '发送' }}
                </button>
              </div>
            </form>
            <p v-if="error" class="error">{{ error }}</p>
          </section>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { usePageMeta } from '../composables/usePageMeta'
import {
  fetchAiStatus,
  getPlatformToken,
  platformLogin,
  sendAiChat,
  setPlatformToken,
} from '../api/platform.js'

usePageMeta({
  title: 'AI 助手',
  description: 'CYINC 站内 AI 助手，基于 Dify Chatflow 与博客知识库。',
})

const token = ref(getPlatformToken())
const loginForm = ref({ username: '', password: '' })
const messages = ref([])
const input = ref('')
const loading = ref(false)
const error = ref('')
const chatReady = ref(false)
const statusText = ref('正在检测 Dify 配置…')
const conversationId = ref(null)
const logRef = ref(null)

async function scrollToBottom() {
  await nextTick()
  if (logRef.value) logRef.value.scrollTop = logRef.value.scrollHeight
}

async function loadStatus() {
  try {
    const json = await fetchAiStatus()
    chatReady.value = !!json.data.chat_ready
    statusText.value = chatReady.value
      ? 'Dify Chatflow 已就绪'
      : 'Dify 未配置：请在 backend/.env 填写 DIFY_API_URL 与 DIFY_CHAT_API_KEY，并完成 deploy/README-dify.md 部署'
  } catch {
    chatReady.value = false
    statusText.value = '无法连接后端 API，请确认 FastAPI 已启动（127.0.0.1:8000）'
  }
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await platformLogin(loginForm.value.username, loginForm.value.password)
    token.value = getPlatformToken()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function logout() {
  setPlatformToken('')
  token.value = ''
  messages.value = []
  conversationId.value = null
}

async function handleSend() {
  const q = input.value.trim()
  if (!q || loading.value) return
  error.value = ''
  messages.value.push({ role: 'user', text: q })
  input.value = ''
  loading.value = true
  await scrollToBottom()
  try {
    const json = await sendAiChat(q, conversationId.value)
    if (json.data.conversation_id) conversationId.value = json.data.conversation_id
    messages.value.push({ role: 'assistant', text: json.data.answer })
  } catch (e) {
    error.value = e.message
    messages.value.push({ role: 'assistant', text: `暂时无法回答：${e.message}` })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

onMounted(loadStatus)
</script>

<style scoped>
.ai-shell { max-width: 720px; }

.ai-coord {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  letter-spacing: 0.12em;
  margin-bottom: 0.5rem;
}

.ai-desc {
  color: var(--text-muted);
  margin-top: 0.5rem;
}

.ai-status {
  font-family: var(--mono);
  font-size: 0.78rem;
  margin-top: 1rem;
  color: #2d6a4f;
}

.ai-status.warn { color: #b45309; }

.card {
  margin-top: 1.5rem;
  border: 1px solid var(--border);
  background: var(--card-bg, #fff);
  padding: 1.25rem;
}

.ai-login form {
  display: grid;
  gap: 0.75rem;
}

.ai-login label {
  display: grid;
  gap: 0.35rem;
  font-family: var(--mono);
  font-size: 0.78rem;
}

.ai-login input {
  border: 1px solid var(--border);
  padding: 0.55rem 0.65rem;
  font: inherit;
  background: var(--bg);
}

.chat-log {
  max-height: 420px;
  overflow-y: auto;
  display: grid;
  gap: 0.85rem;
  margin-bottom: 1rem;
  padding-right: 0.25rem;
}

.chat-row.user .bubble { background: rgba(232, 93, 4, 0.12); }
.chat-row.assistant .bubble { background: var(--bg); }

.role {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  display: block;
  margin-bottom: 0.25rem;
}

.bubble {
  border: 1px solid var(--border);
  padding: 0.65rem 0.75rem;
  line-height: 1.55;
  white-space: pre-wrap;
}

.chat-empty {
  color: var(--text-muted);
  font-size: 0.88rem;
}

.chat-input textarea {
  width: 100%;
  border: 1px solid var(--border);
  padding: 0.65rem;
  font: inherit;
  resize: vertical;
  background: var(--bg);
}

.chat-actions {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.btn-primary,
.btn-ghost {
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

.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-ghost { background: transparent; }

.error {
  color: #c0392b;
  font-size: 0.82rem;
  margin-top: 0.5rem;
}
</style>

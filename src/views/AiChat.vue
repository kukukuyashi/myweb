<template>
  <PlatformPageShell
    coord="AI · DIFY · CHATFLOW"
    title="站内 AI 助手"
    lead="基于自建 Dify 知识库，可询问本站博客与技术笔记相关问题。"
  >
    <template #actions>
      <p v-if="statusText" class="ai-status-pill" :class="chatReady ? 'ok' : 'warn'">{{ statusText }}</p>
    </template>

    <section v-if="!token" class="platform-panel ai-guest">
      <h2>登录后使用 AI 助手</h2>
      <p class="ai-guest-hint">请先登录或注册主站账号，会话将绑定你的 CYINC 身份。</p>
      <div class="ai-guest-actions">
        <router-link to="/app/login?redirect=/app/forum" class="platform-btn-primary">登录</router-link>
        <router-link to="/app/register" class="platform-btn-ghost">注册</router-link>
      </div>
    </section>

    <section v-else class="platform-panel ai-terminal">
      <div class="ai-terminal__log" ref="logRef">
        <div v-for="(msg, i) in messages" :key="i" class="ai-terminal__row" :class="msg.role">
          <span class="ai-terminal__role">{{ msg.role === 'user' ? 'YOU' : 'CYINC' }}</span>
          <div class="ai-terminal__bubble">{{ msg.text }}</div>
        </div>
        <p v-if="!messages.length" class="chat-empty">输入问题开始对话，例如：「这个博客用了哪些技术栈？」</p>
      </div>
      <form class="ai-terminal__composer" @submit.prevent="handleSend">
        <textarea
          v-model="input"
          rows="3"
          placeholder="输入问题…"
          :disabled="loading || !chatReady"
        />
        <div class="ai-terminal__composer-actions">
          <button type="button" class="platform-btn-ghost" @click="logout">退出</button>
          <button type="submit" class="platform-btn-primary" :disabled="loading || !input.trim() || !chatReady">
            {{ loading ? '思考中…' : '发送' }}
          </button>
        </div>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </PlatformPageShell>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import PlatformPageShell from '../components/platform/PlatformPageShell.vue'
import { usePageMeta } from '../composables/usePageMeta'
import {
  fetchAiStatus,
  getPlatformToken,
  sendAiChat,
  setPlatformToken,
} from '../api/platform.js'

usePageMeta({
  title: 'AI 助手',
  description: 'CYINC 站内 AI 助手，基于 Dify Chatflow 与博客知识库。',
})

const token = ref(getPlatformToken())
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
      ? '● Dify 已就绪'
      : '● Dify 未配置'
  } catch {
    chatReady.value = false
    statusText.value = '● API 未连接'
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
.ai-status-pill {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text-muted);
}

.ai-status-pill.ok {
  border-color: color-mix(in srgb, #2d6a4f 40%, var(--border));
  color: #2d6a4f;
}

.ai-status-pill.warn {
  border-color: color-mix(in srgb, #b45309 40%, var(--border));
  color: #b45309;
}

.ai-guest h2 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
}

.ai-guest-hint {
  margin: 0 0 1rem;
  color: var(--text-muted);
  line-height: 1.55;
}

.ai-guest-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.ai-terminal__log {
  max-height: min(52vh, 480px);
  overflow-y: auto;
  display: grid;
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.ai-terminal__row {
  display: grid;
  grid-template-columns: 4rem 1fr;
  gap: 0.65rem;
  align-items: start;
}

.ai-terminal__role {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.08em;
  color: var(--orange);
  padding-top: 0.55rem;
}

.ai-terminal__bubble {
  border: 1px solid var(--border);
  background: var(--bg);
  padding: 0.75rem 0.9rem;
  line-height: 1.58;
  white-space: pre-wrap;
}

.ai-terminal__row.user .ai-terminal__bubble {
  background: var(--orange-light);
  border-color: color-mix(in srgb, var(--orange) 30%, var(--border));
}

.ai-terminal__composer {
  display: grid;
  gap: 0.65rem;
  padding-top: 0.85rem;
  border-top: 1px dashed var(--border);
}

.ai-terminal__composer textarea {
  width: 100%;
  border: 1px solid var(--border);
  background: var(--bg);
  color: inherit;
  font: inherit;
  padding: 0.75rem 0.9rem;
  resize: vertical;
}

.ai-terminal__composer-actions {
  display: flex;
  justify-content: space-between;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.chat-empty {
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 0.82rem;
  margin: 0;
}

.error {
  color: #c0392b;
  font-size: 0.82rem;
  margin: 0.65rem 0 0;
}

@media (max-width: 640px) {
  .ai-terminal__row {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }
}
</style>

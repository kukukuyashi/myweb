<template>
  <div class="container layout-single">
    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else-if="thread">
      <PlatformSubPageHeader coord="FORUM · THREAD">
        <router-link :to="`/app/forum/c/${thread.category_slug}`" class="back">
          ← {{ thread.category_name }}
        </router-link>
        <h1 class="page-title">{{ thread.title }}</h1>
        <p class="meta">
          {{ thread.author?.nickname || thread.author?.username }} ·
          {{ formatDate(thread.created_at) }} · {{ thread.view_count }} 浏览
        </p>
        <router-link
          v-if="canEdit"
          :to="`/app/forum/t/${thread.id}/edit`"
          class="edit-link"
        >
          编辑帖子
        </router-link>
      </PlatformSubPageHeader>

      <article class="platform-panel ink-panel post-body">
        <MarkdownBody :content="thread.content" />
      </article>

      <section class="replies">
        <h2>{{ thread.replies.length }} 条回复</h2>
        <div v-for="r in thread.replies" :key="r.id" class="platform-panel ink-panel reply">
          <p class="reply-meta">
            {{ r.author?.nickname || r.author?.username }} · {{ formatDate(r.created_at) }}
          </p>
          <div class="reply-body">
            <MarkdownBody :content="r.content" />
          </div>
        </div>
      </section>

      <section v-if="!thread.is_locked" class="platform-panel ink-panel reply-form">
        <h2>回复</h2>
        <p v-if="!token" class="warn">
          请先 <router-link to="/app/me">登录</router-link> 后回复。
        </p>
        <form v-else @submit.prevent="submitReply">
          <textarea v-model="replyText" rows="4" required maxlength="10000" placeholder="写下你的回复…" />
          <p v-if="replyError" class="error">{{ replyError }}</p>
          <button type="submit" class="btn-primary" :disabled="replyLoading">发送</button>
        </form>
      </section>
      <p v-else class="warn">该帖已锁定，无法回复。</p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import PlatformSubPageHeader from '../../components/platform/PlatformSubPageHeader.vue'
import { usePageMeta } from '../../composables/usePageMeta'
import MarkdownBody from '../../components/MarkdownBody.vue'
import {
  createForumReply,
  fetchForumThread,
  fetchProfile,
  getPlatformToken,
} from '../../api/platform.js'

const props = defineProps({ id: { type: [String, Number], required: true } })

const thread = ref(null)
const profile = ref(null)
const loading = ref(true)
const error = ref('')
const token = ref(getPlatformToken())
const replyText = ref('')
const replyLoading = ref(false)
const replyError = ref('')

const canEdit = computed(() => {
  if (!thread.value?.author || !profile.value) return false
  return thread.value.author.id === profile.value.id
})

usePageMeta(() => ({
  title: thread.value?.title || '帖子',
  description: '论坛帖子详情。',
}))

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const json = await fetchForumThread(props.id)
    thread.value = json.data
    if (token.value) {
      try {
        const me = await fetchProfile()
        profile.value = me.data
      } catch {
        profile.value = null
      }
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function submitReply() {
  replyError.value = ''
  replyLoading.value = true
  try {
    await createForumReply(props.id, replyText.value.trim())
    replyText.value = ''
    await load()
  } catch (e) {
    replyError.value = e.message
  } finally {
    replyLoading.value = false
  }
}

watch(() => props.id, load)
onMounted(load)
</script>

<style scoped>
.back {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--orange);
  text-decoration: none;
}

.meta {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
}

.edit-link {
  display: inline-block;
  margin-top: 0.5rem;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  text-decoration: none;
}

.card {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  padding: 1rem 1.25rem;
  margin-top: 1rem;
}

.post-body, .reply-body {
  font-size: 0.92rem;
}

.replies h2, .reply-form h2 {
  font-size: 0.95rem;
  margin: 1.25rem 0 0.5rem;
}

.reply-meta {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  margin: 0 0 0.5rem;
}

textarea {
  width: 100%;
  border: 1px solid var(--border);
  padding: 0.65rem;
  font: inherit;
  background: var(--bg);
  resize: vertical;
}

.btn-primary {
  margin-top: 0.5rem;
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.45rem 0.9rem;
  background: var(--orange);
  border: 1px solid var(--orange);
  color: #fff;
  cursor: pointer;
}

.btn-primary:disabled { opacity: 0.55; }

.warn { color: #b45309; font-size: 0.85rem; }
.warn a { color: var(--orange); }
.muted { color: var(--text-muted); }
.error { color: #c0392b; font-size: 0.85rem; }
</style>

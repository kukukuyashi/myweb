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
        <div class="thread-author-row">
          <img
            v-if="authorAvatarUrl"
            :src="authorAvatarUrl"
            alt=""
            class="thread-author-avatar"
          >
          <p class="meta">
            {{ thread.author?.nickname || thread.author?.username }}
            <LevelBadge
              v-if="thread.author?.level >= 2"
              :level="thread.author?.level"
              :level-title="thread.author?.level_title"
            />
            <span v-if="thread.author?.level >= 4" class="master-tag">达人</span>
            · {{ formatDate(thread.created_at) }} · {{ thread.view_count }} 浏览
          </p>
        </div>
        <router-link
          v-if="canEdit"
          :to="`/app/forum/t/${thread.id}/edit`"
          class="edit-link"
        >
          编辑帖子
        </router-link>
      </PlatformSubPageHeader>

      <figure v-if="thread.cover_url" class="platform-panel ink-panel thread-cover">
        <img :src="coverUrl" :alt="thread.title">
      </figure>

      <article class="platform-panel ink-panel post-body">
        <MarkdownBody :content="thread.content" />
      </article>

      <div class="thread-actions platform-panel ink-panel">
        <button
          type="button"
          class="action-btn"
          :class="{ active: thread.liked_by_me }"
          :disabled="!token || actionBusy"
          @click="toggleThreadLike"
        >
          {{ thread.liked_by_me ? '♥' : '♡' }} {{ thread.like_count || 0 }}
        </button>
        <button
          type="button"
          class="action-btn"
          :disabled="!token || actionBusy"
          @click="shareThread"
        >
          ↗ 分享 {{ thread.share_count || 0 }}
        </button>
        <p v-if="!token" class="action-hint">
          <router-link to="/app/login">登录</router-link> 后可点赞、分享并获得经验值
        </p>
        <p v-if="actionToast" class="action-toast">{{ actionToast }}</p>
      </div>

      <section class="replies">
        <h2>{{ thread.replies.length }} 条回复</h2>
        <div v-for="r in thread.replies" :key="r.id" class="platform-panel ink-panel reply">
          <p class="reply-meta">
            {{ r.author?.nickname || r.author?.username }}
            <LevelBadge
              v-if="r.author?.level >= 2"
              :level="r.author?.level"
              :level-title="r.author?.level_title"
            />
            · {{ formatDate(r.created_at) }}
            <button
              v-if="token"
              type="button"
              class="reply-like-btn"
              :class="{ active: r.liked_by_me }"
              :disabled="actionBusy"
              @click="toggleReplyLike(r)"
            >
              {{ r.liked_by_me ? '♥' : '♡' }} {{ r.like_count || 0 }}
            </button>
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
import LevelBadge from '../../components/LevelBadge.vue'
import {
  createForumReply,
  fetchForumThread,
  fetchProfile,
  getPlatformToken,
  likeForumReply,
  likeForumThread,
  resolveMediaUrl,
  resolvePublicUrl,
  shareForumThread,
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
const actionBusy = ref(false)
const actionToast = ref('')

const canEdit = computed(() => {
  if (!thread.value?.author || !profile.value) return false
  return thread.value.author.id === profile.value.id
})

const coverUrl = computed(() => resolveMediaUrl(thread.value?.cover_url))
const authorAvatarUrl = computed(() => resolvePublicUrl(thread.value?.author?.avatar || ''))

usePageMeta(() => ({
  title: thread.value?.title || '帖子',
  description: '论坛帖子详情。',
  image: coverUrl.value || undefined,
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

function showActionToast(msg) {
  actionToast.value = msg || ''
  if (msg) setTimeout(() => { actionToast.value = '' }, 3500)
}

async function toggleThreadLike() {
  if (!token.value || actionBusy.value || !thread.value) return
  actionBusy.value = true
  try {
    const json = await likeForumThread(thread.value.id)
    thread.value.liked_by_me = true
    thread.value.like_count = json.data?.like_count ?? thread.value.like_count
    showActionToast(json.message)
  } catch (e) {
    showActionToast(e.message)
  } finally {
    actionBusy.value = false
  }
}

async function toggleReplyLike(reply) {
  if (!token.value || actionBusy.value) return
  actionBusy.value = true
  try {
    const json = await likeForumReply(reply.id)
    reply.liked_by_me = true
    reply.like_count = json.data?.like_count ?? reply.like_count
    showActionToast(json.message)
  } catch (e) {
    showActionToast(e.message)
  } finally {
    actionBusy.value = false
  }
}

async function shareThread() {
  if (!token.value || actionBusy.value || !thread.value) return
  actionBusy.value = true
  try {
    const url = window.location.href
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(url)
    }
    const json = await shareForumThread(thread.value.id)
    thread.value.share_count = json.data?.share_count ?? thread.value.share_count
    showActionToast(json.message || '链接已复制')
  } catch (e) {
    showActionToast(e.message)
  } finally {
    actionBusy.value = false
  }
}

async function submitReply() {
  replyError.value = ''
  replyLoading.value = true
  try {
    const json = await createForumReply(props.id, replyText.value.trim())
    replyText.value = ''
    showActionToast(json.message)
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

.thread-author-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.35rem;
}

.thread-author-row .meta {
  margin-top: 0;
}

.thread-author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--border);
  flex-shrink: 0;
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

.post-cover img,
.thread-cover img {
  display: block;
  width: 100%;
  max-height: 360px;
  object-fit: cover;
  aspect-ratio: 16 / 9;
}

.post-cover,
.thread-cover {
  margin-top: 0.75rem;
  padding: 0;
  overflow: hidden;
}

.thread-actions {
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
}

.action-btn {
  font-family: var(--mono);
  font-size: 0.75rem;
  padding: 0.35rem 0.7rem;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
}

.action-btn.active {
  border-color: var(--orange);
  color: var(--orange);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.action-hint a {
  color: var(--orange);
}

.action-toast {
  margin: 0;
  width: 100%;
  font-size: 0.78rem;
  color: #2d6a4f;
}

[data-theme="dark"] .action-toast {
  color: #95d5b2;
}

.reply-like-btn {
  margin-left: auto;
  font-family: var(--mono);
  font-size: 0.62rem;
  padding: 0.15rem 0.4rem;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.reply-like-btn.active {
  color: var(--orange);
  border-color: rgba(232, 93, 4, 0.45);
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
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
}

.master-tag {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--orange);
  border: 1px solid rgba(232, 93, 4, 0.4);
  padding: 0.1rem 0.35rem;
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

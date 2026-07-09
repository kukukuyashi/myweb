<template>
  <div class="container layout-single me-layout">
    <header class="me-header">
      <p class="coord">ACCOUNT · ME</p>
      <h1 class="page-title">个人中心</h1>
    </header>

    <section v-if="!token" class="card me-login">
      <h2>登录主站账号</h2>
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

    <div v-else class="me-grid">
      <aside class="user-card card">
        <div class="avatar-wrap">
          <img v-if="avatarDisplayUrl" :src="avatarDisplayUrl" alt="" class="avatar" />
          <span v-else class="avatar placeholder">{{ avatarInitial }}</span>
        </div>
        <h2>{{ profile?.nickname || profile?.username }}</h2>
        <p class="username">@{{ profile?.username }}</p>
        <p class="email">{{ profile?.email }}</p>
        <button type="button" class="btn-ghost" @click="logout">退出登录</button>
      </aside>

      <section class="me-main">
        <nav class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </nav>

        <div v-show="activeTab === 'profile'" class="card tab-panel">
          <form @submit.prevent="saveProfile">
            <div class="avatar-field">
              <div class="avatar-preview">
                <img v-if="avatarPreviewUrl" :src="avatarPreviewUrl" alt="" class="avatar-lg" />
                <span v-else class="avatar-lg placeholder">{{ avatarInitial }}</span>
              </div>
              <div class="avatar-actions">
                <input
                  ref="avatarInputRef"
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  class="hidden-file"
                  @change="onAvatarPick"
                />
                <button type="button" class="btn-ghost sm" :disabled="avatarUploading" @click="pickAvatar">
                  {{ avatarUploading ? '上传中…' : '上传头像' }}
                </button>
                <p class="hint">JPG / PNG / WebP / GIF，最大 2MB</p>
              </div>
            </div>
            <label>
              昵称
              <input v-model="editForm.nickname" required maxlength="100" />
            </label>
            <label>
              头像 URL（可选，上传后自动填入）
              <input v-model="editForm.avatar" type="text" placeholder="/uploads/avatars/... 或 https://..." />
            </label>
            <p v-if="profileMsg" class="success">{{ profileMsg }}</p>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit" class="btn-primary" :disabled="loading">保存资料</button>
          </form>
        </div>

        <div v-show="activeTab === 'posts'" class="card tab-panel">
          <div class="panel-head">
            <router-link to="/app/posts/new" class="btn-primary">写文章</router-link>
          </div>
          <p v-if="postsLoading" class="muted">加载中…</p>
          <p v-else-if="!posts.length" class="muted">暂无文章，点上方写第一篇吧。</p>
          <ul v-else class="item-list">
            <li v-for="post in posts" :key="post.id">
              <div class="item-main">
                <router-link :to="`/app/posts/${post.id}`">{{ post.title }}</router-link>
                <span class="badge">{{ statusLabel(post.status) }}</span>
              </div>
              <span class="date">{{ formatDate(post.created_at) }}</span>
              <div class="item-actions">
                <router-link :to="`/app/posts/${post.id}/edit`" class="act">编辑</router-link>
                <button type="button" class="act danger" @click="removePost(post)">删除</button>
              </div>
            </li>
          </ul>
        </div>

        <div v-show="activeTab === 'threads'" class="card tab-panel">
          <div class="panel-head">
            <router-link to="/app/forum/new" class="btn-primary">发帖</router-link>
          </div>
          <p v-if="threadsLoading" class="muted">加载中…</p>
          <p v-else-if="!forumThreads.length" class="muted">暂无帖子，去论坛发一条吧。</p>
          <ul v-else class="item-list">
            <li v-for="t in forumThreads" :key="t.id">
              <div class="item-main">
                <router-link :to="`/app/forum/t/${t.id}`">{{ t.title }}</router-link>
                <span class="badge">{{ t.category_name }}</span>
              </div>
              <span class="date">{{ formatDate(t.created_at) }}</span>
              <div class="item-actions">
                <router-link :to="`/app/forum/t/${t.id}/edit`" class="act">编辑</router-link>
                <button type="button" class="act danger" @click="removeThread(t)">删除</button>
              </div>
            </li>
          </ul>
        </div>

        <div v-show="activeTab === 'timeline'" class="tab-panel">
          <p v-if="timelineLoading" class="muted">加载中…</p>
          <p v-else-if="!timelineDays.length" class="muted">暂无专注记录，去番茄钟开始第一段吧。</p>
          <div v-else class="timeline">
            <section v-for="day in timelineDays" :key="day.date" class="card day-block">
              <h3>{{ day.date }} · {{ day.total_minutes }} 分钟</h3>
              <ul>
                <li v-for="s in day.sessions" :key="s.id">
                  <span class="mins">{{ Math.round(s.duration_sec / 60) }} 分钟</span>
                  <span class="task">{{ s.task_label || '专注' }}</span>
                  <p v-if="s.reflection" class="reflection">{{ s.reflection }}</p>
                  <span class="date">{{ formatTime(s.completed_at) }}</span>
                </li>
              </ul>
            </section>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePageMeta } from '../composables/usePageMeta'
import {
  deleteForumThread,
  deletePost,
  fetchMyForumThreads,
  fetchMyPosts,
  fetchPomodoroTimeline,
  fetchProfile,
  getPlatformToken,
  platformLogin,
  resolveMediaUrl,
  setPlatformToken,
  updateProfile,
  uploadAvatar,
} from '../api/platform.js'

usePageMeta({
  title: '个人中心',
  description: 'CYINC 主站个人中心：资料、文章、帖子与专注时间线。',
})

const tabs = [
  { id: 'profile', label: '资料' },
  { id: 'posts', label: '我的文章' },
  { id: 'threads', label: '我的帖子' },
  { id: 'timeline', label: '专注时间线' },
]

const route = useRoute()
const token = ref(getPlatformToken())
const activeTab = ref(route.query.tab === 'threads' ? 'threads' : route.query.tab === 'posts' ? 'posts' : 'profile')
const loginForm = ref({ username: '', password: '' })
const profile = ref(null)
const editForm = ref({ nickname: '', avatar: '' })
const posts = ref([])
const forumThreads = ref([])
const timelineDays = ref([])
const loading = ref(false)
const postsLoading = ref(false)
const threadsLoading = ref(false)
const timelineLoading = ref(false)
const error = ref('')
const profileMsg = ref('')
const avatarInputRef = ref(null)
const avatarUploading = ref(false)
const avatarPreviewOverride = ref('')

const avatarDisplayUrl = computed(() => {
  if (avatarPreviewOverride.value) return avatarPreviewOverride.value
  return resolveMediaUrl(profile.value?.avatar)
})

const avatarPreviewUrl = computed(() => {
  if (avatarPreviewOverride.value) return avatarPreviewOverride.value
  if (editForm.value.avatar) return resolveMediaUrl(editForm.value.avatar)
  return resolveMediaUrl(profile.value?.avatar)
})

const avatarInitial = computed(() => {
  const n = profile.value?.nickname || profile.value?.username || '?'
  return n.charAt(0).toUpperCase()
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleTimeString('zh-CN', { hour12: false })
}

function statusLabel(status) {
  return status === 'published' ? '已发布' : '草稿'
}

async function removePost(post) {
  if (!window.confirm(`确定删除「${post.title}」？`)) return
  error.value = ''
  try {
    await deletePost(post.id)
    posts.value = posts.value.filter((p) => p.id !== post.id)
  } catch (e) {
    error.value = e.message
  }
}

async function removeThread(thread) {
  if (!window.confirm(`确定删除「${thread.title}」？回复也会一并删除。`)) return
  error.value = ''
  try {
    await deleteForumThread(thread.id)
    forumThreads.value = forumThreads.value.filter((t) => t.id !== thread.id)
  } catch (e) {
    error.value = e.message
  }
}

async function loadProfile() {
  if (!token.value) return
  error.value = ''
  try {
    const json = await fetchProfile()
    profile.value = json.data
    editForm.value = {
      nickname: json.data.nickname || '',
      avatar: json.data.avatar || '',
    }
  } catch (e) {
    error.value = e.message
    if (e.message.includes('401') || e.message.includes('凭证')) logout()
  }
}

async function loadPosts() {
  if (!token.value) return
  postsLoading.value = true
  try {
    const json = await fetchMyPosts()
    posts.value = json.data.items || []
  } catch (e) {
    error.value = e.message
  } finally {
    postsLoading.value = false
  }
}

async function loadThreads() {
  if (!token.value) return
  threadsLoading.value = true
  try {
    const json = await fetchMyForumThreads()
    forumThreads.value = json.data.items || []
  } catch (e) {
    error.value = e.message
  } finally {
    threadsLoading.value = false
  }
}

async function loadTimeline() {
  if (!token.value) return
  timelineLoading.value = true
  try {
    const json = await fetchPomodoroTimeline(14)
    timelineDays.value = json.data.days || []
  } catch (e) {
    error.value = e.message
  } finally {
    timelineLoading.value = false
  }
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await platformLogin(loginForm.value.username, loginForm.value.password)
    token.value = getPlatformToken()
    await loadAll()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  error.value = ''
  profileMsg.value = ''
  loading.value = true
  try {
    const json = await updateProfile({
      nickname: editForm.value.nickname,
      avatar: editForm.value.avatar?.trim() || null,
    })
    profile.value = json.data
    avatarPreviewOverride.value = ''
    profileMsg.value = '资料已更新'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function pickAvatar() {
  avatarInputRef.value?.click()
}

async function onAvatarPick(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    error.value = '头像不能超过 2MB'
    return
  }
  avatarUploading.value = true
  error.value = ''
  profileMsg.value = ''
  avatarPreviewOverride.value = URL.createObjectURL(file)
  try {
    const json = await uploadAvatar(file)
    profile.value = json.data
    editForm.value.avatar = json.data.avatar || ''
    profileMsg.value = '头像已更新'
  } catch (err) {
    avatarPreviewOverride.value = ''
    error.value = err.message
  } finally {
    avatarUploading.value = false
  }
}

function logout() {
  setPlatformToken('')
  token.value = ''
  profile.value = null
  avatarPreviewOverride.value = ''
  posts.value = []
  forumThreads.value = []
  timelineDays.value = []
}

async function loadAll() {
  await loadProfile()
  await Promise.all([loadPosts(), loadThreads(), loadTimeline()])
}

watch(() => route.query.tab, (tab) => {
  if (tab === 'posts' || tab === 'threads' || tab === 'timeline' || tab === 'profile') {
    activeTab.value = tab
  }
})

watch(activeTab, (tab) => {
  if (!token.value) return
  if (tab === 'posts') loadPosts()
  if (tab === 'threads') loadThreads()
  if (tab === 'timeline') loadTimeline()
})

watch(token, (t) => { if (t) loadAll() })

onMounted(() => { if (token.value) loadAll() })
</script>

<style scoped>
.coord {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  letter-spacing: 0.12em;
}

.card {
  border: 1px solid var(--border);
  background: var(--card-bg, #fff);
  padding: 1.25rem;
}

.me-grid {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 1.25rem;
  margin-top: 1.25rem;
}

.user-card {
  text-align: center;
  height: fit-content;
}

.avatar-wrap { margin-bottom: 0.75rem; }

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
}

.avatar.placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--orange);
  color: #fff;
  font-family: var(--mono);
  font-size: 1.5rem;
}

.user-card h2 { font-size: 1rem; margin: 0; }
.username, .email {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin: 0.25rem 0;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

.tabs button {
  font-family: var(--mono);
  font-size: 0.75rem;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--border);
  background: transparent;
  cursor: pointer;
}

.tabs button.active {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

form { display: grid; gap: 0.75rem; }

label {
  display: grid;
  gap: 0.35rem;
  font-family: var(--mono);
  font-size: 0.78rem;
}

input {
  border: 1px solid var(--border);
  padding: 0.55rem 0.65rem;
  font: inherit;
  background: var(--bg);
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.65rem;
}

.item-list li {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.5rem 1rem;
  align-items: center;
  font-size: 0.88rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.65rem;
}

.item-main {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem 0.65rem;
  min-width: 0;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.act {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--orange);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: none;
}

.act.danger { color: #c0392b; }

.panel-head {
  margin-bottom: 0.85rem;
}

.panel-head .btn-primary {
  display: inline-block;
  text-decoration: none;
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.45rem 0.9rem;
  background: var(--orange);
  border: 1px solid var(--orange);
  color: #fff;
}

.item-list a {
  color: inherit;
  text-decoration: none;
  font-weight: 500;
}

.item-list a:hover { color: var(--orange); }

.badge {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
}

.date {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}

.timeline { display: grid; gap: 0.75rem; }

.day-block h3 {
  font-size: 0.88rem;
  margin: 0 0 0.65rem;
  font-family: var(--mono);
}

.day-block ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.65rem;
}

.day-block li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.35rem 0.75rem;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.5rem;
}

.reflection {
  grid-column: 1 / -1;
  margin: 0;
  font-size: 0.82rem;
  color: var(--text-muted);
  white-space: pre-wrap;
}

.mins { font-family: var(--mono); color: var(--orange); }
.task { font-weight: 500; }

.btn-primary, .btn-ghost {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border: 1px solid var(--border);
  width: fit-content;
}

.btn-primary {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.btn-primary:disabled { opacity: 0.55; }
.btn-ghost { background: transparent; margin-top: 0.75rem; }

.error { color: #c0392b; font-size: 0.82rem; }
.success { color: #2d6a4f; font-size: 0.82rem; }
.muted { color: var(--text-muted); font-size: 0.88rem; }

.avatar-field {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.5rem;
}

.avatar-lg {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
}

.avatar-lg.placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--orange);
  color: #fff;
  font-family: var(--mono);
  font-size: 1.75rem;
}

.avatar-actions {
  display: grid;
  gap: 0.35rem;
}

.hidden-file {
  display: none;
}

.btn-ghost.sm {
  margin-top: 0;
  padding: 0.4rem 0.75rem;
  font-size: 0.72rem;
}

.hint {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}

@media (max-width: 720px) {
  .me-grid { grid-template-columns: 1fr; }
}
</style>

<template>
  <PlatformPageShell
    coord="ACCOUNT · ME"
    title="个人中心"
    :lead="token ? '资料、文章、论坛帖与专注时间线 — 你的主站控制台。' : '登录后管理头像、Markdown 文章、论坛帖与番茄钟记录。'"
    :ink-image="PLATFORM_ME_INK_IMAGE"
    :ink-position="PLATFORM_ME_INK_POSITION"
    :ink-r-end="114"
  >
    <section v-if="!token" class="platform-panel ink-panel me-guest">
      <p class="platform-coord">GUEST · READ ONLY</p>
      <h2 class="me-guest-title">尚未登录</h2>
      <p class="muted">登录后可编辑资料、发布文章、管理论坛帖，并查看专注时间线。</p>
      <div class="me-auth-actions">
        <router-link to="/app/login?redirect=/app/me" class="platform-btn-primary">登录</router-link>
        <router-link to="/app/register" class="platform-btn-ghost">注册新账号</router-link>
      </div>
    </section>

    <div v-else class="me-grid">
      <aside class="user-card platform-panel ink-panel">
        <AvatarFrame :level="profile?.level || 1">
          <div class="avatar-wrap">
            <img v-if="avatarDisplayUrl" :src="avatarDisplayUrl" alt="" class="avatar" />
            <span v-else class="avatar placeholder">{{ avatarInitial }}</span>
          </div>
        </AvatarFrame>
        <h2>{{ profile?.nickname || profile?.username }}</h2>
        <p class="username">@{{ profile?.username }}</p>
        <LevelBadge v-if="(profile?.level || 1) >= 2" :level="profile?.level || 1" />
        <p class="email">{{ maskedEmail }}</p>
        <button type="button" class="platform-btn-ghost me-logout" @click="logout">退出登录</button>
      </aside>

      <section class="me-main">
        <nav class="platform-tabs">
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

        <div v-show="activeTab === 'profile'" class="platform-panel ink-panel tab-panel">
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
                <button type="button" class="platform-btn-ghost sm" :disabled="avatarUploading" @click="pickAvatar">
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

          <div class="security-divider" />

          <form class="security-form" @submit.prevent="savePassword">
            <h3 class="security-title">修改密码</h3>
            <p class="security-hint">密码仅用于登录验证，不会在页面上展示或回显。</p>
            <label>
              当前密码
              <input
                v-model="passwordForm.current"
                type="password"
                autocomplete="current-password"
                required
              />
            </label>
            <label>
              新密码
              <input
                v-model="passwordForm.next"
                type="password"
                autocomplete="new-password"
                minlength="9"
                required
              />
            </label>
            <label>
              确认新密码
              <input
                v-model="passwordForm.confirm"
                type="password"
                autocomplete="new-password"
                minlength="9"
                required
              />
            </label>
            <p class="security-rule">至少 9 位，须含大写字母、小写字母和数字。</p>
            <p v-if="passwordMsg" class="success">{{ passwordMsg }}</p>
            <p v-if="passwordError" class="error">{{ passwordError }}</p>
            <button type="submit" class="btn-primary" :disabled="passwordLoading">更新密码</button>
          </form>
        </div>

        <div v-show="activeTab === 'checkin'" class="platform-panel ink-panel tab-panel checkin-tab">
          <div v-if="checkinLoading" class="muted">加载签到数据…</div>
          <template v-else-if="checkinStatus">
            <div class="checkin-summary">
              <div>
                <p class="checkin-level-label">当前等级</p>
                <p class="checkin-level-value">Lv.{{ checkinStatus.level }} {{ checkinStatus.title }}</p>
                <p class="checkin-xp">{{ checkinStatus.xp }} XP · 连续 {{ checkinStatus.streak }} 天</p>
              </div>
              <button
                v-if="!checkinStatus.checked_today"
                type="button"
                class="platform-btn-primary"
                :disabled="checkinBusy"
                @click="handleCheckin"
              >
                {{ checkinBusy ? '签到中…' : '立即签到' }}
              </button>
              <span v-else class="checkin-stamp-inline">今日已签</span>
            </div>

            <div class="checkin-progress-block">
              <div class="checkin-progress-bar">
                <span :style="{ width: `${checkinStatus.progress?.progress_pct || 0}%` }" />
              </div>
              <p class="checkin-progress-hint">
                <template v-if="checkinStatus.progress?.next_level">
                  距 Lv.{{ checkinStatus.progress.next_level }} {{ checkinStatus.progress.next_title }}
                  还需 {{ checkinStatus.progress.xp_to_next }} XP
                </template>
                <template v-else>已满级</template>
              </p>
            </div>

            <h3 class="checkin-section-title">近 3 月签到</h3>
            <div class="checkin-heatmap">
              <span
                v-for="cell in heatmapCells"
                :key="cell.date"
                class="heatmap-cell"
                :class="{ checked: cell.checked, today: cell.isToday }"
                :title="cell.date"
              />
            </div>

            <h3 class="checkin-section-title">等级权益</h3>
            <ul class="perk-list">
              <li
                v-for="tier in checkinStatus.tiers || []"
                :key="tier.level"
                :class="{ unlocked: (checkinStatus.level || 1) >= tier.level }"
              >
                <strong>Lv.{{ tier.level }} {{ tier.title }}</strong>
                <span>{{ tier.xp_required }} XP</span>
                <p v-if="tier.perks?.length">{{ tier.perks.join(' · ') }}</p>
                <p v-else class="muted">基础身份</p>
              </li>
            </ul>

            <h3 v-if="checkinStatus.xp_actions?.length" class="checkin-section-title">经验获取（每日上限）</h3>
            <ul v-if="checkinStatus.xp_actions?.length" class="xp-action-list">
              <li v-for="row in checkinStatus.xp_actions" :key="row.action">
                <span>{{ row.label }}</span>
                <span>+{{ row.xp }} XP</span>
                <span>{{ row.daily_max }} 次/日 · 上限 {{ row.daily_cap_xp }} XP</span>
              </li>
            </ul>

            <h3 class="checkin-section-title">签到记录</h3>
            <ul v-if="checkinHistory.length" class="checkin-history">
              <li v-for="row in checkinHistory" :key="row.date">
                <span>{{ row.date }}</span>
                <span>+{{ row.xp_gained }} XP</span>
                <span>连续 {{ row.streak_day }} 天</span>
              </li>
            </ul>
            <p v-else class="muted">暂无签到记录</p>
            <p v-if="checkinMsg" class="success">{{ checkinMsg }}</p>
          </template>
        </div>

        <div v-show="activeTab === 'posts'" class="platform-panel ink-panel tab-panel">
          <div class="panel-head">
            <router-link to="/app/posts/new" class="platform-btn-primary">写文章</router-link>
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

        <div v-show="activeTab === 'threads'" class="platform-panel ink-panel tab-panel">
          <div class="panel-head">
            <router-link to="/app/forum/new" class="platform-btn-primary">发帖</router-link>
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

        <div v-show="activeTab === 'messages'" class="platform-panel ink-panel tab-panel">
          <div class="panel-head">
            <button
              v-if="notifications.some((n) => !n.is_read)"
              type="button"
              class="platform-btn-ghost"
              @click="readAllNotifications"
            >
              全部已读
            </button>
          </div>
          <p v-if="notificationsLoading" class="muted">加载中…</p>
          <p v-else-if="!notifications.length" class="muted">暂无消息。收到点赞或回复会显示在这里。</p>
          <ul v-else class="notify-list">
            <li
              v-for="n in notifications"
              :key="n.id"
              class="notify-item"
              :class="{ unread: !n.is_read }"
              @click="openNotification(n)"
            >
              <span class="notify-dot" :class="{ on: !n.is_read }" aria-hidden="true" />
              <div class="notify-body">
                <p class="notify-text">{{ notificationText(n) }}</p>
                <p v-if="n.thread_title" class="notify-thread">《{{ n.thread_title }}》</p>
                <span class="date">{{ formatDate(n.created_at) }}</span>
              </div>
            </li>
          </ul>
        </div>

        <div v-show="activeTab === 'timeline'" class="tab-panel">
          <p v-if="timelineLoading" class="muted">加载中…</p>
          <p v-else-if="!timelineDays.length" class="muted">暂无专注记录，去番茄钟开始第一段吧。</p>
          <div v-else class="timeline">
            <section v-for="day in timelineDays" :key="day.date" class="platform-panel day-block">
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
  </PlatformPageShell>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlatformPageShell from '../components/platform/PlatformPageShell.vue'
import AvatarFrame from '../components/AvatarFrame.vue'
import LevelBadge from '../components/LevelBadge.vue'
import { PLATFORM_ME_INK_IMAGE, PLATFORM_ME_INK_POSITION } from '../data/inkTheme.js'
import { usePageMeta } from '../composables/usePageMeta'
import {
  deleteForumThread,
  deletePost,
  fetchMyForumThreads,
  fetchMyPosts,
  fetchNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  fetchPomodoroTimeline,
  fetchProfile,
  getPlatformToken,
  resolveMediaUrl,
  setPlatformToken,
  updateProfile,
  uploadAvatar,
  changePassword,
  doCheckin,
  fetchCheckinCalendar,
  fetchCheckinStatus,
} from '../api/platform.js'

usePageMeta({
  title: '个人中心',
  description: 'CYINC 主站个人中心：资料、文章、帖子与专注时间线。',
})

const tabs = [
  { id: 'profile', label: '资料' },
  { id: 'checkin', label: '签到' },
  { id: 'posts', label: '我的文章' },
  { id: 'threads', label: '我的帖子' },
  { id: 'messages', label: '消息' },
  { id: 'timeline', label: '专注时间线' },
]

const route = useRoute()
const router = useRouter()
const token = ref(getPlatformToken())
const activeTab = ref(
  route.query.tab === 'threads' ? 'threads'
    : route.query.tab === 'posts' ? 'posts'
      : route.query.tab === 'messages' ? 'messages'
        : route.query.tab === 'checkin' ? 'checkin'
          : 'profile',
)
const profile = ref(null)
const editForm = ref({ nickname: '', avatar: '' })
const posts = ref([])
const forumThreads = ref([])
const notifications = ref([])
const notificationsLoading = ref(false)
const timelineDays = ref([])
const loading = ref(false)
const postsLoading = ref(false)
const threadsLoading = ref(false)
const timelineLoading = ref(false)
const error = ref('')
const profileMsg = ref('')
const passwordForm = ref({ current: '', next: '', confirm: '' })
const passwordMsg = ref('')
const passwordError = ref('')
const passwordLoading = ref(false)
const avatarInputRef = ref(null)
const avatarUploading = ref(false)
const avatarPreviewOverride = ref('')
const checkinStatus = ref(null)
const checkinHistory = ref([])
const checkinLoading = ref(false)
const checkinBusy = ref(false)
const checkinMsg = ref('')

const heatmapCells = computed(() => {
  const checked = new Set(checkinHistory.value.map((r) => r.date))
  const today = new Date()
  const cells = []
  for (let i = 89; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const iso = d.toISOString().slice(0, 10)
    const isToday = i === 0
    cells.push({ date: iso, checked: checked.has(iso), isToday })
  }
  return cells
})

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

const maskedEmail = computed(() => {
  const email = profile.value?.email || ''
  const at = email.indexOf('@')
  if (at <= 1) return email
  const name = email.slice(0, at)
  const domain = email.slice(at)
  const visible = name.slice(0, 2)
  return `${visible}${'*'.repeat(Math.min(4, Math.max(1, name.length - 2)))}${domain}`
})

function authSessionExpired(message) {
  return /401|凭证|未登录|请先登录|登录已过期|token/i.test(message || '')
}

function syncToken() {
  const next = getPlatformToken()
  if (!next && token.value) logout()
  else token.value = next
}

function onStorageAuth(e) {
  if (e.key === 'cyinc_platform_token' || e.key === null) syncToken()
}

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
    if (authSessionExpired(e.message)) logout()
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

async function loadNotifications() {
  if (!token.value) return
  notificationsLoading.value = true
  try {
    const json = await fetchNotifications()
    notifications.value = json.data.items || []
  } catch (e) {
    error.value = e.message
  } finally {
    notificationsLoading.value = false
  }
}

function notificationText(n) {
  const who = n.actor?.nickname || n.actor?.username || '有人'
  if (n.type === 'reply') return `${who} 回复了你的帖子`
  if (n.type === 'thread_like') return `${who} 点赞了你的帖子`
  if (n.type === 'reply_like') return `${who} 点赞了你的评论`
  return `${who} 与你互动`
}

async function openNotification(n) {
  try {
    if (!n.is_read) {
      await markNotificationRead(n.id)
      n.is_read = true
      window.dispatchEvent(new CustomEvent('platform-notify-changed'))
    }
  } catch {
    /* ignore */
  }
  if (n.thread_id) {
    router.push(`/app/forum/t/${n.thread_id}`)
  }
}

async function readAllNotifications() {
  try {
    await markAllNotificationsRead()
    notifications.value = notifications.value.map((n) => ({ ...n, is_read: true }))
    window.dispatchEvent(new CustomEvent('platform-notify-changed'))
  } catch (e) {
    error.value = e.message
  }
}

async function loadCheckin() {
  if (!token.value) return
  checkinLoading.value = true
  try {
    const [statusJson, calJson] = await Promise.all([
      fetchCheckinStatus(),
      fetchCheckinCalendar(3),
    ])
    checkinStatus.value = statusJson.data
    checkinHistory.value = calJson.data?.history || []
  } catch (e) {
    error.value = e.message
  } finally {
    checkinLoading.value = false
  }
}

async function handleCheckin() {
  checkinBusy.value = true
  checkinMsg.value = ''
  try {
    const json = await doCheckin()
    checkinMsg.value = json.message || '签到成功'
    await Promise.all([loadCheckin(), loadProfile()])
    window.dispatchEvent(new CustomEvent('platform-checkin-done'))
  } catch (e) {
    error.value = e.message
  } finally {
    checkinBusy.value = false
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

async function savePassword() {
  syncToken()
  passwordError.value = ''
  passwordMsg.value = ''
  if (!token.value) {
    passwordError.value = '登录已过期，请重新登录后再修改密码'
    return
  }
  if (passwordForm.value.next !== passwordForm.value.confirm) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  passwordLoading.value = true
  try {
    const json = await changePassword({
      currentPassword: passwordForm.value.current,
      newPassword: passwordForm.value.next,
    })
    passwordForm.value = { current: '', next: '', confirm: '' }
    passwordMsg.value = json.message || '密码已更新'
  } catch (e) {
    passwordError.value = e.message
    if (authSessionExpired(e.message)) logout()
  } finally {
    passwordLoading.value = false
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
  await Promise.all([loadPosts(), loadThreads(), loadTimeline(), loadCheckin()])
}

watch(() => route.query.tab, (tab) => {
  if (tab === 'posts' || tab === 'threads' || tab === 'messages' || tab === 'timeline' || tab === 'profile' || tab === 'checkin') {
    activeTab.value = tab
  }
})

watch(activeTab, (tab) => {
  if (!token.value) return
  if (tab === 'posts') loadPosts()
  if (tab === 'threads') loadThreads()
  if (tab === 'messages') loadNotifications()
  if (tab === 'timeline') loadTimeline()
  if (tab === 'checkin') loadCheckin()
})

watch(token, (t) => { if (t) loadAll() })

onMounted(() => {
  syncToken()
  window.addEventListener('platform-auth-changed', syncToken)
  window.addEventListener('storage', onStorageAuth)
  window.addEventListener('platform-checkin-done', loadCheckin)
  if (token.value) loadAll()
})

onUnmounted(() => {
  window.removeEventListener('platform-auth-changed', syncToken)
  window.removeEventListener('storage', onStorageAuth)
  window.removeEventListener('platform-checkin-done', loadCheckin)
})
</script>

<style scoped>
.me-guest-title {
  margin: 0 0 0.5rem;
  font-size: 1.35rem;
}

.me-grid {
  display: grid;
  grid-template-columns: minmax(200px, 240px) 1fr;
  gap: 1.25rem;
}

.me-auth-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 1rem;
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

.me-logout {
  margin-top: 0.85rem;
  width: 100%;
}

form { display: grid; gap: 0.75rem; }

label {
  display: grid;
  gap: 0.35rem;
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--text);
}

input {
  border: 1px solid var(--border);
  padding: 0.55rem 0.65rem;
  font: inherit;
  background: var(--bg);
  color: var(--text);
}

input::placeholder {
  color: var(--text-muted);
  opacity: 0.85;
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

.panel-head .platform-btn-primary {
  text-decoration: none;
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

.btn-primary {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border: 1px solid var(--orange);
  background: var(--orange);
  color: #fff;
  width: fit-content;
}

.btn-primary:disabled { opacity: 0.55; }

.error { color: var(--error, #c0392b); font-size: 0.82rem; }
.success { color: var(--success, #2d6a4f); font-size: 0.82rem; }

[data-theme="dark"] .error { color: #ff8a80; }
[data-theme="dark"] .success { color: #95d5b2; }
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

.hint {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--steel, var(--text-muted));
}

.security-divider {
  height: 1px;
  background: var(--border);
  margin: 1.25rem 0;
}

.security-title {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
}

.security-hint,
.security-rule {
  margin: 0 0 0.75rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.security-form {
  display: grid;
  gap: 0.75rem;
}

.checkin-summary {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.checkin-level-label {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.checkin-level-value {
  margin: 0.2rem 0 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.checkin-xp {
  margin: 0.25rem 0 0;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

.checkin-stamp-inline {
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--orange);
  border: 2px solid var(--orange);
  padding: 0.25rem 0.55rem;
  transform: rotate(-6deg);
}

.checkin-progress-block {
  margin-bottom: 1.25rem;
}

.checkin-progress-bar {
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.checkin-progress-bar span {
  display: block;
  height: 100%;
  background: var(--orange);
}

.checkin-progress-hint {
  margin: 0.4rem 0 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.checkin-section-title {
  margin: 1rem 0 0.65rem;
  font-size: 0.92rem;
}

.checkin-heatmap {
  display: grid;
  grid-template-columns: repeat(15, 1fr);
  gap: 4px;
  margin-bottom: 0.5rem;
}

.heatmap-cell {
  aspect-ratio: 1;
  border-radius: 2px;
  background: var(--border);
}

.heatmap-cell.checked {
  background: rgba(232, 93, 4, 0.55);
}

.heatmap-cell.checked.today {
  background: var(--orange);
  box-shadow: 0 0 0 2px rgba(232, 93, 4, 0.35);
}

.perk-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.65rem;
}

.perk-list li {
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border);
  opacity: 0.55;
}

.perk-list li.unlocked {
  opacity: 1;
  border-color: rgba(232, 93, 4, 0.35);
}

.perk-list li strong {
  margin-right: 0.5rem;
}

.perk-list li span {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.perk-list li p {
  margin: 0.35rem 0 0;
  font-size: 0.82rem;
}

.xp-action-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.4rem;
}

.xp-action-list li {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.5rem;
  align-items: center;
  padding: 0.5rem 0.65rem;
  border: 1px dashed var(--border);
  font-size: 0.78rem;
}

.xp-action-list li span:nth-child(2) {
  font-family: var(--mono);
  color: var(--orange);
  font-size: 0.72rem;
}

.xp-action-list li span:nth-child(3) {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.checkin-history {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.45rem;
  font-family: var(--mono);
  font-size: 0.72rem;
}

.checkin-history li {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.75rem;
  border-bottom: 1px dashed var(--border);
  padding-bottom: 0.35rem;
}

@media (max-width: 720px) {
  .me-grid { grid-template-columns: 1fr; }
}

.notify-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}

.notify-item {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.notify-item:hover {
  border-color: color-mix(in srgb, var(--orange) 45%, var(--border));
  background: color-mix(in srgb, var(--orange) 5%, transparent);
}

.notify-item.unread {
  background: color-mix(in srgb, var(--orange) 7%, transparent);
}

.notify-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 0.35rem;
  background: transparent;
  flex-shrink: 0;
}

.notify-dot.on {
  background: var(--orange);
}

.notify-body {
  min-width: 0;
}

.notify-text {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text);
}

.notify-thread {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  color: var(--text-muted);
}

.notify-item .date {
  font-family: var(--mono);
  font-size: 0.66rem;
  color: var(--text-muted);
}</style>

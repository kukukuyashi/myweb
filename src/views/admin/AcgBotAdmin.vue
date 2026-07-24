<template>
  <div class="acg-admin">
    <header class="admin-topbar">
      <div v-if="!embedded" class="admin-brand">
        <span class="admin-badge">ACG BOT</span>
        <h1>资讯机器人</h1>
        <p>
          一键采集「今日新番 / ACG 新闻 / 二游更新」→ 人工审核 → 由机器人账号发布到论坛。
          链接均来自真实数据源。数据后台见
          <a href="/admin" target="_blank" rel="noopener">/admin SQLAdmin</a>
        </p>
      </div>
      <div class="admin-actions">
        <label v-if="authed" class="ai-toggle">
          <input v-model="useAi" type="checkbox" />
          Dify 润色
        </label>
        <button v-if="authed" type="button" class="btn btn-primary" :disabled="generating" @click="handleGenerate">
          {{ generating ? '采集中…' : '一键生成今日汇总' }}
        </button>
        <button v-if="authed" type="button" class="btn btn-ghost" :disabled="repairing" @click="handleRepairMedia">
          {{ repairing ? '补图中…' : '修复已发帖配图' }}
        </button>
        <button v-if="authed" type="button" class="btn btn-ghost" @click="reloadList">刷新</button>
        <button v-if="authed && !embedded" type="button" class="btn btn-ghost" @click="logout">退出</button>
      </div>
    </header>

    <div v-if="!authed && !embedded" class="admin-login-card">
      <h2>登录资讯机器人</h2>
      <p class="login-hint">使用与笔记管理台 / SQLAdmin 相同的运维账号。</p>
      <form class="login-form" @submit.prevent="handleLogin">
        <label>
          用户名
          <input v-model="loginForm.username" type="text" autocomplete="username" required />
        </label>
        <label>
          密码
          <input v-model="loginForm.password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="loginError" class="toast" data-type="error">{{ loginError }}</p>
        <button type="submit" class="btn btn-primary" :disabled="loggingIn">
          {{ loggingIn ? '登录中…' : '登录' }}
        </button>
      </form>
    </div>

    <div v-else class="admin-shell">
      <section class="admin-list">
        <div class="list-head">
          <h2>投稿 · {{ submissions.length }} 篇</h2>
          <div class="status-filters">
            <button
              v-for="opt in statusFilterOptions"
              :key="opt.value"
              type="button"
              class="filter-chip"
              :class="{ active: statusFilter === opt.value }"
              @click="selectStatus(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <p v-if="loadingList" class="hint">加载中…</p>
        <p v-else-if="submissions.length === 0" class="hint">暂无投稿，点右上角「一键生成」。</p>

        <ul v-else class="sub-list">
          <li
            v-for="sub in submissions"
            :key="sub.id"
            :class="{ active: current && current.id === sub.id }"
          >
            <button type="button" class="sub-item" @click="openSubmission(sub.id)">
              <span class="sub-title">{{ sub.title || '未命名' }}</span>
              <span class="sub-meta">{{ formatDate(sub.created_at) }}</span>
              <span class="status" :data-status="sub.status">{{ statusLabel(sub.status) }}</span>
            </button>
          </li>
        </ul>
      </section>

      <section class="admin-editor">
        <div v-if="!current" class="empty-editor">
          <h2>选择一篇投稿</h2>
          <p>或点击「一键生成今日汇总」采集当日资讯。</p>
        </div>

        <template v-else>
          <div class="editor-head">
            <div>
              <div class="editor-title-row">
                <h2>{{ form.title || '未命名' }}</h2>
                <span v-if="current.status === 'published'" class="dirty-badge published-badge">已发布</span>
                <span v-else-if="isDirty" class="dirty-badge">未保存</span>
              </div>
              <p class="path-line">
                #{{ current.id }} · 创建于 {{ formatDate(current.created_at) }}
                <template v-if="current.published_thread_id">
                  · <a :href="threadUrl(current.published_thread_id)" target="_blank" rel="noopener">查看论坛帖 #{{ current.published_thread_id }}</a>
                </template>
              </p>
            </div>
            <div class="editor-actions">
              <template v-if="current.status !== 'published'">
                <button type="button" class="btn btn-ghost" :disabled="saving || !isDirty" @click="saveCurrent">
                  {{ saving ? '保存中…' : '保存' }}
                </button>
                <button type="button" class="btn btn-ghost" :disabled="previewing" @click="runPreview()">
                  {{ previewing ? '预览中…' : '刷新预览' }}
                </button>
                <button type="button" class="btn btn-primary" :disabled="publishing || isDirty" :title="isDirty ? '请先保存再发布' : ''" @click="publishCurrent">
                  {{ publishing ? '发布中…' : '发布到论坛' }}
                </button>
                <button type="button" class="btn btn-danger" :disabled="discarding" @click="discardCurrent">
                  {{ discarding ? '丢弃中…' : '丢弃' }}
                </button>
              </template>
              <a
                v-else-if="current.published_thread_id"
                class="btn btn-primary"
                :href="threadUrl(current.published_thread_id)"
                target="_blank"
                rel="noopener"
              >打开论坛帖</a>
            </div>
          </div>

          <p v-if="message" class="toast" :data-type="messageType">{{ message }}</p>

          <div class="meta-grid">
            <label>
              标题
              <input v-model="form.title" type="text" :disabled="current.status === 'published'" />
            </label>
            <label>
              发布板块
              <select v-model="form.category_id" :disabled="current.status === 'published'">
                <option :value="null">（未指定，用默认板块）</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </label>
            <label class="span-2">
              封面 URL（可选）
              <input v-model="form.cover_url" type="text" placeholder="https://…" :disabled="current.status === 'published'" />
            </label>
          </div>

          <div v-if="sourceItems.length" class="source-panel">
            <div class="source-head">来源核对 · {{ sourceItems.length }} 条真实链接</div>
            <ul class="source-list">
              <li v-for="(item, idx) in sourceItems" :key="idx">
                <span class="source-kind">{{ item.kind || item.source || '来源' }}</span>
                <a v-if="item.link" :href="item.link" target="_blank" rel="noopener">{{ item.title || item.link }}</a>
                <span v-else>{{ item.title }}</span>
              </li>
            </ul>
          </div>

          <div class="editor-panels" :class="`layout-${editorLayout}`">
            <div class="panel-label editor-panel">
              <div class="md-toolbar">
                <span>Markdown 正文</span>
                <div class="layout-toggle">
                  <button type="button" :class="{ active: editorLayout === 'split' }" @click="editorLayout = 'split'">分栏</button>
                  <button type="button" :class="{ active: editorLayout === 'edit' }" @click="editorLayout = 'edit'">编辑</button>
                  <button type="button" :class="{ active: editorLayout === 'preview' }" @click="editorLayout = 'preview'">预览</button>
                </div>
              </div>
              <textarea v-model="form.content" spellcheck="false" :disabled="current.status === 'published'" />
            </div>
            <div class="panel-label preview-panel">
              <div class="preview-head">
                <span>预览 {{ previewing ? '（更新中…）' : '' }}</span>
                <div class="layout-toggle layout-toggle--preview">
                  <button type="button" :class="{ active: editorLayout === 'split' }" @click="editorLayout = 'split'">分栏</button>
                  <button type="button" :class="{ active: editorLayout === 'edit' }" @click="editorLayout = 'edit'">编辑</button>
                  <button type="button" :class="{ active: editorLayout === 'preview' }" @click="editorLayout = 'preview'">预览</button>
                </div>
              </div>
              <div class="preview-box article-body">
                <div v-if="previewHtml" v-html="previewHtml" />
                <p v-else class="hint">编辑时自动预览，或点击「刷新预览」</p>
              </div>
            </div>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import {
  clearNotesAdminToken,
  fetchNotesAdminMe,
  getNotesAdminToken,
  loginNotesAdmin,
} from '../../api/notesAdmin'
import {
  discardSubmission,
  fetchForumCategories,
  fetchSubmission,
  fetchSubmissions,
  generateDigest,
  previewSubmission,
  publishSubmission,
  repairPublishedMedia,
  updateSubmission,
} from '../../api/acgBot'

defineProps({
  embedded: { type: Boolean, default: false },
})

const authed = ref(Boolean(getNotesAdminToken()))
const loggingIn = ref(false)
const loginError = ref('')
const loginForm = reactive({ username: 'Cyinc', password: '' })

const baseUrl = import.meta.env.BASE_URL || '/'
const useAi = ref(false)
const generating = ref(false)
const repairing = ref(false)
const loadingList = ref(false)
const saving = ref(false)
const publishing = ref(false)
const previewing = ref(false)
const discarding = ref(false)
const statusFilter = ref('all')
const submissions = ref([])
const categories = ref([])
const current = ref(null)
const sourceItems = ref([])
const previewHtml = ref('')
const editorLayout = ref('split')
const message = ref('')
const messageType = ref('info')
const savedSnapshot = ref('')

const form = reactive({
  title: '',
  content: '',
  category_id: null,
  cover_url: '',
})

const statusFilterOptions = [
  { value: 'all', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'published', label: '已发布' },
  { value: 'discarded', label: '已丢弃' },
]

const isDirty = computed(() => savedSnapshot.value !== '' && savedSnapshot.value !== snapshotForm())

function snapshotForm() {
  return JSON.stringify({
    title: form.title,
    content: form.content,
    category_id: form.category_id,
    cover_url: form.cover_url,
  })
}

function takeSnapshot() {
  savedSnapshot.value = snapshotForm()
}

function statusLabel(status) {
  return { draft: '草稿', published: '已发布', discarded: '已丢弃' }[status] || status
}

function formatDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const p = (n) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

function threadUrl(threadId) {
  return `${baseUrl}app/forum/t/${threadId}`
}

function flash(text, type = 'info') {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    if (message.value === text) message.value = ''
  }, 3600)
}

function confirmIfDirty() {
  if (!isDirty.value) return true
  return window.confirm('当前草稿有未保存的修改，确定继续吗？')
}

async function bootstrapAuth() {
  if (!getNotesAdminToken()) {
    authed.value = false
    return
  }
  try {
    await fetchNotesAdminMe()
    authed.value = true
    await Promise.all([reloadList(), loadCategories()])
  } catch {
    clearNotesAdminToken()
    authed.value = false
  }
}

async function handleLogin() {
  loggingIn.value = true
  loginError.value = ''
  try {
    await loginNotesAdmin(loginForm.username.trim(), loginForm.password)
    loginForm.password = ''
    authed.value = true
    await Promise.all([reloadList(), loadCategories()])
  } catch (err) {
    loginError.value = err.message || '登录失败'
    authed.value = false
  } finally {
    loggingIn.value = false
  }
}

function logout() {
  clearNotesAdminToken()
  authed.value = false
  submissions.value = []
  current.value = null
  previewHtml.value = ''
  flash('已退出', 'info')
}

async function loadCategories() {
  try {
    const res = await fetchForumCategories()
    categories.value = res.categories || []
  } catch {
    /* ignore */
  }
}

async function reloadList() {
  loadingList.value = true
  try {
    const res = await fetchSubmissions(statusFilter.value)
    submissions.value = res.submissions || []
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    loadingList.value = false
  }
}

async function selectStatus(value) {
  statusFilter.value = value
  await reloadList()
}

async function handleGenerate() {
  generating.value = true
  try {
    const res = await generateDigest({ useAi: useAi.value })
    const list = res?.submissions || []
    const meta = res?.meta || {}
    const first = list[0]
    const msg = list.length
      ? `已生成 ${list.length} 篇草稿（1 篇速报 + ${list.length - 1} 篇深度文章）`
      : '已触发采集，但未生成草稿，请检查数据源'
    flash(msg, list.length ? 'success' : 'error')
    if (meta.article_count === 0 && list.length) {
      flash(`${msg} · 深度文章 0 篇（RSS 内容不足或均无图）`, 'info')
    }
    await reloadList()
    if (first?.id) await openSubmission(first.id)
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    generating.value = false
  }
}

async function handleRepairMedia() {
  repairing.value = true
  try {
    const res = await repairPublishedMedia(30)
    const n = res?.fixed?.length || 0
    flash(n ? `已为 ${n} 篇已发帖补上配图` : '没有需要补图的帖子（或抓取失败）', n ? 'success' : 'info')
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    repairing.value = false
  }
}

async function openSubmission(id) {
  if (current.value && current.value.id === id) return
  if (!confirmIfDirty()) return
  try {
    const data = await fetchSubmission(id)
    current.value = data
    form.title = data.title || ''
    form.content = data.content || ''
    form.category_id = data.category_id ?? null
    form.cover_url = data.cover_url || ''
    sourceItems.value = normalizeSource(data.source_meta)
    previewHtml.value = ''
    takeSnapshot()
    await runPreview(true)
  } catch (err) {
    flash(err.message, 'error')
  }
}

function normalizeSource(meta) {
  if (!meta) return []
  if (Array.isArray(meta)) return meta
  if (Array.isArray(meta.items)) return meta.items
  const out = []
  for (const key of Object.keys(meta)) {
    const val = meta[key]
    if (!Array.isArray(val)) continue
    for (const it of val) {
      out.push({
        kind: key,
        title: it.title || it.name || it.name_cn || '(未命名)',
        link: it.link || it.watch_url || it.url || '',
        source: it.source || '',
      })
    }
  }
  return out
}

async function saveCurrent() {
  if (!current.value) return
  saving.value = true
  try {
    const data = await updateSubmission(current.value.id, {
      title: form.title,
      content: form.content,
      category_id: form.category_id,
      cover_url: form.cover_url,
    })
    current.value = data
    sourceItems.value = normalizeSource(data.source_meta)
    takeSnapshot()
    flash('已保存', 'success')
    await reloadList()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    saving.value = false
  }
}

async function runPreview(silent = false) {
  if (!current.value) return
  previewing.value = true
  try {
    const res = await previewSubmission(current.value.id)
    previewHtml.value = res.html || ''
  } catch (err) {
    if (!silent) flash(err.message, 'error')
  } finally {
    previewing.value = false
  }
}

async function publishCurrent() {
  if (!current.value) return
  if (isDirty.value) {
    flash('请先保存修改再发布', 'error')
    return
  }
  if (!window.confirm('确定以机器人账号发布到论坛？')) return
  publishing.value = true
  try {
    const res = await publishSubmission(current.value.id)
    flash(`已发布 · 论坛帖 #${res.thread_id}`, 'success')
    await openSubmissionForce(current.value.id)
    await reloadList()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    publishing.value = false
  }
}

async function openSubmissionForce(id) {
  const data = await fetchSubmission(id)
  current.value = data
  form.title = data.title || ''
  form.content = data.content || ''
  form.category_id = data.category_id ?? null
  form.cover_url = data.cover_url || ''
  sourceItems.value = normalizeSource(data.source_meta)
  takeSnapshot()
}

async function discardCurrent() {
  if (!current.value) return
  if (!window.confirm('确定丢弃该草稿？')) return
  discarding.value = true
  try {
    await discardSubmission(current.value.id)
    flash('已丢弃', 'success')
    current.value = null
    previewHtml.value = ''
    savedSnapshot.value = ''
    await reloadList()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    discarding.value = false
  }
}

let previewTimer = null
watch(
  () => form.content,
  () => {
    if (!current.value || !authed.value || current.value.status === 'published') return
    clearTimeout(previewTimer)
    previewTimer = setTimeout(() => runPreview(true), 600)
  },
)

onMounted(bootstrapAuth)
onBeforeUnmount(() => clearTimeout(previewTimer))
</script>

<style scoped>
.acg-admin {
  width: 100%;
  max-width: 100vw;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
}

.admin-topbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border);
  background: var(--bg-paper);
}

.admin-badge {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  color: #fff;
  background: var(--orange);
}

.admin-brand h1 {
  margin: 0.35rem 0 0;
  font-size: 1.35rem;
}

.admin-brand p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.85rem;
  max-width: 46rem;
}

.admin-brand a {
  color: var(--orange);
}

.admin-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.ai-toggle {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.admin-login-card {
  max-width: 28rem;
  margin: 3rem auto;
  padding: 1.75rem 1.5rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  border-radius: 10px;
}

.admin-login-card h2 {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
}

.login-hint {
  margin: 0 0 1.25rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.login-form {
  display: grid;
  gap: 0.85rem;
}

.login-form label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.85rem;
}

.login-form input {
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font: inherit;
}

.admin-shell {
  display: grid;
  grid-template-columns: minmax(240px, 320px) minmax(0, 1fr);
  width: 100%;
  min-height: calc(100vh - 88px);
}

.admin-list,
.admin-editor {
  min-height: 100%;
}

.admin-list {
  border-right: 1px solid var(--border);
  padding: 1rem;
  overflow: auto;
}

.list-head {
  display: grid;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.list-head h2 {
  margin: 0;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.status-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.filter-chip {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: inherit;
  padding: 0.2rem 0.5rem;
  font-size: 0.72rem;
  cursor: pointer;
}

.filter-chip.active {
  border-color: var(--orange);
  background: var(--orange-light);
}

.sub-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.45rem;
}

.sub-item {
  width: 100%;
  text-align: left;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  padding: 0.65rem 0.75rem;
  cursor: pointer;
  color: inherit;
  display: grid;
  gap: 0.3rem;
}

.sub-list li.active .sub-item {
  border-color: var(--orange);
  box-shadow: inset 0 0 0 1px var(--orange);
}

.sub-title {
  font-weight: 600;
}

.sub-meta,
.path-line,
.hint {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.status {
  display: inline-block;
  width: fit-content;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  padding: 0.1rem 0.35rem;
  border: 1px solid var(--border);
}

.status[data-status='published'] {
  color: #2a7a49;
  border-color: #9fd4b0;
}

.status[data-status='draft'] {
  color: var(--steel);
}

.status[data-status='discarded'] {
  color: #a33;
  border-color: #e59a9a;
}

.admin-editor {
  padding: 1rem;
  overflow: auto;
}

.empty-editor {
  display: grid;
  place-content: center;
  min-height: 320px;
  text-align: center;
  color: var(--text-muted);
}

.editor-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.editor-head h2 {
  margin: 0;
}

.editor-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.path-line a {
  color: var(--orange);
}

.dirty-badge {
  font-size: 0.72rem;
  color: var(--orange);
  border: 1px solid #efb38a;
  padding: 0.1rem 0.4rem;
}

.published-badge {
  color: #2a7a49;
  border-color: #9fd4b0;
}

.editor-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.meta-grid label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.78rem;
  color: var(--text-muted);
}

.meta-grid .span-2 {
  grid-column: span 2;
}

.meta-grid input,
.meta-grid select,
textarea {
  width: 100%;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: inherit;
  padding: 0.45rem 0.55rem;
  font: inherit;
}

.source-panel {
  margin-bottom: 0.85rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
}

.source-head {
  padding: 0.45rem 0.65rem;
  border-bottom: 1px solid var(--border);
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.source-list {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0.65rem;
  display: grid;
  gap: 0.35rem;
  max-height: 180px;
  overflow: auto;
}

.source-list li {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  font-size: 0.82rem;
}

.source-kind {
  flex-shrink: 0;
  font-family: var(--mono);
  font-size: 0.66rem;
  color: var(--text-muted);
  border: 1px solid var(--border);
  padding: 0.05rem 0.3rem;
}

.source-list a {
  color: var(--orange);
  word-break: break-all;
}

.editor-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  min-height: 420px;
}

.panel-label {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 0.35rem;
  font-size: 0.78rem;
  color: var(--text-muted);
}

.md-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: space-between;
}

.layout-toggle {
  display: flex;
  border: 1px solid var(--border);
}

.layout-toggle button {
  border: none;
  background: var(--bg-paper);
  padding: 0.2rem 0.45rem;
  font-size: 0.72rem;
  cursor: pointer;
  color: inherit;
}

.layout-toggle button.active {
  background: var(--orange-light);
}

textarea {
  min-height: 420px;
  resize: vertical;
  font-family: var(--mono);
  line-height: 1.55;
}

.preview-box {
  min-height: 420px;
  overflow: auto;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  padding: 0.85rem 1rem;
}

.preview-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.editor-panels.layout-split .layout-toggle--preview {
  display: none;
}

.editor-panels.layout-edit .preview-panel {
  display: none;
}

.editor-panels.layout-preview .editor-panel {
  display: none;
}

.editor-panels.layout-edit,
.editor-panels.layout-preview {
  grid-template-columns: 1fr;
}

.btn {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: inherit;
  padding: 0.45rem 0.75rem;
  cursor: pointer;
  font: inherit;
}

.btn-primary {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.btn-danger {
  border-color: #d88;
  color: #a33;
}

.btn-danger:hover:not(:disabled) {
  background: #fff0f0;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.toast {
  margin: 0 0 0.75rem;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
}

.toast[data-type='success'] {
  border-color: #9fd4b0;
}

.toast[data-type='error'] {
  border-color: #e59a9a;
  color: #8a2e2e;
}

@media (max-width: 1100px) {
  .admin-shell {
    grid-template-columns: 1fr;
  }

  .editor-panels {
    grid-template-columns: 1fr;
  }
}
</style>

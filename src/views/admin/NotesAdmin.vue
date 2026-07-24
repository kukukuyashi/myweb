<template>
  <div class="notes-admin">
    <header class="admin-topbar">
      <div v-if="!embedded" class="admin-brand">
        <span class="admin-badge">NOTES</span>
        <h1>笔记管理台</h1>
        <p>
          Markdown 源在服务器 <code>笔记/</code> · 发布写入 <code>Content/</code> +
          <code>data/posts.json</code>（无需整站 Rebuild）· 数据后台请用
          <a href="/admin" target="_blank" rel="noopener">/admin SQLAdmin</a>
        </p>
      </div>
      <div class="admin-actions">
        <button
          v-if="authed"
          type="button"
          class="btn btn-ghost"
          :disabled="syncingContent || !contentOrphans.length"
          @click="handleSyncContent"
        >
          {{ syncingContent ? '同步中…' : contentOrphans.length ? `同步 Content (${contentOrphans.length})` : '同步 Content' }}
        </button>
        <button
          v-if="authed"
          type="button"
          class="btn btn-ghost"
          :disabled="adoptingAll"
          title="把全部仅站点文章生成 Markdown 源，使其可在管理台编辑"
          @click="handleAdoptAll"
        >
          {{ adoptingAll ? '认领中…' : '认领全部仅站点' }}
        </button>
        <button v-if="authed" type="button" class="btn btn-ghost" @click="reloadAll">刷新</button>
        <button v-if="authed" type="button" class="btn btn-primary" @click="showCreate = true">新建笔记</button>
        <button v-if="authed && !embedded" type="button" class="btn btn-ghost" @click="logout">退出</button>
      </div>
    </header>

    <div v-if="!authed && !embedded" class="admin-login-card">
      <h2>登录笔记管理台</h2>
      <p class="login-hint">使用与 SQLAdmin 相同的运维账号（ADMIN_USERNAME / 密码）。</p>
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

    <template v-else>
      <div v-if="contentOrphans.length" class="content-sync-banner">
        <div>
          <strong>Content/ 未登记</strong>
          <span>{{ contentOrphans.length }} 篇 HTML 尚未写入 posts.js，站点首页/归档不会显示。</span>
        </div>
        <ul>
          <li v-for="item in contentOrphans" :key="item.file">{{ item.title }} · {{ item.file }}</li>
        </ul>
      </div>

      <div class="admin-shell">
      <aside class="admin-sidebar">
        <h2>分类</h2>
        <p class="sidebar-hint">拖拽笔记到分类上即可移动</p>
        <ul class="category-list">
          <li
            v-for="cat in droppableCategories"
            :key="cat.name"
            :class="{
              active: activeCategory === cat.name,
              'drop-target': dropTarget === cat.name,
              'drop-disabled': cat.name === '全部' || cat.name === '站点文章',
            }"
            @dragover.prevent="onCategoryDragOver(cat.name)"
            @dragleave="onCategoryDragLeave(cat.name)"
            @drop.prevent="onCategoryDrop(cat.name)"
          >
            <button type="button" @click="selectCategory(cat.name)">
              <span>{{ cat.name }}</span>
              <span class="count">{{ cat.count }}</span>
            </button>
          </li>
        </ul>
        <div class="sidebar-foot">
          <p>目录结构</p>
          <code>笔记/{{ folderHint }}/</code>
        </div>
      </aside>

      <section class="admin-list">
        <div class="list-head">
          <h2>{{ activeCategory }} · {{ filteredNotes.length }} 篇</h2>
          <input v-model="search" type="search" placeholder="搜索标题 / 标签…" class="search-input" />
          <div class="status-filters">
            <button
              v-for="opt in statusFilterOptions"
              :key="opt.value"
              type="button"
              class="filter-chip"
              :class="{ active: statusFilter === opt.value }"
              @click="statusFilter = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <p v-if="loadingList" class="hint">加载中…</p>
        <p v-else-if="filteredNotes.length === 0" class="hint">该分类下暂无笔记</p>

        <ul v-else class="note-list">
          <li
            v-for="note in filteredNotes"
            :key="note.relPath"
            :class="{ active: currentRelPath === note.relPath, dragging: draggingPath === note.relPath }"
            :draggable="!note.siteOnly"
            @dragstart="onNoteDragStart(note, $event)"
            @dragend="onNoteDragEnd"
          >
            <button type="button" class="note-item" @click="openNote(note.relPath)">
              <span class="note-drag" title="拖拽到左侧分类">⠿</span>
              <span class="note-title">
                {{ note.title }}
                <span v-if="note.siteOnly" class="site-only-tag">仅站点</span>
              </span>
              <span class="note-meta">{{ note.date || '无日期' }} · {{ note.folder }}</span>
              <span class="status" :data-status="note.status">{{ statusLabel(note.status) }}</span>
            </button>
          </li>
        </ul>
      </section>

      <section class="admin-editor">
        <template v-if="!currentRelPath">
          <div class="empty-editor">
            <h2>选择一篇笔记</h2>
            <p>或点击「新建笔记」开始写作。左侧「站点文章」可查看仅存在于 Content/ + posts.json 的已发布文章。</p>
          </div>
        </template>

        <template v-else>
          <div class="editor-head">
            <div>
              <div class="editor-title-row">
                <h2>{{ form.meta.title || '未命名' }}</h2>
                <span v-if="currentSiteOnly" class="dirty-badge site-only-badge">仅站点</span>
                <span v-else-if="isDirty" class="dirty-badge">未保存</span>
                <span v-else-if="lastSavedHint" class="saved-hint">{{ lastSavedHint }}</span>
              </div>
              <p class="path-line">
                <code v-if="currentSiteOnly">Content/{{ currentHtmlFile }}</code>
                <code v-else>笔记/{{ currentRelPath }}</code>
              </p>
              <p v-if="currentSiteOnly" class="site-only-hint">
                此文仅登记在 <code>posts.json</code> 与 <code>Content/</code>，服务器没有 Markdown 源文件。如需在管理台编辑，请「新建笔记」后重新发布。
              </p>
              <p v-else-if="currentPostId" class="publish-link">
                已发布 ·
                <a :href="postPreviewUrl" target="_blank" rel="noopener">预览文章 #{{ currentPostId }}</a>
              </p>
            </div>
            <div class="editor-actions">
              <template v-if="!currentSiteOnly">
              <button type="button" class="btn btn-ghost" :disabled="saving" title="Ctrl+S" @click="saveCurrent">
                {{ saving ? '保存中…' : '保存' }}
              </button>
              <button type="button" class="btn btn-ghost" :disabled="previewing" @click="runPreview">
                {{ previewing ? '预览中…' : '刷新预览' }}
              </button>
              <button type="button" class="btn btn-primary" :disabled="publishing || isDirty" :title="isDirty ? '请先保存再发布' : ''" @click="publishCurrent">
                {{ publishing ? '发布中…' : '发布到博客' }}
              </button>
              <button type="button" class="btn btn-danger" :disabled="deleting" @click="deleteCurrent">
                {{ deleting ? '删除中…' : '删除' }}
              </button>
              </template>
              <template v-if="currentSiteOnly">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="adopting"
                title="把本文反解析为 Markdown 源，生成后即可在管理台编辑 / 删除"
                @click="handleAdoptCurrent"
              >
                {{ adopting ? '转换中…' : '转为可编辑' }}
              </button>
              <a
                v-if="currentPostId"
                class="btn btn-ghost"
                :href="postPreviewUrl"
                target="_blank"
                rel="noopener"
              >打开站点预览</a>
              </template>
            </div>
          </div>

          <p v-if="message" class="toast" :data-type="messageType">{{ message }}</p>

          <div v-if="currentSiteOnly" class="site-only-panel">
            <dl class="site-only-meta">
              <div><dt>日期</dt><dd>{{ form.meta.date }}</dd></div>
              <div><dt>分类</dt><dd>{{ form.meta.category }}</dd></div>
              <div><dt>标签</dt><dd>{{ (form.meta.tags || []).join(' · ') || '—' }}</dd></div>
              <div class="span-all"><dt>摘要</dt><dd>{{ form.meta.excerpt || '—' }}</dd></div>
            </dl>
          </div>

          <template v-else>
          <div class="meta-grid">
            <label>
              标题
              <input v-model="form.meta.title" type="text" />
            </label>
            <label>
              日期
              <input v-model="form.meta.date" type="date" />
            </label>
            <label>
              分类
              <select v-model="form.meta.category">
                <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </label>
            <label>
              封面
              <div class="cover-field">
                <input v-model="form.meta.cover" type="text" placeholder="img/bkm/1.jfif" />
                <img
                  v-if="coverPreviewUrl"
                  :src="coverPreviewUrl"
                  alt="封面预览"
                  class="cover-thumb"
                  @error="coverImgError = true"
                />
              </div>
              <div v-if="coverOptions.length" class="cover-picker">
                <button
                  v-for="cover in coverOptions"
                  :key="cover"
                  type="button"
                  class="cover-option"
                  :class="{ active: form.meta.cover === cover }"
                  :title="cover"
                  @click="form.meta.cover = cover"
                >
                  <img :src="coverImg(cover)" :alt="cover" loading="lazy" />
                </button>
              </div>
            </label>
            <label class="span-2">
              标签（逗号分隔）
              <input v-model="tagsInput" type="text" />
            </label>
            <label class="span-2">
              摘要
              <input v-model="form.meta.excerpt" type="text" />
            </label>
          </div>

          <div class="editor-panels" :class="`layout-${editorLayout}`">
            <div class="panel-label editor-panel">
              <div class="md-toolbar">
                <span>Markdown 正文</span>
                <div class="md-toolbar-actions">
                  <button type="button" class="md-btn" title="粗体" @click="insertMarkdown('**', '**', '粗体')">B</button>
                  <button type="button" class="md-btn" title="斜体" @click="insertMarkdown('*', '*', '斜体')">I</button>
                  <button type="button" class="md-btn" title="二级标题" @click="insertLinePrefix('## ')">H2</button>
                  <button type="button" class="md-btn" title="链接" @click="insertMarkdown('[', '](url)', '文字')">链</button>
                  <button type="button" class="md-btn" title="插入图片" :disabled="uploadingImage" @click="pickNoteImage">
                    {{ uploadingImage ? '…' : '图' }}
                  </button>
                  <button type="button" class="md-btn" title="行内代码" @click="insertMarkdown('`', '`', 'code')">`</button>
                  <button type="button" class="md-btn" title="代码块" @click="insertCodeBlock">```</button>
                  <button type="button" class="md-btn" title="列表" @click="insertLinePrefix('- ')">•</button>
                  <button type="button" class="md-btn" title="引用" @click="insertLinePrefix('> ')">引</button>
                  <input
                    ref="imageInputRef"
                    type="file"
                    accept="image/jpeg,image/png,image/webp,image/gif"
                    class="md-file-input"
                    @change="onNoteImageSelected"
                  />
                </div>
                <div class="layout-toggle">
                  <button type="button" :class="{ active: editorLayout === 'split' }" @click="editorLayout = 'split'">分栏</button>
                  <button type="button" :class="{ active: editorLayout === 'edit' }" @click="editorLayout = 'edit'">编辑</button>
                  <button type="button" :class="{ active: editorLayout === 'preview' }" @click="editorLayout = 'preview'">预览</button>
                </div>
              </div>
              <textarea ref="textareaRef" v-model="form.body" spellcheck="false" />
              <p class="editor-stats">{{ bodyStats }}</p>
            </div>
            <div class="panel-label preview-panel">
              <div class="preview-head">
                <span>预览 {{ previewing ? '（更新中…）' : '' }}</span>
                <div class="preview-head-right">
                  <span v-if="currentStatus" class="status" :data-status="currentStatus">
                    {{ statusLabel(currentStatus) }}
                  </span>
                  <div class="layout-toggle layout-toggle--preview">
                    <button type="button" :class="{ active: editorLayout === 'split' }" @click="editorLayout = 'split'">分栏</button>
                    <button type="button" :class="{ active: editorLayout === 'edit' }" @click="editorLayout = 'edit'">编辑</button>
                    <button type="button" :class="{ active: editorLayout === 'preview' }" @click="editorLayout = 'preview'">预览</button>
                  </div>
                </div>
              </div>
              <div class="preview-box article-body">
                <div v-if="previewHtml" v-html="previewHtml" />
                <p v-else class="hint">编辑时自动预览，或点击「刷新预览」</p>
              </div>
            </div>
          </div>
          </template>
        </template>
      </section>
    </div>
    </template>

    <dialog ref="createDialog" class="create-dialog" @close="showCreate = false">
      <form @submit.prevent="submitCreate">
        <h2>新建笔记</h2>
        <label>
          标题
          <input v-model="createForm.title" required />
        </label>
        <label>
          存放分类
          <select v-model="createForm.category">
            <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
            <option value="_drafts">草稿 (_drafts)</option>
          </select>
        </label>
        <label>
          摘要
          <input v-model="createForm.excerpt" />
        </label>
        <label class="checkbox">
          <input v-model="createForm.asDraft" type="checkbox" />
          保存到草稿箱（_drafts）
        </label>
        <div class="dialog-actions">
          <button type="button" class="btn btn-ghost" @click="closeCreate">取消</button>
          <button type="submit" class="btn btn-primary">创建</button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import {
  clearNotesAdminToken,
  createNote,
  deleteNote,
  fetchCategories,
  fetchContentStatus,
  fetchCovers,
  fetchNote,
  fetchNotes,
  fetchNotesAdminMe,
  getNotesAdminToken,
  loginNotesAdmin,
  moveNote,
  previewNote,
  publishNote,
  saveNote,
  syncContent,
  uploadNoteImage,
  adoptSiteNote,
  adoptAllSiteNotes,
} from '../../api/notesAdmin'

defineProps({
  embedded: { type: Boolean, default: false },
})

const authed = ref(Boolean(getNotesAdminToken()))
const loggingIn = ref(false)
const loginError = ref('')
const loginForm = reactive({
  username: 'Cyinc',
  password: '',
})
const baseUrl = import.meta.env.BASE_URL || '/'
const categories = ref([])
const notes = ref([])
const activeCategory = ref('全部')
const currentRelPath = ref('')
const currentSiteOnly = ref(false)
const currentHtmlFile = ref('')
const currentStatus = ref('')
const currentPostId = ref(null)
const loadingList = ref(false)
const saving = ref(false)
const publishing = ref(false)
const previewing = ref(false)
const uploadingImage = ref(false)
const deleting = ref(false)
const search = ref('')
const statusFilter = ref('all')
const message = ref('')
const messageType = ref('info')
const previewHtml = ref('')
const createDialog = ref(null)
const textareaRef = ref(null)
const imageInputRef = ref(null)
const showCreate = ref(false)
const draggingPath = ref('')
const dropTarget = ref('')
const savedSnapshot = ref('')
const lastSavedAt = ref(null)
const coverOptions = ref([])
const coverImgError = ref(false)
const editorLayout = ref('split')
const contentOrphans = ref([])
const syncingContent = ref(false)
const adopting = ref(false)
const adoptingAll = ref(false)

const statusFilterOptions = [
  { value: 'all', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'published', label: '已发布' },
  { value: 'modified', label: '有改动' },
]

const categoryOptions = computed(() =>
  categories.value
    .map((cat) => cat.name)
    .filter((name) => !['全部', '草稿', '未分类', '站点文章'].includes(name)),
)

const form = reactive({
  meta: {
    title: '',
    date: '',
    category: '学习',
    excerpt: '',
    cover: '',
    tags: [],
  },
  body: '',
})

const createForm = reactive({
  title: '',
  category: '学习',
  excerpt: '',
  asDraft: false,
})

const tagsInput = computed({
  get: () => (form.meta.tags || []).join(', '),
  set: (value) => {
    form.meta.tags = value
      .split(/[,，]/)
      .map((t) => t.trim())
      .filter(Boolean)
  },
})

const filteredNotes = computed(() => {
  let list = notes.value
  if (statusFilter.value !== 'all') {
    list = list.filter((note) => note.status === statusFilter.value)
  }
  const q = search.value.trim().toLowerCase()
  if (!q) return list
  return list.filter((note) => {
    const hay = `${note.title} ${note.excerpt} ${(note.tags || []).join(' ')}`.toLowerCase()
    return hay.includes(q)
  })
})

const isDirty = computed(() => savedSnapshot.value !== '' && savedSnapshot.value !== snapshotForm())

const lastSavedHint = computed(() => {
  if (!lastSavedAt.value || isDirty.value) return ''
  const t = lastSavedAt.value
  return `已保存 ${t.getHours().toString().padStart(2, '0')}:${t.getMinutes().toString().padStart(2, '0')}`
})

const postPreviewUrl = computed(() => {
  if (!currentPostId.value) return ''
  return `${baseUrl}content/${currentPostId.value}`
})

const coverPreviewUrl = computed(() => {
  if (coverImgError.value || !form.meta.cover?.trim()) return ''
  return coverImg(form.meta.cover.trim())
})

const bodyStats = computed(() => {
  const text = form.body || ''
  const chars = text.replace(/\s/g, '').length
  const lines = text ? text.split('\n').length : 0
  const words = text.trim() ? text.trim().split(/\s+/).length : 0
  return `${chars} 字 · ${words} 词 · ${lines} 行`
})

function snapshotForm() {
  return JSON.stringify({
    meta: { ...form.meta, tags: [...(form.meta.tags || [])] },
    body: form.body,
  })
}

function takeSnapshot() {
  savedSnapshot.value = snapshotForm()
  lastSavedAt.value = new Date()
}

function coverImg(relativePath) {
  return baseUrl + String(relativePath).replace(/^\//, '')
}

function confirmIfDirty() {
  if (!isDirty.value) return true
  return window.confirm('当前笔记有未保存的修改，确定继续吗？')
}

const folderHint = computed(() => {
  if (activeCategory.value === '站点文章') return 'Content/ + posts.json'
  if (activeCategory.value === '草稿') return '_drafts'
  if (activeCategory.value === '全部' || activeCategory.value === '未分类') return '{分类}/'
  return activeCategory.value
})

const droppableCategories = computed(() => categories.value)

watch(showCreate, (open) => {
  const dialog = createDialog.value
  if (!dialog) return
  if (open && !dialog.open) dialog.showModal()
  if (!open && dialog.open) dialog.close()
})

watch(() => form.meta.cover, () => {
  coverImgError.value = false
})

let previewTimer = null
watch(
  () => [form.body, form.meta.title, form.meta.excerpt, form.meta.date],
  () => {
    if (!currentRelPath.value || !authed.value) return
    clearTimeout(previewTimer)
    previewTimer = setTimeout(() => runPreview(true), 500)
  },
)

function onKeydown(event) {
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault()
    if (currentRelPath.value && isDirty.value) saveCurrent()
  }
}

async function bootstrapAuth() {
  if (!getNotesAdminToken()) {
    authed.value = false
    return
  }
  try {
    await fetchNotesAdminMe()
    authed.value = true
    await reloadAll()
    fetchCovers()
      .then((res) => {
        coverOptions.value = res.covers || []
      })
      .catch(() => {})
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
    await reloadAll()
    fetchCovers()
      .then((res) => {
        coverOptions.value = res.covers || []
      })
      .catch(() => {})
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
  notes.value = []
  categories.value = []
  currentRelPath.value = ''
  previewHtml.value = ''
  flash('已退出', 'info')
}

onMounted(() => {
  bootstrapAuth()
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  clearTimeout(previewTimer)
})

function statusLabel(status) {
  return (
    {
      draft: '草稿',
      published: '已发布',
      modified: '有改动',
    }[status] || status
  )
}

function flash(text, type = 'info') {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    if (message.value === text) message.value = ''
  }, 3200)
}

async function reloadAll() {
  loadingList.value = true
  try {
    const [{ categories: cats }, { notes: list }, contentStatus] = await Promise.all([
      fetchCategories(),
      fetchNotes(activeCategory.value),
      fetchContentStatus().catch(() => ({ orphans: [] })),
    ])
    categories.value = cats
    notes.value = list
    contentOrphans.value = contentStatus.orphans || []
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    loadingList.value = false
  }
}

async function handleSyncContent() {
  if (syncingContent.value || contentOrphans.value.length === 0) return
  syncingContent.value = true
  try {
    const res = await syncContent()
    const count = res.added?.length || res.count || 0
    flash(count ? `已登记 ${count} 篇文章到 posts.json` : '没有需要同步的文件', count ? 'success' : 'info')
    await reloadAll()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    syncingContent.value = false
  }
}

async function handleAdoptCurrent() {
  if (adopting.value || !currentHtmlFile.value) return
  adopting.value = true
  try {
    const res = await adoptSiteNote(currentHtmlFile.value)
    flash('已转为可编辑笔记', 'success')
    await reloadAll()
    if (res?.relPath) {
      currentRelPath.value = ''
      await openNote(res.relPath)
    }
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    adopting.value = false
  }
}

async function handleAdoptAll() {
  if (adoptingAll.value) return
  if (!window.confirm('将把当前全部「仅站点」文章反解析生成 Markdown 源文件，以便在管理台编辑。是否继续？')) return
  adoptingAll.value = true
  try {
    const res = await adoptAllSiteNotes()
    const count = res?.count || 0
    const failed = res?.errors?.length || 0
    if (!count && !failed) {
      flash('没有需要认领的文章', 'info')
    } else {
      const tail = failed ? ('，' + failed + ' 篇失败') : ''
      flash('已认领 ' + count + ' 篇为可编辑笔记' + tail, failed ? 'info' : 'success')
    }
    await reloadAll()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    adoptingAll.value = false
  }
}

async function selectCategory(name) {
  if (!confirmIfDirty()) return
  activeCategory.value = name
  currentRelPath.value = ''
  currentSiteOnly.value = false
  currentHtmlFile.value = ''
  previewHtml.value = ''
  savedSnapshot.value = ''
  await reloadAll()
}

async function openNote(relPath) {
  if (currentRelPath.value === relPath) return
  if (!confirmIfDirty()) return
  try {
    const data = await fetchNote(relPath)
    currentRelPath.value = data.relPath
    currentSiteOnly.value = !!data.siteOnly
    currentHtmlFile.value = data.htmlFile || ''
    currentStatus.value = data.status
    currentPostId.value = data.postId ?? null
    form.meta = {
      title: data.meta.title || '',
      date: data.meta.date || '',
      category: data.meta.category || '学习',
      excerpt: data.meta.excerpt || '',
      cover: data.meta.cover || '',
      tags: Array.isArray(data.meta.tags) ? [...data.meta.tags] : [],
    }
    form.body = data.body || ''
    previewHtml.value = ''
    coverImgError.value = false
    takeSnapshot()
    await runPreview(true)
  } catch (err) {
    flash(err.message, 'error')
  }
}

async function saveCurrent() {
  if (!currentRelPath.value) return
  saving.value = true
  try {
    const pathBefore = currentRelPath.value
    const res = await saveNote(pathBefore, {
      meta: { ...form.meta, tags: [...(form.meta.tags || [])] },
      body: form.body,
    })
    if (res.relPath && res.relPath !== pathBefore) {
      currentRelPath.value = res.relPath
      flash(`已保存并移动到 笔记/${res.relPath}`, 'success')
    } else {
      flash('已保存 Markdown 源文件', 'success')
    }
    currentStatus.value = res.status
    if (res.postId) currentPostId.value = res.postId
    takeSnapshot()
    await reloadAll()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    saving.value = false
  }
}

async function runPreview(silent = false) {
  if (!currentRelPath.value && !form.body) return
  previewing.value = true
  try {
    const res = await previewNote({
      meta: { ...form.meta, tags: [...(form.meta.tags || [])] },
      body: form.body,
    })
    previewHtml.value = res.html
  } catch (err) {
    if (!silent) flash(err.message, 'error')
  } finally {
    previewing.value = false
  }
}

async function publishCurrent() {
  if (!currentRelPath.value) return
  if (isDirty.value) {
    flash('请先保存修改再发布', 'error')
    return
  }
  publishing.value = true
  try {
    const res = await publishNote(currentRelPath.value)
    currentStatus.value = 'published'
    currentPostId.value = res.post.id
    takeSnapshot()
    try {
      const { reloadPostsCatalog } = await import('../../data/posts.js')
      await reloadPostsCatalog()
    } catch {
      /* ignore */
    }
    flash(
      `已发布 · #${res.post.id} · 打开 /myweb/content/${res.post.id} 并 Ctrl+F5 强制刷新即可看到`,
      'success',
    )
    await reloadAll()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    publishing.value = false
  }
}

function insertMarkdown(before, after = '', placeholder = '') {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = form.body.slice(start, end) || placeholder
  const insertion = before + selected + after
  form.body = form.body.slice(0, start) + insertion + form.body.slice(end)
  nextTick(() => {
    ta.focus()
    const selStart = start + before.length
    const selEnd = selStart + selected.length
    ta.setSelectionRange(selStart, selEnd)
  })
}

function insertLinePrefix(prefix) {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const lineStart = form.body.lastIndexOf('\n', start - 1) + 1
  form.body = form.body.slice(0, lineStart) + prefix + form.body.slice(lineStart)
  nextTick(() => {
    ta.focus()
    ta.setSelectionRange(start + prefix.length, start + prefix.length)
  })
}

function insertCodeBlock() {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = form.body.slice(start, end)
  const block = selected ? `\`\`\`javascript\n${selected}\n\`\`\`` : '```javascript\n\n```'
  form.body = form.body.slice(0, start) + block + form.body.slice(end)
  nextTick(() => ta.focus())
}

function pickNoteImage() {
  imageInputRef.value?.click()
}

function insertAtCursor(text) {
  const ta = textareaRef.value
  if (!ta) {
    form.body = `${form.body}\n${text}\n`
    return
  }
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const padBefore = start > 0 && form.body[start - 1] !== '\n' ? '\n' : ''
  const padAfter = '\n'
  const insertion = padBefore + text + padAfter
  form.body = form.body.slice(0, start) + insertion + form.body.slice(end)
  nextTick(() => {
    ta.focus()
    const pos = start + insertion.length
    ta.setSelectionRange(pos, pos)
  })
}

async function onNoteImageSelected(event) {
  const input = event.target
  const file = input?.files?.[0]
  if (!file) return
  uploadingImage.value = true
  try {
    const data = await uploadNoteImage(file)
    const md = data?.markdown || (data?.url ? `![图片说明](${data.url})` : '')
    if (!md) throw new Error('上传成功但未返回图片地址')
    insertAtCursor(md)
    flash('图片已插入', 'success')
  } catch (err) {
    flash(err.message || '图片上传失败', 'error')
  } finally {
    uploadingImage.value = false
    if (input) input.value = ''
  }
}

function onNoteDragStart(note, event) {
  draggingPath.value = note.relPath
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', note.relPath)
}

function onNoteDragEnd() {
  draggingPath.value = ''
  dropTarget.value = ''
}

function onCategoryDragOver(categoryName) {
  if (categoryName === '全部' || !draggingPath.value) return
  dropTarget.value = categoryName
}

function onCategoryDragLeave(categoryName) {
  if (dropTarget.value === categoryName) dropTarget.value = ''
}

async function onCategoryDrop(categoryName) {
  const relPath = draggingPath.value
  dropTarget.value = ''
  draggingPath.value = ''
  if (!relPath || categoryName === '全部') return

  try {
    const res = await moveNote(relPath, categoryName)
    if (res.moved) {
      if (currentRelPath.value === relPath) {
        currentRelPath.value = res.relPath
      }
      flash(`已移动到 ${categoryName}`, 'success')
      await reloadAll()
      if (currentRelPath.value === res.relPath) {
        await openNote(res.relPath)
      }
    }
  } catch (err) {
    flash(err.message, 'error')
  }
}

async function deleteCurrent() {
  if (!currentRelPath.value) return

  const isPublished = currentStatus.value === 'published' || currentStatus.value === 'modified'
  const msg = isPublished
    ? '该笔记已发布。删除后将同时从 posts.json 与 Content HTML 移除，确定吗？'
    : `确定删除 笔记/${currentRelPath.value} 吗？`

  if (!window.confirm(msg)) return

  deleting.value = true
  try {
    const pathToDelete = currentRelPath.value
    await deleteNote(pathToDelete, { unpublish: isPublished })
    currentRelPath.value = ''
    currentPostId.value = null
    previewHtml.value = ''
    savedSnapshot.value = ''
    flash(isPublished ? '已删除笔记并移出博客' : '已删除笔记', 'success')
    await reloadAll()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    deleting.value = false
  }
}

function closeCreate() {
  showCreate.value = false
}

async function submitCreate() {
  try {
    const asDraft = createForm.asDraft || createForm.category === '_drafts'
    const category = createForm.category === '_drafts' ? '学习' : createForm.category
    const res = await createNote({
      title: createForm.title,
      category,
      excerpt: createForm.excerpt || `${createForm.title} — 学习笔记。`,
      asDraft,
    })
    showCreate.value = false
    createForm.title = ''
    createForm.excerpt = ''
    createForm.asDraft = false
    await reloadAll()
    await openNote(res.relPath)
    flash(`已创建 笔记/${res.relPath}`, 'success')
  } catch (err) {
    flash(err.message, 'error')
  }
}

</script>

<style scoped>
.notes-admin {
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

.admin-brand h1 {
  margin: 0.35rem 0 0;
  font-size: 1.35rem;
}

.admin-brand p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.admin-brand a {
  color: var(--orange);
}

.admin-actions {
  display: flex;
  gap: 0.5rem;
}

.admin-warning {
  margin: 2rem;
  padding: 1rem 1.25rem;
  border: 1px dashed var(--border);
  background: var(--bg-paper);
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

.content-sync-banner {
  margin: 0 1.25rem 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid #e9c46a;
  background: #fff8e7;
  border-radius: 8px;
  font-size: 0.9rem;
}

.content-sync-banner strong {
  margin-right: 0.5rem;
}

.content-sync-banner ul {
  margin: 0.5rem 0 0;
  padding-left: 1.25rem;
  color: var(--text-muted, #666);
}

.site-only-hint {
  margin: 0.35rem 0 0;
  font-size: 0.82rem;
  line-height: 1.45;
  color: var(--text-muted, #666);
}

.site-only-badge {
  background: #457b9d;
}

.site-only-panel {
  padding: 1rem 0 0;
}

.site-only-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem 1rem;
  margin: 0;
}

.site-only-meta div {
  margin: 0;
}

.site-only-meta dt {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted, #666);
  margin-bottom: 0.2rem;
}

.site-only-meta dd {
  margin: 0;
  font-size: 0.88rem;
}

.site-only-meta .span-all {
  grid-column: 1 / -1;
}

.site-only-tag {
  display: inline-block;
  margin-left: 0.35rem;
  padding: 0.05rem 0.35rem;
  border-radius: 4px;
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.04em;
  color: #fff;
  background: #457b9d;
  vertical-align: middle;
}

.admin-shell {
  display: grid;
  grid-template-columns: 200px minmax(220px, 300px) minmax(0, 1fr);
  width: 100%;
  min-height: calc(100vh - 88px);
}

.admin-sidebar,
.admin-list,
.admin-editor {
  border-right: 1px solid var(--border);
  min-height: 100%;
}

.admin-editor {
  border-right: none;
}

.admin-sidebar {
  padding: 1rem 0.75rem;
  background: var(--bg-paper);
}

.admin-sidebar h2,
.list-head h2 {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.category-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.category-list button {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.45rem 0.55rem;
  border: 1px solid transparent;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.category-list li.active button,
.category-list button:hover {
  border-color: var(--border);
  background: var(--orange-light);
}

.count {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.sidebar-foot {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  font-size: 0.78rem;
  color: var(--text-muted);
}

.admin-list {
  padding: 1rem;
  overflow: auto;
}

.list-head {
  display: grid;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.search-input,
.meta-grid input,
.meta-grid select,
textarea,
.create-dialog input,
.create-dialog select {
  width: 100%;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: inherit;
  padding: 0.45rem 0.55rem;
  font: inherit;
}

.note-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.45rem;
}

.sidebar-hint {
  margin: 0 0 0.65rem;
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.category-list li.drop-target button {
  border-color: var(--orange);
  background: var(--orange-light);
  box-shadow: inset 0 0 0 1px var(--orange);
}

.category-list li.dragging,
.note-list li.dragging {
  opacity: 0.55;
}

.note-item {
  width: 100%;
  text-align: left;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  padding: 0.65rem 0.75rem;
  cursor: pointer;
  color: inherit;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.25rem 0.5rem;
}

.note-drag {
  grid-row: span 3;
  align-self: center;
  color: var(--text-muted);
  cursor: grab;
  font-size: 0.9rem;
  user-select: none;
}

.note-list li.active .note-item {
  border-color: var(--orange);
  box-shadow: inset 0 0 0 1px var(--orange);
}

.note-title {
  font-weight: 600;
  grid-column: 2;
}

.note-meta,
.note-item .status {
  grid-column: 2;
}

.note-meta,
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

.status[data-status='modified'] {
  color: var(--orange);
  border-color: #efb38a;
}

.status[data-status='draft'] {
  color: var(--steel);
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

.preview-box :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0.75rem 0;
  border: 1px solid var(--border);
}

.preview-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.preview-head-right {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-shrink: 0;
}

/* 分栏时编辑侧已有切换；预览侧重复的隐藏。纯预览时编辑侧被藏，只留预览侧切换 */
.editor-panels.layout-split .layout-toggle--preview {
  display: none;
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

.build-dialog {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: inherit;
  padding: 0;
  width: min(720px, 92vw);
  max-height: 80vh;
}

.build-dialog-inner {
  padding: 1rem;
  display: grid;
  gap: 0.75rem;
}

.build-log {
  margin: 0;
  max-height: 50vh;
  overflow: auto;
  padding: 0.75rem;
  background: #1a1816;
  color: #eae6e1;
  font-family: var(--mono);
  font-size: 0.72rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
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

.create-dialog {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: inherit;
  padding: 0;
  max-width: 420px;
}

.create-dialog form {
  padding: 1rem;
  display: grid;
  gap: 0.75rem;
}

.create-dialog label {
  display: grid;
  gap: 0.25rem;
}

.create-dialog .checkbox {
  grid-template-columns: auto 1fr;
  align-items: center;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
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

.editor-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.dirty-badge {
  font-size: 0.72rem;
  color: var(--orange);
  border: 1px solid #efb38a;
  padding: 0.1rem 0.4rem;
}

.saved-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.publish-link {
  margin: 0.25rem 0 0;
  font-size: 0.82rem;
}

.publish-link a {
  color: var(--orange);
}

.cover-field {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.cover-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.cover-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.35rem;
}

.cover-option {
  padding: 0;
  border: 2px solid transparent;
  background: none;
  cursor: pointer;
  width: 40px;
  height: 40px;
  overflow: hidden;
}

.cover-option.active {
  border-color: var(--orange);
}

.cover-option img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.md-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  justify-content: space-between;
}

.md-toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.md-btn {
  min-width: 1.75rem;
  padding: 0.2rem 0.4rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  font-family: var(--mono);
  font-size: 0.72rem;
  cursor: pointer;
}

.md-btn:disabled {
  opacity: 0.5;
  cursor: wait;
}

.md-file-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
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

.editor-stats {
  margin: 0.35rem 0 0;
  font-size: 0.72rem;
  color: var(--text-muted);
  font-family: var(--mono);
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

@media (max-width: 1100px) {
  .admin-shell {
    grid-template-columns: 1fr;
  }

  .editor-panels {
    grid-template-columns: 1fr;
  }
}
</style>

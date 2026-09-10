<template>
  <div class="site-pages-admin">
    <header class="page-head">
      <div>
        <h2>页面管理</h2>
        <p class="page-hint">维护个人博客的「关于」和「归档」展示配置。</p>
      </div>
      <div class="head-actions">
        <button type="button" class="platform-btn-ghost" :disabled="loading" @click="load">
          {{ loading ? '加载中…' : '重新加载' }}
        </button>
        <button type="button" class="platform-btn-primary" :disabled="saving" @click="saveActive">
          {{ saving ? '保存中…' : '保存当前页' }}
        </button>
      </div>
    </header>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <p v-if="message" class="toast" :data-type="messageType">{{ message }}</p>

    <section v-if="activeTab === 'about'" class="platform-panel form-panel">
      <div class="form-grid">
        <label>昵称
          <input v-model="about.name" type="text" />
        </label>
        <label>Tagline
          <input v-model="about.tagline" type="text" />
        </label>
        <label>头像路径
          <input v-model="about.avatar" type="text" />
        </label>
        <label>主图路径
          <input v-model="about.heroImage" type="text" />
        </label>
        <label>ACG 标签（用 / 分隔）
          <input v-model="aboutTagsText" type="text" />
        </label>
        <label>技术栈（用 / 分隔）
          <input v-model="aboutSkillsText" type="text" />
        </label>
      </div>

      <label>首屏简介
        <textarea v-model="about.lead" rows="3" />
      </label>
      <label>我是谁（空行分段）
        <textarea v-model="aboutIntroText" rows="5" />
      </label>
      <label>引用语
        <input v-model="about.quote" type="text" />
      </label>

      <h3>联系方式</h3>
      <div class="form-grid">
        <label>邮箱
          <input v-model="about.contacts.email" type="email" />
        </label>
        <label>博客
          <input v-model="about.contacts.blog" type="url" />
        </label>
        <label>GitHub
          <input v-model="about.contacts.github" type="url" />
        </label>
        <label>音乐室路径
          <input v-model="about.contacts.musicPath" type="text" />
        </label>
      </div>

      <h3>现在在做什么</h3>
      <div v-for="(item, index) in about.favorites" :key="index" class="favorite-row">
        <input v-model="item.label" type="text" placeholder="标签" />
        <input v-model="item.text" type="text" placeholder="内容" />
        <button type="button" class="platform-btn-ghost" @click="removeFavorite(index)">删除</button>
      </div>
      <button type="button" class="platform-btn-ghost" @click="addFavorite">+ 添加一条</button>

      <h3>贴纸墙 <small>{{ about.stickers.length }} 张</small></h3>
      <div class="sticker-toolbar">
        <button
          type="button"
          class="platform-btn-primary"
          :disabled="uploadingSticker"
          @click="stickerFileInput?.click()"
        >
          {{ uploadingSticker ? '上传中…' : '上传贴纸' }}
        </button>
        <select v-model="selectedLibraryPath" class="library-select">
          <option value="">从现有贴纸库选择…</option>
          <option v-for="item in availableStickers" :key="item.path" :value="item.path">
            {{ item.label }} · {{ item.path }}
          </option>
        </select>
        <button
          type="button"
          class="platform-btn-ghost"
          :disabled="!selectedLibraryPath"
          @click="addLibrarySticker"
        >
          从贴纸库添加
        </button>
        <input ref="stickerFileInput" type="file" accept="image/*" hidden @change="onStickerFile" />
      </div>

      <div v-for="(item, index) in about.stickers" :key="`${item.path}-${index}`" class="sticker-row">
        <img :src="resolvePublicUrl(item.path)" alt="" />
        <div class="sticker-fields">
          <input v-model="item.path" type="text" placeholder="图片路径或 URL" />
          <input v-model="item.label" type="text" placeholder="标签" />
        </div>
        <div class="sticker-ops">
          <button type="button" class="platform-btn-ghost" :disabled="index === 0" @click="moveSticker(index, -1)">↑</button>
          <button type="button" class="platform-btn-ghost" :disabled="index === about.stickers.length - 1" @click="moveSticker(index, 1)">↓</button>
          <button type="button" class="platform-btn-ghost danger" @click="removeSticker(index)">删除</button>
        </div>
      </div>
    </section>

    <section v-else class="platform-panel form-panel">
      <div class="form-grid">
        <label>标题
          <input v-model="archive.title" type="text" />
        </label>
        <label>文章展示数量（0 表示全部）
          <input v-model.number="archive.postLimit" type="number" min="0" />
        </label>
      </div>
      <label>描述
        <textarea v-model="archive.description" rows="3" />
      </label>
      <div class="switch-row">
        <label>
          <input v-model="archive.showStats" type="checkbox" />
          显示统计信息
        </label>
        <label>
          <input v-model="archive.showCategoryPanel" type="checkbox" />
          显示分类侧栏
        </label>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { aboutGallery } from '../../data/aboutGallery'
import { resolvePublicUrl } from '../../api/platform.js'
import {
  cloneSitePageContent,
  defaultAboutContent,
  defaultArchiveContent,
} from '../../data/sitePageDefaults'
import { fetchSitePage, saveSitePage } from '../../api/sitePages'
import { uploadNoteImage } from '../../api/notesAdmin'

const tabs = [
  { key: 'about', label: '关于' },
  { key: 'archive', label: '归档' },
]

const activeTab = ref('about')
const loading = ref(false)
const saving = ref(false)
const uploadingSticker = ref(false)
const message = ref('')
const messageType = ref('ok')
const selectedLibraryPath = ref('')
const stickerFileInput = ref(null)

const about = reactive(cloneSitePageContent(defaultAboutContent))
const archive = reactive(cloneSitePageContent(defaultArchiveContent))

const aboutTagsText = computed({
  get: () => about.acgTags.join(' / '),
  set: (value) => {
    about.acgTags = value.split('/').map((item) => item.trim()).filter(Boolean)
  },
})

const aboutSkillsText = computed({
  get: () => about.skills.join(' / '),
  set: (value) => {
    about.skills = value.split('/').map((item) => item.trim()).filter(Boolean)
  },
})

const aboutIntroText = computed({
  get: () => about.whoIAm.join('\n\n'),
  set: (value) => {
    about.whoIAm = value.split(/\n{2,}/).map((item) => item.trim()).filter(Boolean)
  },
})

const availableStickers = computed(() => {
  const selected = new Set(about.stickers.map((item) => item.path))
  return aboutGallery.filter((item) => !selected.has(item.path))
})

function notify(text, type = 'ok') {
  message.value = text
  messageType.value = type
}

async function load() {
  loading.value = true
  message.value = ''
  try {
    const [aboutResult, archiveResult] = await Promise.allSettled([
      fetchSitePage('about'),
      fetchSitePage('archive'),
    ])
    if (aboutResult.status === 'fulfilled' && aboutResult.value?.content) {
      Object.assign(about, cloneSitePageContent(defaultAboutContent), aboutResult.value.content)
    }
    if (archiveResult.status === 'fulfilled' && archiveResult.value?.content) {
      Object.assign(archive, cloneSitePageContent(defaultArchiveContent), archiveResult.value.content)
    }
    const failed = [aboutResult, archiveResult].some((item) => item.status === 'rejected')
    notify(failed ? '部分配置加载失败，已显示默认值' : '配置已加载')
  } finally {
    loading.value = false
  }
}

function addFavorite() {
  about.favorites.push({ label: '', text: '' })
}

function removeFavorite(index) {
  about.favorites.splice(index, 1)
}

function nextStickerLabel() {
  return String(about.stickers.length + 1).padStart(2, '0')
}

function stickerLabelFromFileName(fileName = '') {
  const label = String(fileName).replace(/\.[^.]+$/, '').trim()
  return label || nextStickerLabel()
}

function addSticker(path, label = '') {
  if (!path.trim()) return false
  about.stickers.push({ path: path.trim(), label: label.trim() || nextStickerLabel() })
  return true
}

function addLibrarySticker() {
  const item = aboutGallery.find((gallery) => gallery.path === selectedLibraryPath.value)
  if (item && addSticker(item.path, item.label)) selectedLibraryPath.value = ''
}

function moveSticker(index, direction) {
  const target = index + direction
  if (target < 0 || target >= about.stickers.length) return
  const [item] = about.stickers.splice(index, 1)
  about.stickers.splice(target, 0, item)
}

function removeSticker(index) {
  about.stickers.splice(index, 1)
}

async function onStickerFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploadingSticker.value = true
  try {
    const data = await uploadNoteImage(file)
    if (addSticker(data.url, stickerLabelFromFileName(file.name))) notify('贴纸已上传')
  } catch (err) {
    notify(err.message || '贴纸上传失败', 'error')
  } finally {
    uploadingSticker.value = false
    event.target.value = ''
  }
}

async function saveActive() {
  saving.value = true
  try {
    const content = activeTab.value === 'about'
      ? cloneSitePageContent(about)
      : cloneSitePageContent(archive)
    await saveSitePage(activeTab.value, content)
    notify(`${activeTab.value === 'about' ? '关于' : '归档'}配置已保存`)
  } catch (err) {
    notify(err.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.site-pages-admin { display: flex; flex-direction: column; gap: 1rem; }
.page-head { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; }
.page-head h2 { margin: 0 0 0.3rem; }
.page-hint { margin: 0; color: var(--text-muted); font-size: 0.9rem; }
.head-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }
.tabs { display: flex; gap: 0.5rem; }
.tab { border: 1px solid var(--border); background: var(--bg); color: var(--text); padding: 0.5rem 1rem; border-radius: 999px; cursor: pointer; }
.tab.active { border-color: var(--primary-color); color: var(--primary-color); font-weight: 600; }
.form-panel { display: flex; flex-direction: column; gap: 1rem; }
.form-panel h3 { margin: 0.4rem 0 0; font-size: 1rem; }
.form-panel h3 small { color: var(--text-muted); }
.form-panel label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.88rem; color: var(--text-muted); }
.form-panel input, .form-panel textarea, .form-panel select {
  border: 1px solid var(--border); border-radius: 10px; background: var(--bg); color: var(--text); padding: 0.55rem 0.7rem; font: inherit;
}
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.9rem; }
.favorite-row { display: grid; grid-template-columns: 160px 1fr 74px; gap: 0.6rem; align-items: center; }
.favorite-row input { width: 100%; }
.sticker-toolbar { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.library-select { min-width: min(320px, 100%); }
.sticker-toolbar > .platform-btn-primary { min-width: 118px; }
.sticker-row { display: grid; grid-template-columns: 72px minmax(0, 1fr) auto; gap: 0.7rem; align-items: center; padding: 0.55rem; border: 1px solid var(--border); border-radius: 12px; }
.sticker-row img { width: 72px; height: 48px; object-fit: cover; border-radius: 8px; background: var(--bg-muted); }
.sticker-fields { display: grid; grid-template-columns: minmax(0, 2fr) 90px; gap: 0.5rem; }
.sticker-ops { display: flex; gap: 0.3rem; }
.switch-row { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.switch-row label { flex-direction: row; align-items: center; color: var(--text); }
.danger { color: #d64545; }
.toast { margin: 0; font-size: 0.88rem; }
.toast[data-type='error'] { color: #d64545; }

@media (max-width: 760px) {
  .page-head, .head-actions { flex-direction: column; align-items: stretch; }
  .form-grid, .favorite-row, .sticker-row { grid-template-columns: 1fr; }
  .sticker-fields { grid-template-columns: 1fr; }
  .sticker-toolbar { flex-direction: column; align-items: stretch; }
  .library-select, .sticker-toolbar > .platform-btn-primary { width: 100%; }
}
</style>

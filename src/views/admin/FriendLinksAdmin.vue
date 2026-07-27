<template>
  <div class="fl-admin">
    <header class="fl-head">
      <div>
        <h2>友链管理</h2>
        <p class="fl-hint">收录朋友的博客、B 站视频等外部链接，前台「友链」页展示。</p>
      </div>
      <button type="button" class="platform-btn-primary" @click="openCreate">+ 新增友链</button>
    </header>

    <div class="fl-toolbar">
      <input
        v-model="search"
        type="search"
        class="fl-search"
        placeholder="搜索名称 / 链接 / 描述…"
        @keyup.enter="reload"
      />
      <select v-model="categoryFilter" class="fl-cat-select" @change="onCategoryChange">
        <option value="">全部分类</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <button type="button" class="platform-btn-ghost" @click="reload">搜索</button>
      <span class="fl-count">共 {{ total }} 条</span>
    </div>

    <p v-if="message" class="toast" :data-type="messageType">{{ message }}</p>

    <div class="platform-panel fl-table-wrap">
      <table class="fl-table">
        <thead>
          <tr>
            <th style="width:64px">图片</th>
            <th style="width:16%">名称</th>
            <th>链接</th>
            <th style="width:12%">分类</th>
            <th style="width:8%">排序</th>
            <th style="width:12%">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="fl-empty">加载中…</td></tr>
          <tr v-else-if="!links.length"><td colspan="6" class="fl-empty">暂无友链，点击右上角「新增友链」。</td></tr>
          <tr v-for="x in links" :key="x.id">
            <td>
              <img v-if="x.image_url" :src="x.image_url" alt="" class="fl-thumb" />
              <span v-else class="fl-thumb fl-thumb--empty">—</span>
            </td>
            <td class="fl-name">{{ x.name }}</td>
            <td class="fl-url"><a :href="x.url" target="_blank" rel="noopener">{{ x.url }}</a></td>
            <td>{{ x.category || '—' }}</td>
            <td>{{ x.sort_order }}</td>
            <td class="fl-ops">
              <button type="button" class="fl-link" @click="openEdit(x)">编辑</button>
              <button type="button" class="fl-link fl-del" @click="remove(x)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="fl-pager" v-if="total > pageSize">
      <button type="button" class="platform-btn-ghost" :disabled="page <= 1" @click="go(page - 1)">上一页</button>
      <span>第 {{ page }} / {{ totalPages }} 页</span>
      <button type="button" class="platform-btn-ghost" :disabled="page >= totalPages" @click="go(page + 1)">下一页</button>
    </div>

    <div v-if="showForm" class="fl-drawer-scrim" @click.self="closeForm">
      <div class="platform-panel fl-drawer">
        <h3>{{ editing ? '编辑友链' : '新增友链' }}</h3>
        <label>名称 *
          <input v-model="form.name" type="text" placeholder="如 某某的博客" />
        </label>
        <label>链接 *
          <input v-model="form.url" type="url" placeholder="https://…" />
        </label>
        <label>分类
          <input v-model="form.category" type="text" placeholder="如 个人博客 / B站视频" />
        </label>
        <label>排序（数字越小越靠前）
          <input v-model.number="form.sort_order" type="number" placeholder="0" />
        </label>
        <label>图片
          <div class="fl-img-row">
            <input v-model="form.image_url" type="text" placeholder="图片 URL，或点右侧上传" />
            <button type="button" class="platform-btn-ghost" :disabled="uploading" @click="pickImage">
              {{ uploading ? '上传中…' : '上传' }}
            </button>
            <input ref="fileInput" type="file" accept="image/*" hidden @change="onFile" />
          </div>
          <img v-if="form.image_url" :src="form.image_url" alt="" class="fl-preview" />
        </label>
        <label>描述
          <textarea v-model="form.description" rows="3" placeholder="一句话介绍这个链接"></textarea>
        </label>
        <div class="fl-drawer-foot">
          <button type="button" class="platform-btn-ghost" @click="closeForm">取消</button>
          <button type="button" class="platform-btn-primary" :disabled="saving" @click="submit">
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  fetchFriendLinksAdmin,
  fetchFriendLinkCategories,
  createFriendLink,
  updateFriendLink,
  deleteFriendLink,
} from '../../api/friendLinks'
import { uploadNoteImage } from '../../api/notesAdmin'

const links = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const categoryFilter = ref('')
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const showForm = ref(false)
const editing = ref(null)
const message = ref('')
const messageType = ref('info')
const fileInput = ref(null)

const form = reactive({ name: '', url: '', image_url: '', description: '', category: '', sort_order: 0 })
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

function flash(text, type = 'info') {
  message.value = text
  messageType.value = type
  setTimeout(() => { if (message.value === text) message.value = '' }, 3200)
}

async function reload() {
  loading.value = true
  try {
    const data = await fetchFriendLinksAdmin({ q: search.value.trim(), category: categoryFilter.value, page: page.value, pageSize: pageSize.value })
    links.value = data.links || []
    total.value = data.total || 0
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const data = await fetchFriendLinkCategories()
    categories.value = data.categories || []
  } catch { /* ignore */ }
}

function onCategoryChange() {
  page.value = 1
  reload()
}

function go(p) {
  page.value = p
  reload()
}

function openCreate() {
  editing.value = null
  form.name = ''; form.url = ''; form.image_url = ''; form.description = ''; form.category = ''; form.sort_order = 0
  showForm.value = true
}

function openEdit(x) {
  editing.value = x
  form.name = x.name; form.url = x.url; form.image_url = x.image_url || ''
  form.description = x.description || ''; form.category = x.category || ''; form.sort_order = x.sort_order || 0
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
}

function pickImage() {
  if (fileInput.value) fileInput.value.click()
}

async function onFile(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  uploading.value = true
  try {
    const data = await uploadNoteImage(file)
    form.image_url = data.url || form.image_url
    flash('图片已上传', 'success')
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function submit() {
  if (!form.name.trim() || !form.url.trim()) {
    flash('名称和链接不能为空', 'error')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name.trim(),
      url: form.url.trim(),
      image_url: form.image_url.trim(),
      description: form.description.trim(),
      category: form.category.trim(),
      sort_order: Number(form.sort_order) || 0,
    }
    if (editing.value) {
      await updateFriendLink(editing.value.id, payload)
      flash('已保存', 'success')
    } else {
      await createFriendLink(payload)
      flash('已新增', 'success')
    }
    closeForm()
    await reload()
    await loadCategories()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    saving.value = false
  }
}

async function remove(x) {
  if (!window.confirm(`确认删除友链「${x.name}」？`)) return
  try {
    await deleteFriendLink(x.id)
    flash('已删除', 'success')
    if (links.value.length === 1 && page.value > 1) page.value -= 1
    await reload()
  } catch (err) {
    flash(err.message, 'error')
  }
}

onMounted(() => { reload(); loadCategories() })
</script>

<style scoped>
.fl-admin { display: flex; flex-direction: column; gap: 1rem; }
.fl-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.fl-head h2 { margin: 0; font-size: 1.15rem; }
.fl-hint { margin: 0.35rem 0 0; font-size: 0.8rem; color: var(--text-muted); }
.fl-toolbar { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.fl-search {
  flex: 1; min-width: 200px; padding: 0.5rem 0.75rem;
  border: 1px solid var(--border); border-radius: 8px; background: var(--bg-paper); color: var(--text);
}
.fl-cat-select {
  padding: 0.5rem 0.7rem; border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg-paper); color: var(--text); font-size: 0.85rem; font-family: inherit; cursor: pointer;
}
.fl-count { font-size: 0.8rem; color: var(--text-muted); margin-left: auto; }
.fl-table-wrap { padding: 0; overflow-x: auto; }
.fl-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.fl-table th, .fl-table td { padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid var(--border); vertical-align: middle; }
.fl-table th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); }
.fl-thumb { width: 44px; height: 44px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border); display: block; }
.fl-thumb--empty { display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
.fl-name { font-weight: 600; }
.fl-url a { color: var(--orange); word-break: break-all; text-decoration: none; }
.fl-url a:hover { text-decoration: underline; }
.fl-empty { text-align: center; color: var(--text-muted); padding: 2rem 0; }
.fl-ops { white-space: nowrap; }
.fl-link { background: none; border: none; cursor: pointer; color: var(--orange); font-size: 0.8rem; padding: 0 0.35rem; }
.fl-link.fl-del { color: #d9534f; }
.fl-pager { display: flex; align-items: center; justify-content: center; gap: 1rem; font-size: 0.85rem; color: var(--text-muted); }
.fl-drawer-scrim { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; justify-content: center; align-items: flex-start; z-index: 200; padding: 4vh 1rem; }
.fl-drawer { width: min(560px, 100%); display: flex; flex-direction: column; gap: 0.85rem; max-height: 92vh; overflow-y: auto; }
.fl-drawer h3 { margin: 0; }
.fl-drawer label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.8rem; color: var(--text-muted); }
.fl-drawer input, .fl-drawer textarea {
  padding: 0.5rem 0.7rem; border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg-paper); color: var(--text); font-size: 0.9rem; font-family: inherit;
}
.fl-img-row { display: flex; gap: 0.5rem; align-items: center; }
.fl-img-row input[type="text"] { flex: 1; }
.fl-preview { margin-top: 0.5rem; max-width: 160px; max-height: 100px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border); }
.fl-drawer-foot { display: flex; justify-content: flex-end; gap: 0.6rem; margin-top: 0.5rem; }
</style>
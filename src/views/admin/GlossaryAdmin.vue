<template>
  <div class="glossary-admin">
    <header class="ga-head">
      <div>
        <h2>术语库</h2>
        <p class="ga-hint">录入专有名词与解释，笔记正文中会自动高亮并悬停显示释义。</p>
      </div>
      <button type="button" class="platform-btn-primary" @click="openCreate">+ 新增术语</button>
    </header>

    <div class="ga-toolbar">
      <input
        v-model="search"
        type="search"
        class="ga-search"
        placeholder="搜索术语 / 别名 / 释义…"
        @keyup.enter="reload"
      />
      <button type="button" class="platform-btn-ghost" @click="reload">搜索</button>
      <span class="ga-count">共 {{ total }} 条</span>
    </div>

    <p v-if="message" class="toast" :data-type="messageType">{{ message }}</p>

    <div class="platform-panel ga-table-wrap">
      <table class="ga-table">
        <thead>
          <tr>
            <th style="width:18%">术语</th>
            <th style="width:18%">别名</th>
            <th>释义</th>
            <th style="width:10%">分类</th>
            <th style="width:12%">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="5" class="ga-empty">加载中…</td></tr>
          <tr v-else-if="!terms.length"><td colspan="5" class="ga-empty">暂无术语，点击右上角「新增术语」。</td></tr>
          <tr v-for="t in terms" :key="t.id">
            <td class="ga-term">{{ t.term }}</td>
            <td class="ga-alias">{{ t.aliases || '—' }}</td>
            <td class="ga-def">{{ t.definition }}</td>
            <td>{{ t.category || '—' }}</td>
            <td class="ga-ops">
              <button type="button" class="ga-link" @click="openEdit(t)">编辑</button>
              <button type="button" class="ga-link ga-del" @click="remove(t)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="ga-pager" v-if="total > pageSize">
      <button type="button" class="platform-btn-ghost" :disabled="page <= 1" @click="go(page - 1)">上一页</button>
      <span>第 {{ page }} / {{ totalPages }} 页</span>
      <button type="button" class="platform-btn-ghost" :disabled="page >= totalPages" @click="go(page + 1)">下一页</button>
    </div>

    <div v-if="showForm" class="ga-drawer-scrim" @click.self="closeForm">
      <div class="platform-panel ga-drawer">
        <h3>{{ editing ? '编辑术语' : '新增术语' }}</h3>
        <label>术语名 *
          <input v-model="form.term" type="text" placeholder="如 DNS 解析" />
        </label>
        <label>别名（英文缩写大小写不敏感，逗号分隔）
          <input v-model="form.aliases" type="text" placeholder="如 DNS,域名系统" />
        </label>
        <label>分类
          <input v-model="form.category" type="text" placeholder="如 网络 / 部署" />
        </label>
        <label>释义 *
          <textarea v-model="form.definition" rows="4" placeholder="把域名翻译成 IP 地址的过程…"></textarea>
        </label>
        <div class="ga-drawer-foot">
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
  fetchGlossaryAdmin,
  createGlossaryTerm,
  updateGlossaryTerm,
  deleteGlossaryTerm,
} from '../../api/glossary'

const terms = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)
const editing = ref(null)
const message = ref('')
const messageType = ref('info')

const form = reactive({ term: '', aliases: '', category: '', definition: '' })
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

function flash(text, type = 'info') {
  message.value = text
  messageType.value = type
  setTimeout(() => { if (message.value === text) message.value = '' }, 3200)
}

async function reload() {
  loading.value = true
  try {
    const data = await fetchGlossaryAdmin({ q: search.value.trim(), page: page.value, pageSize: pageSize.value })
    terms.value = data.terms || []
    total.value = data.total || 0
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    loading.value = false
  }
}

function go(p) {
  page.value = p
  reload()
}

function openCreate() {
  editing.value = null
  form.term = ''; form.aliases = ''; form.category = ''; form.definition = ''
  showForm.value = true
}

function openEdit(t) {
  editing.value = t
  form.term = t.term; form.aliases = t.aliases || ''; form.category = t.category || ''; form.definition = t.definition
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
}

async function submit() {
  if (!form.term.trim() || !form.definition.trim()) {
    flash('术语名和释义不能为空', 'error')
    return
  }
  saving.value = true
  try {
    const payload = {
      term: form.term.trim(),
      aliases: form.aliases.trim(),
      category: form.category.trim(),
      definition: form.definition.trim(),
    }
    if (editing.value) {
      await updateGlossaryTerm(editing.value.id, payload)
      flash('已保存', 'success')
    } else {
      await createGlossaryTerm(payload)
      flash('已新增', 'success')
    }
    closeForm()
    await reload()
  } catch (err) {
    flash(err.message, 'error')
  } finally {
    saving.value = false
  }
}

async function remove(t) {
  if (!window.confirm(`确认删除术语「${t.term}」？`)) return
  try {
    await deleteGlossaryTerm(t.id)
    flash('已删除', 'success')
    if (terms.value.length === 1 && page.value > 1) page.value -= 1
    await reload()
  } catch (err) {
    flash(err.message, 'error')
  }
}

onMounted(reload)
</script>

<style scoped>
.glossary-admin { display: flex; flex-direction: column; gap: 1rem; }
.ga-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.ga-head h2 { margin: 0; font-size: 1.15rem; }
.ga-hint { margin: 0.35rem 0 0; font-size: 0.8rem; color: var(--text-muted); }
.ga-toolbar { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.ga-search {
  flex: 1; min-width: 200px; padding: 0.5rem 0.75rem;
  border: 1px solid var(--border); border-radius: 8px; background: var(--bg-paper); color: var(--text);
}
.ga-count { font-size: 0.8rem; color: var(--text-muted); margin-left: auto; }
.ga-table-wrap { padding: 0; overflow-x: auto; }
.ga-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.ga-table th, .ga-table td { padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }
.ga-table th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); }
.ga-term { font-weight: 600; }
.ga-alias { color: var(--text-muted); }
.ga-def { color: var(--text); line-height: 1.5; white-space: pre-wrap; }
.ga-empty { text-align: center; color: var(--text-muted); padding: 2rem 0; }
.ga-ops { white-space: nowrap; }
.ga-link { background: none; border: none; cursor: pointer; color: var(--orange); font-size: 0.8rem; padding: 0 0.35rem; }
.ga-link.ga-del { color: #d9534f; }
.ga-pager { display: flex; align-items: center; justify-content: center; gap: 1rem; font-size: 0.85rem; color: var(--text-muted); }
.ga-drawer-scrim { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; justify-content: center; align-items: flex-start; z-index: 200; padding: 4vh 1rem; }
.ga-drawer { width: min(560px, 100%); display: flex; flex-direction: column; gap: 0.85rem; max-height: 92vh; overflow-y: auto; }
.ga-drawer h3 { margin: 0; }
.ga-drawer label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.8rem; color: var(--text-muted); }
.ga-drawer input, .ga-drawer textarea {
  padding: 0.5rem 0.7rem; border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg-paper); color: var(--text); font-size: 0.9rem; font-family: inherit;
}
.ga-drawer-foot { display: flex; justify-content: flex-end; gap: 0.6rem; margin-top: 0.5rem; }
</style>
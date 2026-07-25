<template>
  <div class="admin-table">
    <!-- 顶部工具栏 -->
    <div class="table-toolbar platform-panel">
      <div class="toolbar-left">
        <input
          v-model="searchInput"
          type="search"
          class="table-search"
          :placeholder="`搜索 ${searchHint}...`"
          @keyup.enter="applySearch"
        />
        <button type="button" class="platform-btn-ghost" @click="applySearch">搜索</button>
        <button v-if="searchQuery" type="button" class="platform-btn-ghost" @click="clearSearch">清除</button>
      </div>
      <div class="toolbar-right">
        <span v-if="selectedIds.length" class="selected-hint">已选 {{ selectedIds.length }} 项</span>
        <button
          type="button"
          class="platform-btn-ghost danger"
          :disabled="!selectedIds.length || busy"
          @click="confirmBulkDelete"
        >
          批量删除
        </button>
        <button type="button" class="platform-btn-ghost" :disabled="busy" @click="reload">刷新</button>
      </div>
    </div>

    <!-- 表格本体 -->
    <div class="table-wrap platform-panel">
      <div v-if="error" class="toast" data-type="error">{{ error }}</div>

      <div class="table-scroll">
        <table class="grid">
          <thead>
            <tr>
              <th class="col-check">
                <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" />
              </th>
              <th
                v-for="col in columns"
                :key="col.field"
                :class="{ sortable: col.sortable !== false, active: sortField === col.field }"
                @click="col.sortable !== false && toggleSort(col.field)"
              >
                {{ col.label }}
                <span v-if="col.sortable !== false && sortField === col.field" class="sort-arrow">
                  {{ sortAsc ? '▲' : '▼' }}
                </span>
              </th>
              <th class="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="columns.length + 2" class="empty">加载中…</td>
            </tr>
            <tr v-else-if="!items.length">
              <td :colspan="columns.length + 2" class="empty">暂无数据</td>
            </tr>
            <tr v-for="row in items" v-else :key="row.id">
              <td class="col-check">
                <input type="checkbox" :value="row.id" v-model="selectedIds" />
              </td>
              <td v-for="col in columns" :key="col.field" :class="col.class">
                <span :title="formatValue(row, col)">{{ formatValue(row, col) }}</span>
              </td>
              <td class="col-actions">
                <button type="button" class="row-btn" @click="startEdit(row)">编辑</button>
                <button type="button" class="row-btn danger" @click="confirmDelete(row)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="table-pager">
        <span>共 {{ total }} 条 · 第 {{ page }} / {{ totalPages }} 页</span>
        <div class="pager-actions">
          <label>
            每页
            <select v-model.number="pageSize" @change="reload">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </label>
          <button type="button" class="platform-btn-ghost" :disabled="page <= 1" @click="goto(page - 1)">上一页</button>
          <button type="button" class="platform-btn-ghost" :disabled="page >= totalPages" @click="goto(page + 1)">
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑抽屉 -->
    <div v-if="editing" class="drawer-mask" @click.self="cancelEdit">
      <div class="drawer platform-panel">
        <header class="drawer-head">
          <h3>编辑 #{{ editing.id }}</h3>
          <button type="button" class="platform-btn-ghost" @click="cancelEdit">关闭</button>
        </header>
        <form class="drawer-body" @submit.prevent="submitEdit">
          <label v-for="field in editableFields" :key="field" class="field">
            <span>{{ fieldLabel(field) }}</span>
            <textarea
              v-if="fieldKind(field) === 'textarea'"
              v-model="editForm[field]"
              rows="6"
            />
            <input
              v-else-if="fieldKind(field) === 'boolean'"
              v-model="editForm[field]"
              type="checkbox"
            />
            <input
              v-else-if="fieldKind(field) === 'number'"
              v-model.number="editForm[field]"
              type="number"
            />
            <input
              v-else-if="fieldKind(field) === 'date'"
              v-model="editForm[field]"
              type="date"
            />
            <input v-else v-model="editForm[field]" type="text" />
          </label>
          <div v-if="editError" class="toast" data-type="error">{{ editError }}</div>
          <div class="drawer-actions">
            <button type="button" class="platform-btn-ghost" @click="cancelEdit">取消</button>
            <button type="submit" class="platform-btn-primary" :disabled="savingEdit">
              {{ savingEdit ? '保存中…' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认 -->
    <div v-if="deleteTarget" class="drawer-mask" @click.self="deleteTarget = null">
      <div class="confirm platform-panel">
        <h3>确认删除</h3>
        <p>{{ deleteTargetHint }}</p>
        <div v-if="deleteError" class="toast" data-type="error">{{ deleteError }}</div>
        <div class="drawer-actions">
          <button type="button" class="platform-btn-ghost" @click="deleteTarget = null">取消</button>
          <button type="button" class="platform-btn-primary danger" :disabled="deleting" @click="performDelete">
            {{ deleting ? '删除中…' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import {
  bulkDeleteResource,
  deleteResource,
  listResource,
  updateResource,
} from '../../api/adminCrud.js'

const props = defineProps({
  resource: { type: String, required: true },
  columns: { type: Array, required: true },
  /** 覆盖后端默认；不传则使用后端返回的 editable */
  editableFieldsOverride: { type: Array, default: null },
  defaultSort: { type: String, default: '-id' },
  /** 每个字段的编辑控件类型：text / textarea / number / boolean / date */
  fieldTypes: { type: Object, default: () => ({}) },
})

const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const busy = ref(false)
const error = ref('')

const sortField = ref('id')
const sortAsc = ref(false)

const searchInput = ref('')
const searchQuery = ref('')

const selectedIds = ref([])

const editing = ref(null)
const editForm = reactive({})
const savingEdit = ref(false)
const editError = ref('')
const backendEditable = ref([])

const deleteTarget = ref(null)
const deleteError = ref('')
const deleting = ref(false)

const searchHint = computed(() => {
  const first = props.columns.find((c) => c.searchable)
  return first ? first.label : '关键字'
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const allSelected = computed(() => items.value.length > 0 && selectedIds.value.length === items.value.length)

const editableFields = computed(() => props.editableFieldsOverride || backendEditable.value)

function fieldLabel(field) {
  const col = props.columns.find((c) => c.field === field)
  return col ? col.label : field
}
function fieldKind(field) {
  return props.fieldTypes[field] || 'text'
}

function formatValue(row, col) {
  const raw = row[col.field]
  if (raw === null || raw === undefined) return ''
  if (typeof col.format === 'function') return col.format(raw, row)
  if (typeof raw === 'boolean') return raw ? '是' : '否'
  if (typeof raw === 'string' && raw.length > 80) return raw.slice(0, 80) + '…'
  return String(raw)
}

async function reload() {
  loading.value = true
  error.value = ''
  try {
    const sort = (sortAsc.value ? '' : '-') + sortField.value
    const data = await listResource(props.resource, {
      page: page.value,
      pageSize: pageSize.value,
      q: searchQuery.value,
      sort,
    })
    items.value = data.items || []
    total.value = data.total || 0
    backendEditable.value = data.editable || []
    selectedIds.value = selectedIds.value.filter((id) => items.value.some((r) => r.id === id))
  } catch (err) {
    error.value = err.message || '加载失败'
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function toggleSort(field) {
  if (sortField.value === field) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = field
    sortAsc.value = true
  }
  page.value = 1
  reload()
}

function applySearch() {
  searchQuery.value = searchInput.value.trim()
  page.value = 1
  reload()
}
function clearSearch() {
  searchInput.value = ''
  searchQuery.value = ''
  page.value = 1
  reload()
}

function goto(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  reload()
}

function toggleSelectAll(e) {
  if (e.target.checked) selectedIds.value = items.value.map((r) => r.id)
  else selectedIds.value = []
}

function startEdit(row) {
  editError.value = ''
  editing.value = row
  const fields = editableFields.value
  Object.keys(editForm).forEach((k) => delete editForm[k])
  fields.forEach((f) => {
    let value = row[f]
    if (fieldKind(f) === 'date' && typeof value === 'string') {
      value = value.slice(0, 10)
    }
    editForm[f] = value ?? (fieldKind(f) === 'boolean' ? false : '')
  })
}
function cancelEdit() {
  editing.value = null
}

async function submitEdit() {
  if (!editing.value) return
  savingEdit.value = true
  editError.value = ''
  try {
    const payload = {}
    editableFields.value.forEach((f) => {
      payload[f] = editForm[f]
    })
    await updateResource(props.resource, editing.value.id, payload)
    editing.value = null
    await reload()
  } catch (err) {
    editError.value = err.message || '保存失败'
  } finally {
    savingEdit.value = false
  }
}

function confirmDelete(row) {
  deleteError.value = ''
  deleteTarget.value = { kind: 'single', row }
}
function confirmBulkDelete() {
  if (!selectedIds.value.length) return
  deleteError.value = ''
  deleteTarget.value = { kind: 'bulk', ids: [...selectedIds.value] }
}

const deleteTargetHint = computed(() => {
  if (!deleteTarget.value) return ''
  if (deleteTarget.value.kind === 'single') {
    const row = deleteTarget.value.row
    return `确定要删除 #${row.id} 吗？此操作不可撤销。`
  }
  return `确定要删除已选的 ${deleteTarget.value.ids.length} 条记录吗？此操作不可撤销。`
})

async function performDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    if (deleteTarget.value.kind === 'single') {
      await deleteResource(props.resource, deleteTarget.value.row.id)
    } else {
      await bulkDeleteResource(props.resource, deleteTarget.value.ids)
      selectedIds.value = []
    }
    deleteTarget.value = null
    await reload()
  } catch (err) {
    deleteError.value = err.message || '删除失败'
  } finally {
    deleting.value = false
  }
}

watch(
  () => props.resource,
  () => {
    page.value = 1
    searchInput.value = ''
    searchQuery.value = ''
    selectedIds.value = []
    sortField.value = 'id'
    sortAsc.value = false
    reload()
  },
)

onMounted(() => {
  sortField.value = props.defaultSort.replace(/^-/, '')
  sortAsc.value = !props.defaultSort.startsWith('-')
  reload()
})
</script>

<style scoped>
.admin-table { display: flex; flex-direction: column; gap: 0.85rem; }

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.55rem 0.75rem;
  flex-wrap: wrap;
}
.toolbar-left { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.toolbar-right { display: flex; gap: 0.5rem; align-items: center; }
.selected-hint { color: var(--text-muted); font-size: 0.85rem; }
.table-search {
  min-width: 240px;
  padding: 0.45rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.9rem;
}

.table-wrap { padding: 0; overflow: hidden; }
.toast { padding: 0.55rem 0.8rem; color: #d64545; font-size: 0.85rem; }
.toast[data-type='error'] { color: #d64545; }

.table-scroll { overflow-x: auto; }
.grid { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 720px; }
.grid th, .grid td {
  padding: 0.6rem 0.9rem;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 55%, transparent);
  text-align: left;
  vertical-align: middle;
  font-size: 0.9rem;
}
.grid thead th {
  background: color-mix(in srgb, var(--bg-paper) 80%, transparent);
  font-weight: 600;
  color: var(--text-muted);
  user-select: none;
  position: sticky;
  top: 0;
  z-index: 1;
}
.grid th.sortable { cursor: pointer; }
.grid th.active { color: var(--primary-color); }
.sort-arrow { margin-left: 0.2rem; font-size: 0.7rem; }

.grid td span {
  display: inline-block;
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.col-check { width: 36px; text-align: center; }
.col-actions { width: 130px; white-space: nowrap; }

.row-btn {
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}
.row-btn:hover { background: color-mix(in srgb, var(--text) 6%, transparent); }
.row-btn.danger:hover {
  background: color-mix(in srgb, #d64545 18%, transparent);
  color: #d64545;
  border-color: color-mix(in srgb, #d64545 45%, transparent);
}
.row-btn + .row-btn { margin-left: 0.35rem; }

.platform-btn-ghost.danger:hover {
  background: color-mix(in srgb, #d64545 14%, transparent);
  color: #d64545;
}

.empty { text-align: center; color: var(--text-muted); padding: 1.5rem; }

.table-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.9rem;
  border-top: 1px solid color-mix(in srgb, var(--border) 45%, transparent);
  gap: 0.6rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.pager-actions { display: flex; align-items: center; gap: 0.4rem; }
.pager-actions select {
  padding: 0.2rem 0.4rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
}

/* Drawer */
.drawer-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: grid;
  place-items: center;
  z-index: 60;
  padding: 1rem;
}
.drawer, .confirm {
  width: min(560px, 100%);
  max-height: calc(100vh - 2rem);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.drawer-head h3, .confirm h3 { margin: 0; font-size: 1.1rem; }
.drawer-body { display: flex; flex-direction: column; gap: 0.75rem; }
.field { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.88rem; color: var(--text-muted); }
.field input[type='text'],
.field input[type='number'],
.field input[type='date'],
.field textarea {
  padding: 0.5rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.95rem;
  font-family: inherit;
}
.field textarea { resize: vertical; min-height: 120px; }
.drawer-actions { display: flex; justify-content: flex-end; gap: 0.5rem; }
.platform-btn-primary.danger {
  background: #d64545;
  border-color: #d64545;
}
.platform-btn-primary.danger:hover { background: #b83a3a; }
</style>
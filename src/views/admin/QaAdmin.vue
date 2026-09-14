<template>
  <div class="qa-admin">
    <header class="admin-section-head">
      <div>
        <h2>留言板设置</h2>
        <p class="subtle">提交防护 + 留言管理，防止乱留言</p>
      </div>
      <div class="head-stats">
        <span class="stat-chip"><b>{{ total }}</b> 条留言</span>
        <span class="stat-chip live" :class="{ on: form.submit_enabled }">
          {{ form.submit_enabled ? 'OPEN' : 'CLOSED' }}
        </span>
      </div>
    </header>

    <div class="admin-grid">
      <section class="panel settings-panel">
        <div class="panel-head">
          <h3>提交防护</h3>
        </div>
        <div class="settings-form">
          <label class="switch-row">
            <input type="checkbox" v-model="form.submit_enabled" />
            <span class="switch-text">
              <strong>开放留言</strong>
              <small>关闭后访客无法提交，历史留言仍展示</small>
            </span>
          </label>
          <label class="switch-row">
            <input type="checkbox" v-model="form.require_login" />
            <span class="switch-text">
              <strong>仅登录用户可留言</strong>
              <small>开启后匿名提交会被拒绝</small>
            </span>
          </label>
          <label class="field">
            <span>同 IP 最小间隔（秒）</span>
            <input type="number" v-model.number="form.min_interval_seconds" min="0" max="3600" />
            <small class="muted">0 = 不限制；建议 10~60</small>
          </label>
          <label class="field">
            <span>屏蔽关键词</span>
            <textarea v-model="keywordsText" rows="5" placeholder="每行一个，命中昵称或正文即拒绝"></textarea>
            <small class="muted">最多 200 条，单条 50 字以内</small>
          </label>
          <div class="form-actions">
            <button class="primary" :disabled="saving" @click="save">
              {{ saving ? '保存中…' : '保存设置' }}
            </button>
            <span v-if="saveMsg" class="save-msg" :class="{ error: saveErr }">{{ saveMsg }}</span>
          </div>
        </div>
      </section>

      <section class="panel messages-panel">
        <div class="panel-head">
          <h3>留言管理</h3>
          <div class="row-actions">
            <input
              v-model="q"
              class="search-input"
              type="search"
              placeholder="搜索昵称 / 内容"
              @keydown.enter="reload(1)"
            />
            <button class="ghost" @click="reload(1)">搜索</button>
            <button class="ghost" @click="reload()">刷新</button>
          </div>
        </div>
        <div class="msg-list">
          <article v-for="m in items" :key="m.id" class="msg-row">
            <div class="msg-body">
              <div class="msg-meta">
                <strong>{{ m.name || '访客' }}</strong>
                <span class="ts">{{ formatTime(m.created_at) }}</span>
                <span class="muted">#{{ m.id }}</span>
              </div>
              <div class="msg-content"><p>{{ m.content }}</p></div>
            </div>
            <div class="msg-actions">
              <button class="danger" :disabled="deleting === m.id" @click="del(m)">删除</button>
            </div>
          </article>
          <p v-if="!items.length && !loading" class="empty">暂无留言</p>
          <p v-if="loading" class="empty">加载中…</p>
        </div>
        <div class="pager" v-if="total > pageSize">
          <button class="ghost" :disabled="page <= 1" @click="reload(page - 1)">上一页</button>
          <span class="muted">{{ page }} / {{ totalPages }}</span>
          <button class="ghost" :disabled="page >= totalPages" @click="reload(page + 1)">下一页</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchQaSettings, saveQaSettings } from '../../api/qaAdmin.js'
import { deleteResource, listResource } from '../../api/adminCrud.js'

const form = reactive({
  submit_enabled: true,
  require_login: false,
  min_interval_seconds: 15,
})
const keywordsText = ref('')
const saving = ref(false)
const saveMsg = ref('')
const saveErr = ref(false)

const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const q = ref('')
const loading = ref(false)
const deleting = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  if (d.toDateString() === now.toDateString()) return pad(d.getHours()) + ':' + pad(d.getMinutes())
  return (d.getMonth() + 1) + '-' + d.getDate() + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes())
}

async function loadSettings() {
  const r = await fetchQaSettings()
  const s = (r && r.settings) || {}
  form.submit_enabled = Boolean(s.submit_enabled)
  form.require_login = Boolean(s.require_login)
  form.min_interval_seconds = Number.isFinite(s.min_interval_seconds) ? s.min_interval_seconds : 15
  keywordsText.value = (s.blocked_keywords || []).join('\n')
}

async function save() {
  saving.value = true
  saveMsg.value = ''
  saveErr.value = false
  try {
    const r = await saveQaSettings({
      submit_enabled: form.submit_enabled,
      require_login: form.require_login,
      min_interval_seconds: form.min_interval_seconds,
      blocked_keywords: keywordsText.value.split('\n').map((s) => s.trim()).filter(Boolean),
    })
    const s = (r && r.settings) || {}
    keywordsText.value = (s.blocked_keywords || []).join('\n')
    saveMsg.value = '已保存'
  } catch (e) {
    saveErr.value = true
    saveMsg.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

async function reload(toPage) {
  if (toPage) page.value = toPage
  loading.value = true
  try {
    const r = await listResource('qa', { page: page.value, pageSize, q: q.value.trim(), sort: '-id' })
    items.value = r.items || []
    total.value = r.total || 0
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function del(m) {
  if (!confirm('确定删除留言 #' + m.id + '？')) return
  deleting.value = m.id
  try {
    await deleteResource('qa', m.id)
    items.value = items.value.filter((x) => x.id !== m.id)
    total.value = Math.max(0, total.value - 1)
  } finally {
    deleting.value = 0
  }
}

onMounted(() => {
  loadSettings().catch(() => {})
  reload(1)
})
</script>

<style scoped>
.qa-admin { display: flex; flex-direction: column; gap: 1rem; }
.admin-section-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; flex-wrap: wrap; }
.admin-section-head h2 { margin: 0 0 0.25rem; font-size: 1.15rem; }
.subtle { color: rgba(255,255,255,0.55); font-size: 0.78rem; margin: 0; }
.head-stats { display: flex; gap: 0.5rem; }
.stat-chip { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.3rem 0.65rem; border: 1px solid rgba(255,255,255,0.1); border-radius: 999px; background: rgba(255,255,255,0.04); }
.stat-chip b { color: var(--orange, #ff7a45); }
.stat-chip.live { color: rgba(255,255,255,0.5); }
.stat-chip.live.on { color: #6ef195; border-color: rgba(110,241,149,0.4); }
.admin-grid { display: grid; grid-template-columns: 340px 1fr; gap: 1rem; align-items: start; }
@media (max-width: 900px) { .admin-grid { grid-template-columns: 1fr; } }
.panel { background: rgba(8,10,14,0.55); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 0.85rem; }
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; gap: 0.5rem; flex-wrap: wrap; }
.panel-head h3 { margin: 0; font-size: 0.95rem; }
.row-actions { display: flex; gap: 0.4rem; align-items: center; }
button.ghost { background: transparent; border: 1px solid rgba(255,255,255,0.12); color: rgba(255,255,255,0.7); padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer; }
button.ghost:hover { border-color: var(--orange, #ff7a45); color: #fff; }
button.ghost:disabled { opacity: 0.4; cursor: default; }
button.danger { background: rgba(255,80,80,0.12); border: 1px solid rgba(255,80,80,0.4); color: #ff8a8a; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer; }
button.danger:hover { background: rgba(255,80,80,0.22); }
button.primary { background: rgba(110,241,149,0.12); border: 1px solid rgba(110,241,149,0.4); color: #6ef195; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.8rem; cursor: pointer; }
button.primary:hover { background: rgba(110,241,149,0.2); }
button.primary:disabled { opacity: 0.5; cursor: default; }

.settings-form { display: flex; flex-direction: column; gap: 0.85rem; }
.switch-row { display: flex; gap: 0.6rem; align-items: flex-start; cursor: pointer; }
.switch-row input { margin-top: 0.2rem; }
.switch-text { display: flex; flex-direction: column; gap: 0.15rem; font-size: 0.85rem; }
.switch-text small { color: rgba(255,255,255,0.45); font-size: 0.72rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; }
.field input, .field textarea {
  padding: 0.5rem 0.65rem;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 8px;
  background: rgba(255,255,255,0.03);
  color: rgba(255,255,255,0.9);
  font-size: 0.85rem;
  font-family: inherit;
}
.field textarea { resize: vertical; }
.muted { color: rgba(255,255,255,0.45); font-size: 0.72rem; }
.form-actions { display: flex; align-items: center; gap: 0.6rem; }
.save-msg { font-size: 0.75rem; color: #6ef195; }
.save-msg.error { color: #ff8a8a; }

.search-input {
  padding: 0.3rem 0.55rem;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  background: rgba(255,255,255,0.03);
  color: rgba(255,255,255,0.85);
  font-size: 0.78rem;
  width: 160px;
}
.msg-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: 60vh; overflow-y: auto; }
.msg-row { display: grid; grid-template-columns: 1fr auto; gap: 0.65rem; padding: 0.55rem 0.65rem; background: rgba(255,255,255,0.02); border-radius: 8px; align-items: center; }
.msg-body { min-width: 0; }
.msg-meta { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; font-size: 0.78rem; }
.ts { color: rgba(255,255,255,0.4); font-size: 0.7rem; }
.msg-content p { margin: 0.2rem 0 0; font-size: 0.85rem; color: rgba(255,255,255,0.85); word-break: break-word; }
.msg-actions { display: flex; gap: 0.4rem; }
.empty { color: rgba(255,255,255,0.4); font-size: 0.8rem; text-align: center; padding: 1rem; }
.pager { display: flex; align-items: center; justify-content: center; gap: 0.6rem; margin-top: 0.65rem; }
</style>

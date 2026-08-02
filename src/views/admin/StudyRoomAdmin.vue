<template>
  <div class="study-room-admin">
    <header class="admin-section-head">
      <div>
        <h2>聊天室管理</h2>
        <p class="subtle">实时消息流 + 在线用户 + 删/恢复 + 踢出</p>
      </div>
      <div class="head-stats">
        <span class="stat-chip"><b>{{ totalMessages }}</b> 消息</span>
        <span class="stat-chip"><b>{{ onlineUsers.length }}</b> 在线</span>
        <span class="stat-chip live" :class="{ on: live }">{{ live ? 'LIVE' : 'PAUSED' }}</span>
      </div>
    </header>

    <div class="admin-grid">
      <section class="panel messages-panel">
        <div class="panel-head">
          <h3>消息流</h3>
          <div class="row-actions">
            <label class="checkbox">
              <input type="checkbox" v-model="includeDeleted" @change="reload" />
              <span>含已删</span>
            </label>
            <button class="ghost" @click="reload">刷新</button>
            <button class="ghost" @click="live = !live">{{ live ? '暂停' : '继续' }}</button>
          </div>
        </div>
        <div class="msg-list" ref="listRef">
          <article v-for="m in messages" :key="m.id" class="msg-row" :class="{ deleted: m.is_deleted }">
            <div class="msg-avatar">
              <img v-if="m.avatar" :src="resolveAvatar(m.avatar)" :alt="m.username" />
              <span v-else class="avatar-fallback">{{ (m.username || '?').slice(0, 1).toUpperCase() }}</span>
            </div>
            <div class="msg-body">
              <div class="msg-meta">
                <strong>{{ m.nickname || m.username || '匿名' }}</strong>
                <span class="muted">@{{ m.username }}</span>
                <span class="ts">{{ formatTime(m.created_at) }}</span>
                <span v-if="m.is_deleted" class="tag-deleted">已软删</span>
                <span v-else-if="m.message_type === 'sticker'" class="tag-sticker">表情</span>
              </div>
              <div class="msg-content">
                <img v-if="m.message_type === 'sticker' && m.sticker_url" :src="resolveSticker(m.sticker_url)" alt="sticker" class="sticker-thumb" />
                <p v-else>{{ m.content }}</p>
              </div>
            </div>
            <div class="msg-actions">
              <button v-if="!m.is_deleted" class="danger" @click="del(m)">删除</button>
              <button v-else class="primary" @click="restore(m)">恢复</button>
            </div>
          </article>
          <p v-if="!messages.length" class="empty">暂无消息</p>
        </div>
      </section>

      <aside class="panel users-panel">
        <div class="panel-head">
          <h3>在线用户</h3>
          <button class="ghost" @click="reloadUsers">刷新</button>
        </div>
        <ul class="user-list">
          <li v-for="u in onlineUsers" :key="u.id" class="user-row">
            <div class="user-avatar">
              <img v-if="u.avatar" :src="resolveAvatar(u.avatar)" :alt="u.username" />
              <span v-else class="avatar-fallback">{{ (u.username || '?').slice(0, 1).toUpperCase() }}</span>
            </div>
            <div class="user-meta">
              <strong>{{ u.nickname || u.username }}</strong>
              <span class="muted">@{{ u.username }} · #{{ u.id }}</span>
            </div>
            <button class="danger" @click="kick(u)">踢出</button>
          </li>
          <li v-if="!onlineUsers.length" class="empty">暂无在线用户</li>
        </ul>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import {
  adminListStudyRoomMessages,
  adminDeleteStudyRoomMessage,
  adminRestoreStudyRoomMessage,
  adminListStudyRoomOnlineUsers,
  adminKickUser,
} from '../../api/platform.js'
import { resolveMediaUrl } from '../../api/platform.js'
import { onMounted as _onMounted } from 'vue'

const messages = ref([])
const onlineUsers = ref([])
const includeDeleted = ref(true)
const live = ref(true)
const listRef = ref(null)
let pollTimer = 0
let usersTimer = 0

const totalMessages = computed(() => messages.value.length)

function resolveAvatar(url) { return resolveMediaUrl(url) }
function resolveSticker(url) { return resolveMediaUrl(url) }
function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  if (d.toDateString() === now.toDateString()) return pad(d.getHours()) + ':' + pad(d.getMinutes())
  return (d.getMonth()+1) + '-' + d.getDate() + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes())
}

async function reload() {
  const r = await adminListStudyRoomMessages({ limit: 100, includeDeleted: includeDeleted.value ? 1 : 0 })
  const data = r && r.data ? r.data : r
  messages.value = (data && data.items) || []
}
async function reloadUsers() {
  const r = await adminListStudyRoomOnlineUsers()
  const data = r && r.data ? r.data : r
  onlineUsers.value = (data && data.items) || []
}

async function del(m) {
  if (!confirm('确定删除消息 #' + m.id + '?')) return
  await adminDeleteStudyRoomMessage(m.id)
  m.is_deleted = true
  m.deleted_at = new Date().toISOString()
}
async function restore(m) {
  await adminRestoreStudyRoomMessage(m.id)
  m.is_deleted = false
  m.deleted_at = null
}
async function kick(u) {
  const reason = prompt('踢出原因 (可选):', '') || '管理员请出'
  if (reason === null) return
  await adminKickUser(u.id, reason)
  await reloadUsers()
}

onMounted(() => {
  reload()
  reloadUsers()
  pollTimer = window.setInterval(() => { if (live.value) reload() }, 8000)
  usersTimer = window.setInterval(reloadUsers, 15000)
})
onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (usersTimer) clearInterval(usersTimer)
})
</script>

<style scoped>
.study-room-admin { display: flex; flex-direction: column; gap: 1rem; }
.admin-section-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; flex-wrap: wrap; }
.admin-section-head h2 { margin: 0 0 0.25rem; font-size: 1.15rem; }
.subtle { color: rgba(255,255,255,0.55); font-size: 0.78rem; margin: 0; }
.head-stats { display: flex; gap: 0.5rem; }
.stat-chip { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.3rem 0.65rem; border: 1px solid rgba(255,255,255,0.1); border-radius: 999px; background: rgba(255,255,255,0.04); }
.stat-chip b { color: var(--orange, #ff7a45); }
.stat-chip.live.on { color: #6ef195; border-color: rgba(110,241,149,0.4); }
.admin-grid { display: grid; grid-template-columns: 1fr 320px; gap: 1rem; }
@media (max-width: 900px) { .admin-grid { grid-template-columns: 1fr; } }
.panel { background: rgba(8,10,14,0.55); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 0.85rem; }
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; }
.panel-head h3 { margin: 0; font-size: 0.95rem; }
.row-actions { display: flex; gap: 0.4rem; align-items: center; }
.checkbox { display: inline-flex; gap: 0.35rem; font-size: 0.75rem; color: rgba(255,255,255,0.6); }
button.ghost { background: transparent; border: 1px solid rgba(255,255,255,0.12); color: rgba(255,255,255,0.7); padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer; }
button.ghost:hover { border-color: var(--orange, #ff7a45); color: #fff; }
button.danger { background: rgba(255,80,80,0.12); border: 1px solid rgba(255,80,80,0.4); color: #ff8a8a; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer; }
button.danger:hover { background: rgba(255,80,80,0.22); }
button.primary { background: rgba(110,241,149,0.12); border: 1px solid rgba(110,241,149,0.4); color: #6ef195; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer; }
.msg-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: 60vh; overflow-y: auto; }
.msg-row { display: grid; grid-template-columns: 36px 1fr auto; gap: 0.65rem; padding: 0.55rem 0.65rem; background: rgba(255,255,255,0.02); border-radius: 8px; align-items: center; }
.msg-row.deleted { opacity: 0.5; }
.msg-avatar, .user-avatar { width: 36px; height: 36px; border-radius: 50%; overflow: hidden; background: rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: center; }
.msg-avatar img, .user-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-fallback { font-weight: 600; color: rgba(255,255,255,0.7); }
.msg-body { min-width: 0; }
.msg-meta { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; font-size: 0.78rem; }
.muted { color: rgba(255,255,255,0.45); }
.ts { color: rgba(255,255,255,0.4); font-size: 0.7rem; }
.tag-deleted { background: rgba(255,80,80,0.2); color: #ff8a8a; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.65rem; }
.tag-sticker { background: rgba(110,241,149,0.18); color: #6ef195; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.65rem; }
.msg-content p { margin: 0.2rem 0 0; font-size: 0.85rem; color: rgba(255,255,255,0.85); word-break: break-word; }
.sticker-thumb { max-width: 60px; max-height: 60px; border-radius: 4px; }
.msg-actions { display: flex; gap: 0.4rem; }
.user-list { display: flex; flex-direction: column; gap: 0.4rem; max-height: 60vh; overflow-y: auto; }
.user-row { display: grid; grid-template-columns: 32px 1fr auto; gap: 0.5rem; padding: 0.5rem; background: rgba(255,255,255,0.02); border-radius: 8px; align-items: center; }
.user-meta { display: flex; flex-direction: column; min-width: 0; font-size: 0.8rem; }
.empty { color: rgba(255,255,255,0.4); font-size: 0.8rem; text-align: center; padding: 1rem; }
</style>

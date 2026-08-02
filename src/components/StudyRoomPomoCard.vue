<template>
  <div class="sp-card-grid">
    <button type="button" class="sp-card sp-card--chat" @click="goChat" :title="`进入自习室 · ${online} 人在线`">
      <div class="sp-card__head">
        <span class="sp-label">ONLINE</span>
        <span v-if="hasNew" class="sp-dot" aria-label="新消息" />
      </div>
      <div class="sp-value">{{ online }}</div>
      <div class="sp-sub">
        <template v-if="recent">
          <img v-if="recent.message_type === 'sticker' && recent.sticker_url" :src="resolveUrl(recent.sticker_url)" alt="" class="sp-mini" />
          <span class="sp-sub__text">{{ recentText }}</span>
        </template>
        <template v-else><span class="sp-sub__text">自习室静悄悄</span></template>
      </div>
    </button>

    <button type="button" class="sp-card sp-card--pomo" @click="goPomo" :title="pomoTitle">
      <div class="sp-card__head">
        <span class="sp-label">FOCUS</span>
        <span v-if="running" class="sp-dot sp-dot--on" />
      </div>
      <div class="sp-value">{{ focusValue }}</div>
      <div class="sp-sub">
        <span class="sp-sub__text">{{ focusSub }}</span>
      </div>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { fetchStudyRoomOnline, fetchStudyRoomMessages, fetchPomodoroStats, resolveMediaUrl, getPlatformToken, openStudyRoomSocket } from '../api/platform.js'
import { useRouter } from 'vue-router'

const router = useRouter()
const online = ref(0)
const recent = ref(null)
const stats = ref({ today_count: 0, today_minutes: 0, running: null })
const now = ref(Date.now())
const hasNew = ref(false)

let pollTimer = 0
let tickTimer = 0
let ws = null
let lastSeenId = 0

const focusValue = computed(() => {
  const r = stats.value.running
  if (r && r.started_at) {
    const end = new Date(r.started_at).getTime() + (r.duration_min || 25) * 60000
    const left = Math.max(0, Math.floor((end - now.value) / 1000))
    const m = Math.floor(left / 60), s = left % 60
    return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0')
  }
  return String(stats.value.today_count || 0)
})
const focusSub = computed(() => {
  const r = stats.value.running
  if (r && r.started_at) return '专注中 · ' + (r.mode || 'focus') + ''
  const mins = stats.value.today_minutes || 0
  return '今日 ' + mins + ' 分钟'
})
const pomoTitle = computed(() => focusSub.value)
const recentText = computed(() => {
  const m = recent.value
  if (!m) return ''
  if (m.message_type === 'sticker') return '[表情] ' + (m.nickname || m.username || '')
  const t = (m.content || '').slice(0, 18)
  return t + (m.content && m.content.length > 18 ? '...' : '')
})
const running = computed(() => !!(stats.value.running && stats.value.running.started_at))

function resolveUrl(p) { try { return resolveMediaUrl(p) } catch (e) { return p } }

async function refresh() {
  try {
    const [o, m, s] = await Promise.all([
      fetchStudyRoomOnline().catch(() => null),
      fetchStudyRoomMessages({ limit: 1 }).catch(() => null),
      fetchPomodoroStats().catch(() => null),
    ])
    if (o) {
      const d = o.data || o
      online.value = d.count || 0
    }
    if (m) {
      const d = m.data || m
      const items = (d.items || [])
      const first = items[items.length - 1] || null
      if (first && first.id !== lastSeenId) {
        if (lastSeenId && first.id > lastSeenId) hasNew.value = true
        lastSeenId = first.id
      }
      recent.value = first
    }
    if (s) {
      const d = s.data || s
      stats.value = d
    }
  } catch (e) { /* ignore */ }
}

function goChat() {
  hasNew.value = false
  router.push('/app/pomo')
  // 通知 PomoStudyRoom 打开(下次进入时会自动拉历史;这里仅跳转)
}
function goPomo() {
  router.push('/app/pomo')
}

onMounted(() => {
  refresh()
  pollTimer = window.setInterval(refresh, 20000)
  tickTimer = window.setInterval(() => { now.value = Date.now() }, 1000)
  // 可选:订阅 WS 拿最新消息(此处简化用轮询)
  try {
    const tk = getPlatformToken && getPlatformToken()
    if (tk && openStudyRoomSocket) {
      ws = openStudyRoomSocket({
        token: tk,
        onMessage: (msg) => {
          if (msg && msg.type === 'msg' && msg.id) {
            if (msg.id > lastSeenId) {
              lastSeenId = msg.id
              recent.value = msg
              hasNew.value = true
            }
          }
        },
      })
    }
  } catch (e) { /* ignore */ }
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (tickTimer) clearInterval(tickTimer)
  if (ws && ws.close) try { ws.close() } catch (e) { /* ignore */ }
})
</script>

<style scoped>
.sp-card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; padding: 0.4rem; }
.sp-card {
  appearance: none;
  background: rgba(8,10,14,0.55);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 0.55rem 0.7rem;
  text-align: left;
  color: rgba(255,255,255,0.85);
  cursor: pointer;
  transition: border-color 0.15s, transform 0.15s;
  font-family: inherit;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}
.sp-card:hover { border-color: var(--orange, #ff7a45); transform: translateY(-1px); }
.sp-card__head { display: flex; justify-content: space-between; align-items: center; }
.sp-label { font-size: 0.6rem; letter-spacing: 0.18em; color: rgba(255,255,255,0.45); text-transform: uppercase; }
.sp-value { font-size: 1.25rem; font-weight: 600; font-variant-numeric: tabular-nums; color: var(--orange, #ff7a45); line-height: 1.1; }
.sp-card--pomo .sp-value { color: #6ef195; }
.sp-sub { display: flex; gap: 0.3rem; align-items: center; min-width: 0; }
.sp-sub__text { font-size: 0.66rem; color: rgba(255,255,255,0.55); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sp-mini { width: 16px; height: 16px; object-fit: cover; border-radius: 3px; flex-shrink: 0; }
.sp-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--orange, #ff7a45); box-shadow: 0 0 6px var(--orange, #ff7a45); }
.sp-dot--on { background: #6ef195; box-shadow: 0 0 6px #6ef195; }
</style>

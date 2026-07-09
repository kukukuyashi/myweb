<template>
  <div class="platform-stats">
    <div class="lcd-row">
      <span class="lcd-key">TIME</span>
      <span class="lcd-val lcd-val--time">{{ clockText }}</span>
    </div>
    <div class="lcd-row">
      <span class="lcd-key">TODAY</span>
      <span class="lcd-val">{{ todayCount }}</span>
    </div>
    <div class="lcd-row">
      <span class="lcd-key">TOTAL</span>
      <span class="lcd-val">{{ totalCount }}</span>
    </div>
    <div class="lcd-row">
      <span class="lcd-key">UPTIME</span>
      <span class="lcd-val">{{ siteDays }}<span class="lcd-unit">D</span></span>
    </div>
    <p v-if="profile" class="stats-user">当前 <strong>@{{ profile.username }}</strong></p>
    <p v-else class="stats-user">访客模式 · <router-link to="/app/me">登录</router-link></p>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

defineProps({
  siteDays: { type: Number, default: 0 },
  profile: { type: Object, default: null },
})

const STORAGE_KEY = 'cyincVisitorStats'
const clockText = ref('')
const todayCount = ref(0)
const totalCount = ref(0)
let clockTimer = null

function todayKey() {
  return new Date().toISOString().slice(0, 10)
}

function updateClock() {
  clockText.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
}

function loadAndBumpVisitor() {
  let data = {}
  try {
    data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    data = {}
  }

  const day = todayKey()
  const sessionKey = `platform-seen-${day}`
  if (!sessionStorage.getItem(sessionKey)) {
    data[day] = (data[day] || 0) + 1
    data.total = (data.total || 0) + 1
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    sessionStorage.setItem(sessionKey, '1')
  }

  todayCount.value = data[day] || 0
  totalCount.value = data.total || 0
}

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  loadAndBumpVisitor()
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
})
</script>

<style scoped>
.platform-stats {
  display: grid;
  gap: 0.35rem;
}

.lcd-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0.6rem;
  background: var(--topbar-bg, #1a1a2e);
  color: #c8f7c5;
  font-family: var(--mono);
  border: 1px inset var(--border);
}

.lcd-key {
  font-size: 0.58rem;
  letter-spacing: 0.12em;
  opacity: 0.75;
}

.lcd-val {
  font-size: 0.95rem;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.08em;
  text-shadow: 0 0 8px rgba(200, 247, 197, 0.35);
}

.lcd-val--time {
  font-size: 1.05rem;
  color: #fff;
}

.lcd-unit {
  font-size: 0.65rem;
  opacity: 0.7;
  margin-left: 0.15rem;
}

.stats-user {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0.35rem 0 0;
}

.stats-user strong {
  color: var(--orange);
}

.stats-user a {
  color: var(--orange);
  text-decoration: none;
}
</style>

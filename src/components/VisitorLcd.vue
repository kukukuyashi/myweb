<template>
  <div class="visitor-lcd panel">
    <div class="panel-header">
      <span>Visitors</span>
      <span class="lcd-dot" aria-hidden="true" />
    </div>
    <div class="panel-body">
      <div class="lcd-row">
        <span class="lcd-key">TODAY</span>
        <span class="lcd-val">{{ todayCount }}</span>
      </div>
      <div class="lcd-row">
        <span class="lcd-key">TOTAL</span>
        <span class="lcd-val">{{ totalCount }}</span>
      </div>
      <p class="lcd-note">装饰计数 · 非真实统计</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const STORAGE_KEY = 'cyincVisitorStats'
const todayCount = ref(0)
const totalCount = ref(0)

function todayKey() {
  return new Date().toISOString().slice(0, 10)
}

function loadStats() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

function saveStats(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

onMounted(() => {
  const data = loadStats()
  const day = todayKey()
  const sessionKey = `seen-${day}`
  const alreadyToday = sessionStorage.getItem(sessionKey)

  if (!alreadyToday) {
    data[day] = (data[day] || 0) + 1
    data.total = (data.total || 0) + 1
    saveStats(data)
    sessionStorage.setItem(sessionKey, '1')
  }

  todayCount.value = data[day] || 0
  totalCount.value = data.total || 0
})
</script>

<style scoped>
.visitor-lcd {
  margin-top: 0;
}

.lcd-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--orange);
  box-shadow: 0 0 6px rgba(232, 93, 4, 0.65);
  animation: lcd-pulse 1.6s ease-in-out infinite;
}

@keyframes lcd-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.lcd-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.55rem;
  margin-bottom: 0.35rem;
  background: var(--topbar-bg);
  color: #c8f7c5;
  font-family: var(--mono);
  border: 1px inset var(--border);
}

.lcd-row:last-of-type {
  margin-bottom: 0.5rem;
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

.lcd-note {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.52rem;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

@media (prefers-reduced-motion: reduce) {
  .lcd-dot {
    animation: none;
  }
}
</style>

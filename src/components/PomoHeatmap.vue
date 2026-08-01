<template>
  <section class="pomo-heatmap platform-panel ink-panel reveal-item" data-reveal>
    <header class="panel-head">
      <h2>90 天专注热力图</h2>
      <p class="panel-sub">HEATMAP · 90 DAYS</p>
    </header>
    <div v-if="loading" class="heatmap-loading">加载中…</div>
    <div v-else class="heatmap-wrap">
      <div class="heatmap-legend">
        <span>少</span>
        <span class="heatmap-legend__cell" v-for="(c,i) in 5" :key="i" :data-level="i-1"></span>
        <span>多</span>
      </div>
      <svg :viewBox="`0 0 ${width} ${height}`" class="heatmap-svg" preserveAspectRatio="xMinYMid meet" role="img" aria-label="90 days pomo heatmap">
        <g v-for="(week, wi) in grid" :key="wi" :transform="`translate(${week.x}, 0)`">
          <g v-for="(day, di) in week.days" :key="di" :transform="`translate(0, ${day.y})`">
            <rect
              class="heatmap-cell"
              :data-level="day.level"
              :width="cell" :height="cell"
              rx="2" ry="2"
            />
            <title>{{ day.tooltip }}</title>
          </g>
        </g>
      </svg>
      <div class="heatmap-foot">
        <span>共 <strong>{{ totalMinutes }}</strong> 分钟 · <strong>{{ totalSessions }}</strong> 个番茄</span>
        <span class="heatmap-foot__date">{{ rangeLabel }}</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchPomodoroTimeline } from '../api/platform.js'

const days = 90
const cell = 12
const gap = 2
const labelW = 18
const headerH = 16

const cellDay = computed(() => cell + gap)
const height = computed(() => headerH + 7 * cellDay.value)
const width = computed(() => labelW + Math.ceil(days / 7) * cellDay.value)

const loading = ref(true)
const dataMap = ref({}) // { 'YYYY-MM-DD': { total_minutes, sessions_count } }

async function load() {
  loading.value = true
  try {
    const json = await fetchPomodoroTimeline(days)
    const map = {}
    for (const d of json.data?.days || []) {
      map[d.date] = {
        total_minutes: d.total_minutes || 0,
        sessions_count: d.sessions?.length || 0,
      }
    }
    dataMap.value = map
  } catch {
    dataMap.value = {}
  } finally {
    loading.value = false
  }
}
onMounted(load)

function dateKey(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function levelFor(min) {
  if (min <= 0) return 0
  if (min <= 25) return 1
  if (min <= 60) return 2
  if (min <= 120) return 3
  return 4
}

const grid = computed(() => {
  // start from 89 days ago, align to Monday of that week
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const start = new Date(today)
  start.setDate(today.getDate() - (days - 1))
  // shift to Monday of start week
  const startDay = (start.getDay() + 6) % 7 // Mon=0..Sun=6
  start.setDate(start.getDate() - startDay)

  const weeks = []
  for (let w = 0; w < Math.ceil(days / 7) + 1; w++) {
    const week = { x: labelW + w * cellDay.value, days: [] }
    for (let d = 0; d < 7; d++) {
      const date = new Date(start)
      date.setDate(start.getDate() + w * 7 + d)
      const key = dateKey(date)
      const info = dataMap.value[key] || { total_minutes: 0, sessions_count: 0 }
      week.days.push({
        y: headerH + d * cellDay.value,
        level: levelFor(info.total_minutes),
        tooltip: `${key}：${info.sessions_count} 番茄 / ${info.total_minutes} 分钟`,
      })
    }
    weeks.push(week)
  }
  return weeks
})

const totalMinutes = computed(() => Object.values(dataMap.value).reduce((s, d) => s + d.total_minutes, 0))
const totalSessions = computed(() => Object.values(dataMap.value).reduce((s, d) => s + d.sessions_count, 0))
const rangeLabel = computed(() => {
  const today = new Date()
  const start = new Date(today)
  start.setDate(today.getDate() - (days - 1))
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}`
  return `${fmt(start)} – ${fmt(today)}`
})
</script>

<style scoped>
.pomo-heatmap { padding: 1.15rem 1.25rem; margin-bottom: 1rem; }
.panel-head { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.85rem; }
.panel-head h2 { margin: 0; font-size: 1rem; }
.panel-sub { margin: 0; font-family: var(--mono); font-size: 0.7rem; color: var(--text-muted); letter-spacing: 0.05em; }
.heatmap-loading { font-size: 0.85rem; color: var(--text-muted); font-family: var(--mono); }

.heatmap-wrap { display: flex; flex-direction: column; gap: 0.6rem; }

.heatmap-svg {
  width: 100%;
  height: auto;
  display: block;
}

.heatmap-cell {
  fill: var(--border);
  transition: fill 0.15s;
}
.heatmap-cell[data-level="1"] { fill: rgba(232, 93, 4, 0.18); }
.heatmap-cell[data-level="2"] { fill: rgba(232, 93, 4, 0.38); }
.heatmap-cell[data-level="3"] { fill: rgba(232, 93, 4, 0.65); }
.heatmap-cell[data-level="4"] { fill: var(--orange, #e85d04); }
.heatmap-cell:hover { stroke: var(--text); stroke-width: 1; }

.heatmap-legend { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.7rem; color: var(--text-muted); font-family: var(--mono); align-self: flex-end; }
.heatmap-legend__cell {
  width: 11px; height: 11px; border-radius: 2px;
  background: var(--border);
}
.heatmap-legend__cell[data-level="0"] { background: var(--border); }
.heatmap-legend__cell[data-level="1"] { background: rgba(232, 93, 4, 0.18); }
.heatmap-legend__cell[data-level="2"] { background: rgba(232, 93, 4, 0.38); }
.heatmap-legend__cell[data-level="3"] { background: rgba(232, 93, 4, 0.65); }
.heatmap-legend__cell[data-level="4"] { background: var(--orange, #e85d04); }

.heatmap-foot {
  display: flex; justify-content: space-between; align-items: center; gap: 0.75rem;
  font-size: 0.75rem; color: var(--text-muted); font-family: var(--mono);
  flex-wrap: wrap;
}
.heatmap-foot strong { color: var(--text); }
.heatmap-foot__date { opacity: 0.7; }

@media (max-width: 640px) {
  .heatmap-svg { font-size: 0.7rem; }
}
</style>

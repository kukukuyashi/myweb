<template>
  <div class="arcade-page platform-page container layout-single">
    <router-link to="/app/arcade" class="arcade-back">← 返回游戏厅</router-link>
    <header class="arcade-hero platform-panel ink-panel">
      <p class="platform-coord">ARCADE · REACTION · SPEED</p>
      <h1 class="arcade-title">反应速度测试</h1>
      <p class="arcade-lead">
        屏幕会在<strong>随机时间</strong>后由红转绿，看到绿色立刻点击。
        测的是你从「看到」到「动手」的纯反应时间 —— 太早点会算犯规。
      </p>
    </header>

    <section class="arcade-body platform-panel ink-panel">
      <div class="arcade-toolbar">
        <div class="arcade-stats">
          <div class="arcade-stat">
            <span class="arcade-stat-label">本次</span>
            <span class="arcade-stat-value arcade-next">{{ lastText }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">最近平均</span>
            <span class="arcade-stat-value">{{ avgText }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">最佳</span>
            <span class="arcade-stat-value">{{ bestText }}</span>
          </div>
        </div>
      </div>

      <button
        type="button"
        class="react-stage"
        :class="'is-' + phase"
        @click="onStageClick"
      >
        <template v-if="phase === 'idle'">
          <span class="react-big">点击开始</span>
          <span class="react-sub">看到绿色就立刻点</span>
        </template>
        <template v-else-if="phase === 'wait'">
          <span class="react-big">等待绿色…</span>
          <span class="react-sub">别急，还没变</span>
        </template>
        <template v-else-if="phase === 'go'">
          <span class="react-big">点！</span>
        </template>
        <template v-else-if="phase === 'early'">
          <span class="react-big">太早了！</span>
          <span class="react-sub">点击重试</span>
        </template>
        <template v-else-if="phase === 'result'">
          <span class="react-big react-ms">{{ lastMs }}<em>ms</em></span>
          <span class="react-sub">{{ resultComment }} · 点击再来</span>
        </template>
      </button>

      <div v-if="history.length" class="react-history">
        <span class="react-history-label">最近</span>
        <span v-for="(h, i) in history" :key="i" class="react-chip">{{ h }}</span>
      </div>

      <p class="arcade-hint">人类平均视觉反应约 200-270ms。连点无效，绿色出现才计时。</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const phase = ref('idle')
const lastMs = ref(0)
const history = ref([])
const best = ref(loadBest())
let goAt = 0
let waitTimer = null

const lastText = computed(() => (lastMs.value ? `${lastMs.value}ms` : '--'))
const bestText = computed(() => (best.value ? `${best.value}ms` : '--'))
const avgText = computed(() => {
  if (!history.value.length) return '--'
  const sum = history.value.reduce((a, b) => a + b, 0)
  return `${Math.round(sum / history.value.length)}ms`
})
const resultComment = computed(() => {
  const v = lastMs.value
  if (v < 180) return '闪电反应'
  if (v < 240) return '相当敏捷'
  if (v < 320) return '正常水平'
  return '再放松些'
})

function loadBest() {
  try { return Number(localStorage.getItem('arcade-react-best') || 0) } catch { return 0 }
}

function clearWait() {
  if (waitTimer) { clearTimeout(waitTimer); waitTimer = null }
}

function onStageClick() {
  if (phase.value === 'idle' || phase.value === 'early' || phase.value === 'result') {
    startWait()
  } else if (phase.value === 'wait') {
    clearWait()
    phase.value = 'early'
  } else if (phase.value === 'go') {
    const ms = Math.round(performance.now() - goAt)
    lastMs.value = ms
    const h = history.value.slice()
    h.push(ms)
    if (h.length > 5) h.shift()
    history.value = h
    if (!best.value || ms < best.value) {
      best.value = ms
      try { localStorage.setItem('arcade-react-best', String(ms)) } catch { /* ignore */ }
    }
    phase.value = 'result'
  }
}

function startWait() {
  phase.value = 'wait'
  const delay = 1200 + Math.random() * 2800
  clearWait()
  waitTimer = setTimeout(() => {
    phase.value = 'go'
    goAt = performance.now()
  }, delay)
}

onUnmounted(clearWait)
</script>

<style scoped>
.arcade-back {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.74rem;
  color: var(--text-muted);
  text-decoration: none;
  margin-bottom: 0.85rem;
  transition: color 0.15s;
}
.arcade-back:hover { color: var(--orange); }

.arcade-hero { text-align: left; }
.arcade-title {
  font-family: var(--mono);
  font-size: clamp(1.5rem, 4vw, 2.1rem);
  margin: 0.35rem 0 0.5rem;
}
.arcade-lead {
  color: var(--text-muted);
  line-height: 1.7;
  margin: 0;
  max-width: 46rem;
}
.arcade-lead strong { color: var(--orange); }

.arcade-body { margin-top: 1rem; }

.arcade-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem 1.5rem;
  padding-bottom: 1.1rem;
  margin-bottom: 1.2rem;
  border-bottom: 1px dashed var(--border);
}
.arcade-stat-label {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  text-transform: uppercase;
}
.arcade-stats { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.arcade-stat { display: flex; flex-direction: column; gap: 0.2rem; }
.arcade-stat-value {
  font-family: var(--mono);
  font-size: 1.15rem;
  font-variant-numeric: tabular-nums;
}
.arcade-next { color: var(--orange); }

.react-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  min-height: 16rem;
  border: 1px solid var(--border);
  cursor: pointer;
  color: #fff;
  user-select: none;
  transition: background 0.12s ease;
}

.react-stage.is-idle { background: #3f6fb0; }
.react-stage.is-wait { background: #d64545; }
.react-stage.is-go { background: #3f9d6a; }
.react-stage.is-early { background: #b5842a; }
.react-stage.is-result { background: var(--steel); }

.react-big {
  font-family: var(--mono);
  font-size: clamp(1.8rem, 7vw, 3rem);
  font-weight: 700;
  line-height: 1;
}
.react-ms em { font-size: 0.4em; font-style: normal; margin-left: 0.15em; }
.react-sub { font-family: var(--mono); font-size: 0.85rem; opacity: 0.9; }

.react-history {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}
.react-history-label {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.react-chip {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text-muted);
}

.arcade-hint {
  margin: 1.2rem 0 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
}

@media (max-width: 560px) {
  .arcade-stats { width: 100%; justify-content: space-between; gap: 0.75rem; }
}
</style>
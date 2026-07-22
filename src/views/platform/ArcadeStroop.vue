<template>
  <div class="arcade-page platform-page container layout-single">
    <router-link to="/app/arcade" class="arcade-back">← 返回游戏厅</router-link>
    <header class="arcade-hero platform-panel ink-panel">
      <p class="platform-coord">ARCADE · STROOP · CONFLICT</p>
      <h1 class="arcade-title">斯特鲁普测试</h1>
      <p class="arcade-lead">
        屏幕上的字有它的<strong>意思</strong>，也有它的<strong>颜色</strong>。请一直选
        <strong>字的实际颜色</strong>，别被字义带偏 —— 这就是著名的「斯特鲁普效应」。
      </p>
    </header>

    <section class="arcade-body platform-panel ink-panel">
      <div class="arcade-toolbar">
        <div class="arcade-stats">
          <div class="arcade-stat">
            <span class="arcade-stat-label">进度</span>
            <span class="arcade-stat-value">{{ Math.min(round, totalRounds) }}/{{ totalRounds }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">正确</span>
            <span class="arcade-stat-value arcade-next">{{ correct }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">平均反应</span>
            <span class="arcade-stat-value">{{ avgText }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">最佳</span>
            <span class="arcade-stat-value">{{ bestText }}</span>
          </div>
        </div>
        <div class="arcade-actions">
          <button type="button" class="platform-btn-primary" @click="startGame">
            {{ playing ? '重开' : '开始' }}
          </button>
        </div>
      </div>

      <div class="stroop-stage">
        <transition name="arcade-veil">
          <div v-if="!playing && !finished" class="arcade-veil">
            <p class="arcade-veil-title">准备好了吗？</p>
            <p class="arcade-veil-tip">共 {{ totalRounds }} 轮，选“字的颜色”不是字义</p>
          </div>
        </transition>

        <transition name="arcade-veil">
          <div v-if="finished" class="arcade-veil arcade-veil--win">
            <p class="arcade-veil-title">完成！</p>
            <p class="arcade-veil-time">{{ avgText }}</p>
            <p class="arcade-veil-sub">正确 {{ correct }}/{{ totalRounds }}</p>
            <p v-if="isNewBest" class="arcade-veil-best">★ 新纪录</p>
            <button type="button" class="platform-btn-primary" @click="startGame">再来一局</button>
          </div>
        </transition>

        <p
          v-if="playing"
          class="stroop-word"
          :class="{ 'is-flash': flash }"
          :style="{ color: current.colorHex }"
        >{{ current.wordLabel }}</p>
        <p v-else class="stroop-word stroop-word--ghost">颜色</p>
      </div>

      <div class="stroop-options">
        <button
          v-for="opt in colorSet"
          :key="opt.key"
          type="button"
          class="stroop-opt"
          :class="{ 'is-wrong': wrongKey === opt.key, 'is-right': rightKey === opt.key }"
          :disabled="!playing"
          @click="answer(opt.key)"
        >
          <span class="stroop-swatch" :style="{ background: opt.hex }" />
          {{ opt.label }}
        </button>
      </div>

      <p class="arcade-hint">越快越准越好。反应时间只统计答对的轮次。</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const colorSet = [
  { key: 'red', label: '红', hex: '#d64545' },
  { key: 'blue', label: '蓝', hex: '#3f6fb0' },
  { key: 'green', label: '绿', hex: '#3f9d6a' },
  { key: 'orange', label: '橙', hex: '#e08a1e' },
  { key: 'purple', label: '紫', hex: '#8a5cc4' },
]

const totalRounds = 20
const round = ref(0)
const correct = ref(0)
const reactionSum = ref(0)
const playing = ref(false)
const finished = ref(false)
const flash = ref(false)
const wrongKey = ref(null)
const rightKey = ref(null)
const shownAt = ref(0)

const current = ref({ wordLabel: '', colorKey: '', colorHex: '' })
const bestScores = ref(loadBest())

const avgText = computed(() => (correct.value ? `${Math.round(reactionSum.value / correct.value)}ms` : '--'))
const bestText = computed(() => (bestScores.value.avg ? `${bestScores.value.avg}ms` : '--'))
const isNewBest = ref(false)

function loadBest() {
  try {
    return JSON.parse(localStorage.getItem('arcade-stroop-best') || '{}') || {}
  } catch {
    return {}
  }
}

function nextRound() {
  const word = colorSet[Math.floor(Math.random() * colorSet.length)]
  let color = colorSet[Math.floor(Math.random() * colorSet.length)]
  if (Math.random() < 0.7) {
    while (color.key === word.key) {
      color = colorSet[Math.floor(Math.random() * colorSet.length)]
    }
  }
  current.value = { wordLabel: word.label, colorKey: color.key, colorHex: color.hex }
  flash.value = true
  setTimeout(() => { flash.value = false }, 160)
  shownAt.value = performance.now()
}

function startGame() {
  round.value = 1
  correct.value = 0
  reactionSum.value = 0
  finished.value = false
  isNewBest.value = false
  wrongKey.value = null
  rightKey.value = null
  playing.value = true
  nextRound()
}

function answer(key) {
  if (!playing.value) return
  const rt = performance.now() - shownAt.value
  if (key === current.value.colorKey) {
    correct.value += 1
    reactionSum.value += rt
    rightKey.value = key
    setTimeout(() => { if (rightKey.value === key) rightKey.value = null }, 180)
  } else {
    wrongKey.value = key
    setTimeout(() => { if (wrongKey.value === key) wrongKey.value = null }, 320)
  }
  if (round.value >= totalRounds) {
    finishGame()
  } else {
    round.value += 1
    nextRound()
  }
}

function finishGame() {
  playing.value = false
  finished.value = true
  if (correct.value > 0) {
    const avg = Math.round(reactionSum.value / correct.value)
    const prev = bestScores.value.avg
    const prevCorrect = bestScores.value.correct || 0
    if (correct.value > prevCorrect || (correct.value === prevCorrect && (!prev || avg < prev))) {
      bestScores.value = { avg, correct: correct.value }
      isNewBest.value = true
      try { localStorage.setItem('arcade-stroop-best', JSON.stringify(bestScores.value)) } catch { /* ignore */ }
    }
  }
}

onUnmounted(() => { playing.value = false })
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

.arcade-actions { display: flex; gap: 0.5rem; margin-left: auto; }

.stroop-stage {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 12rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  margin-bottom: 1.2rem;
}

.stroop-word {
  font-family: var(--sans);
  font-weight: 800;
  font-size: clamp(3rem, 12vw, 5.5rem);
  line-height: 1;
  margin: 0;
  user-select: none;
  transition: transform 0.16s ease;
}

.stroop-word.is-flash { transform: scale(1.08); }

.stroop-word--ghost {
  color: var(--border);
}

.stroop-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(6rem, 1fr));
  gap: 0.6rem;
}

.stroop-opt {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.7rem 0.5rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text);
  font-family: var(--mono);
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.12s ease, border-color 0.15s, box-shadow 0.15s;
}

.stroop-opt:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: var(--orange);
}

.stroop-opt:disabled { cursor: default; opacity: 0.6; }

.stroop-opt.is-right {
  border-color: var(--orange);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--orange) 40%, transparent);
}

.stroop-opt.is-wrong {
  border-color: #d64545;
  animation: arcade-shake 0.32s ease;
}

.stroop-swatch {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: inline-block;
}

.arcade-veil {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  text-align: center;
  background: color-mix(in srgb, var(--bg-paper) 88%, transparent);
  backdrop-filter: blur(3px);
  z-index: 2;
}

.arcade-veil-title { font-family: var(--mono); font-size: 1.3rem; margin: 0; }
.arcade-veil-tip { color: var(--text-muted); font-size: 0.85rem; margin: 0; }
.arcade-veil--win .arcade-veil-time {
  font-family: var(--mono);
  font-size: 2rem;
  color: var(--orange);
  margin: 0.2rem 0;
}
.arcade-veil-sub { color: var(--text-muted); font-size: 0.85rem; margin: 0; }
.arcade-veil-best {
  font-family: var(--mono);
  color: var(--orange);
  letter-spacing: 0.08em;
  margin: 0.2rem 0 0.4rem;
  animation: arcade-pop 0.4s ease;
}

.arcade-veil-enter-active,
.arcade-veil-leave-active { transition: opacity 0.25s ease; }
.arcade-veil-enter-from,
.arcade-veil-leave-to { opacity: 0; }

.arcade-hint {
  margin: 1.2rem 0 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
}

@keyframes arcade-pop {
  0% { transform: scale(1); }
  45% { transform: scale(1.12); }
  100% { transform: scale(1); }
}

@keyframes arcade-shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-4px); }
  40% { transform: translateX(4px); }
  60% { transform: translateX(-3px); }
  80% { transform: translateX(3px); }
}

@media (max-width: 560px) {
  .arcade-actions { margin-left: 0; width: 100%; }
}
</style>
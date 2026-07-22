<template>
  <div class="arcade-page platform-page container layout-single">
    <router-link to="/app/arcade" class="arcade-back">← 返回游戏厅</router-link>
    <header class="arcade-hero platform-panel ink-panel">
      <p class="platform-coord">ARCADE · SEQUENCE · MEMORY</p>
      <h1 class="arcade-title">点位序列记忆</h1>
      <p class="arcade-lead">
        方格会<strong>按顺序</strong>一个个亮起，记住它们的先后，再依样点出来。
        每过一关，序列就加长一位 —— 看你能记到第几关。
      </p>
    </header>

    <section class="arcade-body platform-panel ink-panel">
      <div class="arcade-toolbar">
        <div class="arcade-stats">
          <div class="arcade-stat">
            <span class="arcade-stat-label">关卡</span>
            <span class="arcade-stat-value arcade-next">{{ level }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">序列长度</span>
            <span class="arcade-stat-value">{{ sequence.length || '--' }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">最佳</span>
            <span class="arcade-stat-value">{{ best || '--' }}</span>
          </div>
        </div>
        <div class="arcade-actions">
          <button type="button" class="platform-btn-primary" @click="startGame">
            {{ playing ? '重开' : '开始' }}
          </button>
        </div>
      </div>

      <p class="dots-status" :class="phaseClass">{{ statusText }}</p>

      <div class="dots-grid">
        <button
          v-for="i in gridSize * gridSize"
          :key="i"
          type="button"
          class="dots-cell"
          :class="{
            'is-lit': litIndex === (i - 1),
            'is-hit': hitIndex === (i - 1),
            'is-miss': missIndex === (i - 1),
          }"
          :disabled="phase !== 'input'"
          @click="onCellClick(i - 1)"
        />
        <transition name="arcade-veil">
          <div v-if="!playing && !gameOver" class="arcade-veil">
            <p class="arcade-veil-title">准备好了吗？</p>
            <p class="arcade-veil-tip">看清亮灯顺序，再按原顺序点回来</p>
          </div>
        </transition>
        <transition name="arcade-veil">
          <div v-if="gameOver" class="arcade-veil arcade-veil--win">
            <p class="arcade-veil-title">到此为止！</p>
            <p class="arcade-veil-time">第 {{ level }} 关</p>
            <p v-if="isNewBest" class="arcade-veil-best">★ 新纪录</p>
            <button type="button" class="platform-btn-primary" @click="startGame">再来一局</button>
          </div>
        </transition>
      </div>

      <p class="arcade-hint">小提示：把序列想成一条路径或一个形状，比死记位置更好记。</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const gridSize = 3
const level = ref(1)
const sequence = ref([])
const inputPos = ref(0)
const phase = ref('idle')
const playing = ref(false)
const gameOver = ref(false)
const litIndex = ref(null)
const hitIndex = ref(null)
const missIndex = ref(null)
const isNewBest = ref(false)

const best = ref(loadBest())
const timers = []

const phaseClass = computed(() => ({
  'is-show': phase.value === 'show',
  'is-input': phase.value === 'input',
}))

const statusText = computed(() => {
  if (phase.value === 'show') return '记住顺序…'
  if (phase.value === 'input') return `轮到你了 · ${inputPos.value}/${sequence.value.length}`
  if (gameOver.value) return '游戏结束'
  return '点“开始”出题'
})

function loadBest() {
  try { return Number(localStorage.getItem('arcade-dots-best') || 0) } catch { return 0 }
}

function clearTimers() {
  while (timers.length) clearTimeout(timers.pop())
}

function startGame() {
  clearTimers()
  level.value = 1
  sequence.value = []
  gameOver.value = false
  isNewBest.value = false
  playing.value = true
  nextLevel()
}

function nextLevel() {
  const total = gridSize * gridSize
  const next = Math.floor(Math.random() * total)
  const seq = sequence.value.slice()
  seq.push(next)
  sequence.value = seq
  playSequence()
}

function playSequence() {
  phase.value = 'show'
  inputPos.value = 0
  litIndex.value = null
  const step = 640
  sequence.value.forEach((cell, i) => {
    timers.push(setTimeout(() => { litIndex.value = cell }, i * step + 200))
    timers.push(setTimeout(() => { litIndex.value = null }, i * step + 200 + step * 0.62))
  })
  timers.push(setTimeout(() => { phase.value = 'input' }, sequence.value.length * step + 300))
}

function onCellClick(idx) {
  if (phase.value !== 'input') return
  if (idx === sequence.value[inputPos.value]) {
    hitIndex.value = idx
    setTimeout(() => { if (hitIndex.value === idx) hitIndex.value = null }, 200)
    inputPos.value += 1
    if (inputPos.value >= sequence.value.length) {
      level.value += 1
      phase.value = 'idle'
      timers.push(setTimeout(nextLevel, 650))
    }
  } else {
    missIndex.value = idx
    setTimeout(() => { if (missIndex.value === idx) missIndex.value = null }, 400)
    endGame()
  }
}

function endGame() {
  clearTimers()
  phase.value = 'idle'
  playing.value = false
  gameOver.value = true
  const reached = level.value
  if (reached > best.value) {
    best.value = reached
    isNewBest.value = true
    try { localStorage.setItem('arcade-dots-best', String(reached)) } catch { /* ignore */ }
  }
}

onUnmounted(clearTimers)
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
  margin-bottom: 1rem;
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

.dots-status {
  text-align: center;
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 1rem;
  height: 1.2rem;
  transition: color 0.2s;
}
.dots-status.is-show { color: var(--steel); }
.dots-status.is-input { color: var(--orange); }

.dots-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(0.5rem, 2vw, 0.85rem);
  width: min(100%, 26rem);
  margin: 0 auto;
  aspect-ratio: 1 / 1;
}

.dots-cell {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  cursor: pointer;
  transition: transform 0.12s ease, background 0.15s, box-shadow 0.15s, border-color 0.15s;
}

.dots-cell:hover:not(:disabled) {
  border-color: var(--orange);
}

.dots-cell:disabled { cursor: default; }

.dots-cell.is-lit {
  background: var(--steel);
  border-color: var(--steel);
  box-shadow: 0 0 18px color-mix(in srgb, var(--steel) 60%, transparent);
  transform: scale(1.03);
}

.dots-cell.is-hit {
  background: color-mix(in srgb, var(--orange) 30%, var(--bg-paper));
  border-color: var(--orange);
  box-shadow: 0 0 14px color-mix(in srgb, var(--orange) 45%, transparent);
}

.dots-cell.is-miss {
  background: color-mix(in srgb, #d64545 30%, var(--bg-paper));
  border-color: #d64545;
  animation: arcade-shake 0.4s ease;
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
  background: color-mix(in srgb, var(--bg-paper) 84%, transparent);
  backdrop-filter: blur(3px);
  border: 1px solid var(--border);
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
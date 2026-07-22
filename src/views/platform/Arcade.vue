<template>
  <div class="arcade-page platform-page container layout-single">
    <header class="arcade-hero platform-panel ink-panel">
      <p class="platform-coord">ARCADE · SCHULTE · FOCUS</p>
      <h1 class="arcade-title">奇怪的游戏厅</h1>
      <p class="arcade-lead">
        舒尔特方格 —— 按 <strong>1 → {{ size * size }}</strong> 的顺序，尽可能快地依次点击。
        经典的注意力与视觉搜索小训练。
      </p>
    </header>

    <section class="arcade-body platform-panel ink-panel">
      <div class="arcade-toolbar">
        <div class="arcade-sizes">
          <span class="arcade-field-label">阶数</span>
          <button
            v-for="n in sizeOptions"
            :key="n"
            type="button"
            class="arcade-size-btn"
            :class="{ 'is-active': size === n }"
            @click="changeSize(n)"
          >{{ n }}×{{ n }}</button>
        </div>

        <div class="arcade-stats">
          <div class="arcade-stat">
            <span class="arcade-stat-label">用时</span>
            <span class="arcade-stat-value">{{ elapsedText }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">下一个</span>
            <span class="arcade-stat-value arcade-next">{{ finished ? '✓' : nextNumber }}</span>
          </div>
          <div class="arcade-stat">
            <span class="arcade-stat-label">最佳</span>
            <span class="arcade-stat-value">{{ bestText }}</span>
          </div>
        </div>

        <div class="arcade-actions">
          <button type="button" class="platform-btn-primary" @click="startGame">
            {{ started && !finished ? '重开' : '开始' }}
          </button>
        </div>
      </div>

      <div
        class="arcade-grid"
        :class="{ 'is-idle': !started, 'is-done': finished }"
        :style="{ '--cols': size }"
      >
        <button
          v-for="(cell, idx) in cells"
          :key="idx"
          type="button"
          class="arcade-cell"
          :class="{
            'is-cleared': cell < nextNumber && started,
            'is-shake': shakeCell === cell,
            'is-pop': popCell === cell,
          }"
          :disabled="!started || finished"
          @click="onCellClick(cell)"
        >
          <span class="arcade-cell-num">{{ cell }}</span>
        </button>

        <transition name="arcade-veil">
          <div v-if="!started" class="arcade-veil">
            <p class="arcade-veil-title">准备好了吗？</p>
            <p class="arcade-veil-tip">点击「开始」，从 1 依次点到 {{ size * size }}</p>
          </div>
        </transition>

        <transition name="arcade-veil">
          <div v-if="finished" class="arcade-veil arcade-veil--win">
            <p class="arcade-veil-title">完成！</p>
            <p class="arcade-veil-time">{{ elapsedText }}</p>
            <p v-if="isNewBest" class="arcade-veil-best">★ 新纪录</p>
            <button type="button" class="platform-btn-primary" @click="startGame">再来一局</button>
          </div>
        </transition>
      </div>

      <p class="arcade-hint">小提示：视线尽量固定在方格中央，用余光去搜索下一个数字。</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const sizeOptions = [3, 4, 5, 6]
const size = ref(5)
const cells = ref([])
const nextNumber = ref(1)
const started = ref(false)
const finished = ref(false)
const shakeCell = ref(null)
const popCell = ref(null)

const startAt = ref(0)
const elapsedMs = ref(0)
const isNewBest = ref(false)
let timer = null

const bestScores = ref(loadBest())

const elapsedText = computed(() => formatMs(elapsedMs.value))
const bestText = computed(() => {
  const v = bestScores.value[size.value]
  return v ? formatMs(v) : '--'
})

function formatMs(ms) {
  const s = Math.floor(ms / 1000)
  const cs = Math.floor((ms % 1000) / 10)
  return `${s}.${String(cs).padStart(2, '0')}s`
}

function loadBest() {
  try {
    return JSON.parse(localStorage.getItem('arcade-schulte-best') || '{}') || {}
  } catch {
    return {}
  }
}

function saveBest() {
  try {
    localStorage.setItem('arcade-schulte-best', JSON.stringify(bestScores.value))
  } catch {
    /* ignore */
  }
}

function shuffle(n) {
  const arr = Array.from({ length: n }, (_, i) => i + 1)
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function changeSize(n) {
  if (size.value === n) return
  size.value = n
  resetBoard()
}

function resetBoard() {
  stopTimer()
  cells.value = shuffle(size.value * size.value)
  nextNumber.value = 1
  started.value = false
  finished.value = false
  elapsedMs.value = 0
  isNewBest.value = false
}

function startGame() {
  cells.value = shuffle(size.value * size.value)
  nextNumber.value = 1
  finished.value = false
  isNewBest.value = false
  started.value = true
  startAt.value = performance.now()
  elapsedMs.value = 0
  stopTimer()
  timer = setInterval(() => {
    elapsedMs.value = performance.now() - startAt.value
  }, 50)
}

function onCellClick(cell) {
  if (!started.value || finished.value) return
  if (cell === nextNumber.value) {
    popCell.value = cell
    setTimeout(() => {
      if (popCell.value === cell) popCell.value = null
    }, 220)
    nextNumber.value += 1
    if (nextNumber.value > size.value * size.value) {
      finishGame()
    }
  } else {
    shakeCell.value = cell
    setTimeout(() => {
      if (shakeCell.value === cell) shakeCell.value = null
    }, 320)
  }
}

function finishGame() {
  stopTimer()
  elapsedMs.value = performance.now() - startAt.value
  finished.value = true
  const prev = bestScores.value[size.value]
  if (!prev || elapsedMs.value < prev) {
    bestScores.value = { ...bestScores.value, [size.value]: Math.round(elapsedMs.value) }
    isNewBest.value = true
    saveBest()
  }
}

resetBoard()

onUnmounted(stopTimer)
</script>

<style scoped>
.arcade-hero {
  text-align: left;
}

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

.arcade-lead strong {
  color: var(--orange);
}

.arcade-body {
  margin-top: 1rem;
}

.arcade-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem 1.5rem;
  padding-bottom: 1.1rem;
  margin-bottom: 1.2rem;
  border-bottom: 1px dashed var(--border);
}

.arcade-field-label,
.arcade-stat-label {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.arcade-sizes {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.arcade-size-btn {
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.arcade-size-btn:hover {
  border-color: var(--orange);
  color: var(--orange);
}

.arcade-size-btn.is-active {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.arcade-stats {
  display: flex;
  gap: 1.5rem;
  margin-left: auto;
}

.arcade-stat {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.arcade-stat-value {
  font-family: var(--mono);
  font-size: 1.15rem;
  font-variant-numeric: tabular-nums;
}

.arcade-next {
  color: var(--orange);
}

.arcade-actions {
  display: flex;
  gap: 0.5rem;
}

.arcade-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(var(--cols), 1fr);
  gap: clamp(0.35rem, 1.2vw, 0.6rem);
  width: min(100%, 32rem);
  margin: 0 auto;
  aspect-ratio: 1 / 1;
}

.arcade-cell {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text);
  font-family: var(--mono);
  font-size: clamp(1rem, 4vw, 1.6rem);
  font-variant-numeric: tabular-nums;
  cursor: pointer;
  user-select: none;
  transition: transform 0.12s ease, border-color 0.15s, background 0.15s, color 0.15s, box-shadow 0.15s;
}

.arcade-cell:hover:not(:disabled) {
  border-color: var(--orange);
  color: var(--orange);
  transform: translateY(-1px);
}

.arcade-cell:disabled {
  cursor: default;
}

.arcade-cell.is-cleared {
  background: color-mix(in srgb, var(--orange) 14%, var(--bg-paper));
  border-color: color-mix(in srgb, var(--orange) 35%, var(--border));
  color: color-mix(in srgb, var(--orange) 70%, var(--text-muted));
  opacity: 0.55;
}

.arcade-cell.is-pop {
  animation: arcade-pop 0.22s ease;
  border-color: var(--orange);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--orange) 40%, transparent);
}

.arcade-cell.is-shake {
  animation: arcade-shake 0.32s ease;
  border-color: #d64545;
  color: #d64545;
}

.arcade-grid.is-idle .arcade-cell,
.arcade-grid.is-done .arcade-cell {
  filter: blur(2px);
  opacity: 0.5;
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

.arcade-veil {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  text-align: center;
  background: color-mix(in srgb, var(--bg-paper) 82%, transparent);
  backdrop-filter: blur(3px);
  border: 1px solid var(--border);
}

.arcade-veil-title {
  font-family: var(--mono);
  font-size: 1.3rem;
  margin: 0;
}

.arcade-veil-tip {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin: 0;
}

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
  margin: 0 0 0.4rem;
  animation: arcade-pop 0.4s ease;
}

.arcade-veil-enter-active,
.arcade-veil-leave-active {
  transition: opacity 0.25s ease;
}

.arcade-veil-enter-from,
.arcade-veil-leave-to {
  opacity: 0;
}

.arcade-hint {
  margin: 1.2rem 0 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
}

@media (max-width: 560px) {
  .arcade-stats {
    width: 100%;
    margin-left: 0;
    justify-content: space-between;
    gap: 0.75rem;
  }
}
</style>
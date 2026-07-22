<template>
  <div class="arcade-page platform-page container layout-single">
    <router-link to="/app/arcade" class="arcade-back">← 返回游戏厅</router-link>
    <header class="arcade-hero platform-panel ink-panel">
      <p class="platform-coord">ARCADE · SIZE · CONGRUITY</p>
      <h1 class="arcade-title">数值·字号冲突</h1>
      <p class="arcade-lead">
        两个数字，请一直选<strong>数值更大</strong>的那个。但字号常常故意反着来 ——
        数值大的字偏小、数值小的字偏大，大脑会被视觉大小带偏。
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

      <div class="size-stage">
        <transition name="arcade-veil">
          <div v-if="!playing && !finished" class="arcade-veil">
            <p class="arcade-veil-title">准备好了吗？</p>
            <p class="arcade-veil-tip">共 {{ totalRounds }} 轮，选“数值大”的，别看字号</p>
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

        <button
          v-for="(pair, side) in pairView"
          :key="side"
          type="button"
          class="size-choice"
          :class="{ 'is-right': rightSide === side, 'is-wrong': wrongSide === side }"
          :disabled="!playing"
          @click="answer(side)"
        >
          <span class="size-num" :style="{ fontSize: pair.fontSize }">{{ pair.value }}</span>
        </button>
      </div>

      <p class="arcade-hint">数值-字号一致时最好答；冲突时你会明显慢一拍，这就是「尺寸一致性效应」。</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const totalRounds = 20
const round = ref(0)
const correct = ref(0)
const reactionSum = ref(0)
const playing = ref(false)
const finished = ref(false)
const rightSide = ref(null)
const wrongSide = ref(null)
const shownAt = ref(0)
const isNewBest = ref(false)

const pair = ref([{ value: 0, fontSize: '3rem' }, { value: 0, fontSize: '3rem' }])
const bigSide = ref(0)
const best = ref(loadBest())

const pairView = computed(() => pair.value)
const avgText = computed(() => (correct.value ? `${Math.round(reactionSum.value / correct.value)}ms` : '--'))
const bestText = computed(() => (best.value.avg ? `${best.value.avg}ms` : '--'))

function loadBest() {
  try { return JSON.parse(localStorage.getItem('arcade-size-best') || '{}') || {} } catch { return {} }
}

const FONTS = ['2.2rem', '3rem', '3.8rem', '4.8rem', '5.8rem']

function nextRound() {
  let a = Math.floor(Math.random() * 9) + 1
  let b = Math.floor(Math.random() * 9) + 1
  while (b === a) b = Math.floor(Math.random() * 9) + 1
  const big = a > b ? 0 : 1
  bigSide.value = big
  const smallFontIdx = Math.floor(Math.random() * 2)
  const bigFontIdx = FONTS.length - 1 - Math.floor(Math.random() * 2)
  let fontBig
  let fontSmall
  if (Math.random() < 0.68) {
    fontBig = FONTS[smallFontIdx]
    fontSmall = FONTS[bigFontIdx]
  } else {
    fontBig = FONTS[bigFontIdx]
    fontSmall = FONTS[smallFontIdx]
  }
  const values = [a, b]
  pair.value = [
    { value: values[0], fontSize: big === 0 ? fontBig : fontSmall },
    { value: values[1], fontSize: big === 1 ? fontBig : fontSmall },
  ]
  shownAt.value = performance.now()
}

function startGame() {
  round.value = 1
  correct.value = 0
  reactionSum.value = 0
  finished.value = false
  isNewBest.value = false
  rightSide.value = null
  wrongSide.value = null
  playing.value = true
  nextRound()
}

function answer(side) {
  if (!playing.value) return
  const rt = performance.now() - shownAt.value
  if (side === bigSide.value) {
    correct.value += 1
    reactionSum.value += rt
    rightSide.value = side
    setTimeout(() => { if (rightSide.value === side) rightSide.value = null }, 160)
  } else {
    wrongSide.value = side
    setTimeout(() => { if (wrongSide.value === side) wrongSide.value = null }, 320)
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
    const prevCorrect = best.value.correct || 0
    const prevAvg = best.value.avg
    if (correct.value > prevCorrect || (correct.value === prevCorrect && (!prevAvg || avg < prevAvg))) {
      best.value = { avg, correct: correct.value }
      isNewBest.value = true
      try { localStorage.setItem('arcade-size-best', JSON.stringify(best.value)) } catch { /* ignore */ }
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

.size-stage {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  min-height: 14rem;
}

.size-choice {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text);
  cursor: pointer;
  min-height: 14rem;
  transition: transform 0.12s ease, border-color 0.15s, box-shadow 0.15s;
}
.size-choice:hover:not(:disabled) {
  border-color: var(--orange);
  transform: translateY(-2px);
}
.size-choice:disabled { cursor: default; }
.size-choice.is-right {
  border-color: var(--orange);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--orange) 40%, transparent);
}
.size-choice.is-wrong {
  border-color: #d64545;
  animation: arcade-shake 0.32s ease;
}

.size-num {
  font-family: var(--mono);
  font-weight: 700;
  line-height: 1;
  transition: font-size 0.15s ease;
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
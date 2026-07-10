<template>
  <div
    ref="roomRef"
    class="pomo-study-room"
    :class="{
      'pomo-study-room--focus': mode === 'focus',
      'pomo-study-room--break': mode === 'break',
      'pomo-study-room--running': running,
    }"
    :style="roomStyle"
  >
    <div class="pomo-study-room__bg" :style="{ backgroundImage: `url(${companionImg})` }" aria-hidden="true" />
    <div class="pomo-study-room__embers" aria-hidden="true" />
    <div class="pomo-study-room__vignette" aria-hidden="true" />

    <header class="pomo-study-room__head">
      <div class="pomo-study-room__brand">
        <p class="pomo-study-room__eyebrow">CYINC · STUDY ROOM</p>
        <h1 class="pomo-study-room__title">Study With {{ companion.name }}</h1>
        <p class="pomo-study-room__subtitle">{{ companion.series }}</p>
      </div>
      <div class="pomo-study-room__head-actions">
        <time class="pomo-study-room__clock" :datetime="clockIso">{{ wallClock }}</time>
        <button type="button" class="study-btn" @click="$emit('switch-scene')">切换</button>
        <button type="button" class="study-btn" @click="$emit('toggle-fullscreen')">全屏</button>
        <button type="button" class="study-btn study-btn--ghost" @click="$emit('close')">退出</button>
      </div>
    </header>

    <main class="pomo-study-room__stage">
      <div class="pomo-study-room__timer-zone">
        <span class="pomo-study-room__round" aria-label="已完成专注轮数">{{ focusCount }}</span>
        <button
          type="button"
          class="pomo-study-room__time"
          :class="{ 'is-running': running }"
          @click="$emit('toggle-timer')"
        >
          {{ displayTime }}
        </button>
        <p class="pomo-study-room__mode">{{ modeLabel }}</p>
        <p v-if="taskLabel" class="pomo-study-room__task">{{ taskLabel }}</p>
        <p class="pomo-study-room__hint">点击时间 · 开始 / 暂停</p>
        <div class="pomo-study-room__controls">
          <button type="button" class="study-btn study-btn--primary" @click="$emit('toggle-timer')">
            {{ running ? '暂停' : secondsLeft === totalSeconds ? '开始' : '继续' }}
          </button>
          <button type="button" class="study-btn study-btn--ghost" @click="$emit('reset')">重置</button>
          <button type="button" class="study-btn study-btn--ghost" @click="$emit('switch-mode')">
            {{ mode === 'focus' ? '休息' : '专注' }}
          </button>
        </div>
      </div>

      <figure class="pomo-study-room__character">
        <img :src="companionImg" :alt="companion.name" />
        <figcaption>{{ companionLine }}</figcaption>
      </figure>
    </main>

    <aside class="pomo-study-room__side">
      <button
        type="button"
        class="pomo-study-room__side-toggle"
        :aria-expanded="memoOpen"
        @click="memoOpen = !memoOpen"
      >
        {{ memoOpen ? '收起备忘' : '自习备忘' }}
      </button>
      <div v-show="memoOpen" class="pomo-study-room__memo">
        <textarea
          :value="memo"
          rows="5"
          maxlength="500"
          placeholder="随手记一点…（仅保存在本机）"
          @input="$emit('update:memo', ($event.target).value)"
        />
      </div>
    </aside>

    <footer class="pomo-study-room__bar">
      <button type="button" class="pomo-study-room__music" @click="$emit('toggle-ambient')">
        <span class="pomo-study-room__music-icon">{{ ambientPlaying ? '❚❚' : '♫' }}</span>
        <span class="pomo-study-room__music-text">{{ ambientLabel }}</span>
      </button>
      <p class="pomo-study-room__credit">参考 Study with Miku 自习室体验 · CYINC 版</p>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  companion: { type: Object, required: true },
  companionImg: { type: String, required: true },
  companionLine: { type: String, default: '' },
  displayTime: { type: String, required: true },
  mode: { type: String, required: true },
  modeLabel: { type: String, required: true },
  focusCount: { type: Number, default: 0 },
  running: { type: Boolean, default: false },
  secondsLeft: { type: Number, default: 0 },
  totalSeconds: { type: Number, default: 0 },
  taskLabel: { type: String, default: '' },
  ambientLabel: { type: String, default: '氛围音 · 关' },
  ambientPlaying: { type: Boolean, default: false },
  memo: { type: String, default: '' },
})

defineEmits([
  'close',
  'switch-scene',
  'toggle-fullscreen',
  'toggle-timer',
  'reset',
  'switch-mode',
  'toggle-ambient',
  'update:memo',
])

const roomRef = ref(null)
const memoOpen = ref(false)
const wallClock = ref('--:--')
const clockIso = ref('')
let clockId = null

const roomStyle = computed(() => ({
  '--study-accent': props.companion.accent,
  '--study-bg': props.companion.sceneGradient || '#0a0a0c',
}))

function tickClock() {
  const now = new Date()
  wallClock.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
  clockIso.value = now.toISOString()
}

onMounted(() => {
  tickClock()
  clockId = setInterval(tickClock, 1000)
})

onUnmounted(() => {
  if (clockId) clearInterval(clockId)
})

defineExpose({ roomRef })
</script>

<style scoped>
.pomo-study-room {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 1fr auto;
  background: var(--study-bg, #0a0a0c);
  color: #f2f2f2;
  overflow: hidden;
  font-family: var(--mono, ui-monospace, monospace);
}

.pomo-study-room__bg {
  position: absolute;
  inset: -8%;
  background-size: cover;
  background-position: 70% bottom;
  opacity: 0.14;
  filter: saturate(0.85) blur(1px);
  pointer-events: none;
}

.pomo-study-room__embers {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(circle at 18% 82%, color-mix(in srgb, var(--study-accent) 45%, transparent) 0 2px, transparent 3px),
    radial-gradient(circle at 72% 68%, color-mix(in srgb, var(--study-accent) 35%, transparent) 0 2px, transparent 3px),
    radial-gradient(circle at 44% 90%, rgba(255, 180, 100, 0.35) 0 1px, transparent 2px),
    radial-gradient(circle at 88% 42%, color-mix(in srgb, var(--study-accent) 25%, transparent) 0 2px, transparent 3px);
  animation: study-ember 8s ease-in-out infinite;
}

.pomo-study-room--running .pomo-study-room__embers {
  animation-duration: 5s;
  opacity: 0.9;
}

@keyframes study-ember {
  0%, 100% { transform: translateY(0); opacity: 0.55; }
  50% { transform: translateY(-6px); opacity: 0.85; }
}

.pomo-study-room__vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(ellipse 90% 80% at 50% 50%, transparent 40%, rgba(0, 0, 0, 0.65) 100%);
}

.pomo-study-room__head {
  position: relative;
  z-index: 2;
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem clamp(1rem, 3vw, 2rem) 0.5rem;
}

.pomo-study-room__eyebrow {
  margin: 0;
  font-size: 0.62rem;
  letter-spacing: 0.16em;
  color: color-mix(in srgb, var(--study-accent) 80%, #fff);
  opacity: 0.85;
}

.pomo-study-room__title {
  margin: 0.25rem 0 0;
  font-size: clamp(1.35rem, 3vw, 1.85rem);
  font-weight: 600;
  letter-spacing: 0.04em;
}

.pomo-study-room__subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.55);
}

.pomo-study-room__head-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  justify-content: flex-end;
  align-items: center;
}

.pomo-study-room__clock {
  font-size: clamp(1rem, 2vw, 1.25rem);
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.72);
  margin-right: 0.35rem;
}

.pomo-study-room__stage {
  position: relative;
  z-index: 2;
  grid-column: 1;
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(200px, 42vw);
  align-items: end;
  gap: clamp(0.5rem, 4vw, 2rem);
  padding: 0 clamp(1rem, 4vw, 3rem) clamp(1rem, 3vh, 2rem);
  min-height: 0;
}

.pomo-study-room__timer-zone {
  align-self: center;
  text-align: left;
  padding-bottom: 8vh;
}

.pomo-study-room__round {
  display: block;
  font-size: clamp(1.5rem, 4vw, 2.25rem);
  color: rgba(255, 255, 255, 0.45);
  line-height: 1;
  margin-bottom: 0.35rem;
}

.pomo-study-room__time {
  display: block;
  margin: 0;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  font: inherit;
  font-size: clamp(3.5rem, 14vw, 7.5rem);
  font-weight: 300;
  letter-spacing: 0.06em;
  line-height: 1;
  color: #fff;
  text-shadow: 0 0 40px color-mix(in srgb, var(--study-accent) 35%, transparent);
  transition: transform 0.15s ease, color 0.15s ease;
}

.pomo-study-room__time:hover {
  transform: scale(1.02);
  color: color-mix(in srgb, var(--study-accent) 30%, #fff);
}

.pomo-study-room__time.is-running {
  color: color-mix(in srgb, var(--study-accent) 25%, #fff);
}

.pomo-study-room__mode {
  margin: 0.5rem 0 0;
  font-size: clamp(0.95rem, 2vw, 1.15rem);
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.7);
}

.pomo-study-room__task {
  margin: 0.45rem 0 0;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.5);
  max-width: 28ch;
}

.pomo-study-room__hint {
  margin: 0.65rem 0 0;
  font-size: 0.62rem;
  color: rgba(255, 255, 255, 0.35);
  letter-spacing: 0.06em;
}

.pomo-study-room__controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 1.25rem;
}

.pomo-study-room__character {
  margin: 0;
  align-self: flex-end;
  text-align: center;
  max-height: min(72vh, 680px);
}

.pomo-study-room__character img {
  display: block;
  max-height: min(68vh, 640px);
  width: auto;
  max-width: 100%;
  margin-inline: auto;
  object-fit: contain;
  filter: drop-shadow(0 12px 48px rgba(0, 0, 0, 0.55));
  animation: study-breathe 6s ease-in-out infinite;
}

.pomo-study-room--running .pomo-study-room__character img {
  animation-duration: 4s;
}

@keyframes study-breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.pomo-study-room__character figcaption {
  margin-top: 0.65rem;
  font-size: 0.78rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.55);
  max-width: 36ch;
  margin-inline: auto;
}

.pomo-study-room__side {
  position: relative;
  z-index: 2;
  grid-column: 2;
  grid-row: 2;
  align-self: end;
  padding: 0 1rem 5rem 0;
  max-width: 220px;
}

.pomo-study-room__side-toggle {
  width: 100%;
  padding: 0.45rem 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.35);
  color: rgba(255, 255, 255, 0.75);
  font: inherit;
  font-size: 0.68rem;
  cursor: pointer;
}

.pomo-study-room__side-toggle:hover {
  border-color: color-mix(in srgb, var(--study-accent) 50%, transparent);
  color: #fff;
}

.pomo-study-room__memo {
  margin-top: 0.45rem;
}

.pomo-study-room__memo textarea {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(0, 0, 0, 0.45);
  color: rgba(255, 255, 255, 0.85);
  padding: 0.55rem;
  font: inherit;
  font-size: 0.72rem;
  resize: vertical;
}

.pomo-study-room__bar {
  position: relative;
  z-index: 2;
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.65rem clamp(1rem, 3vw, 2rem) 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.35);
}

.pomo-study-room__music {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.35rem 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.85);
  font: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  max-width: min(420px, 70vw);
}

.pomo-study-room__music:hover {
  border-color: color-mix(in srgb, var(--study-accent) 45%, transparent);
}

.pomo-study-room__music-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pomo-study-room__credit {
  margin: 0;
  font-size: 0.58rem;
  color: rgba(255, 255, 255, 0.35);
  letter-spacing: 0.04em;
}

.study-btn {
  padding: 0.4rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  font: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.study-btn:hover {
  border-color: color-mix(in srgb, var(--study-accent) 55%, transparent);
  background: rgba(255, 255, 255, 0.1);
}

.study-btn--primary {
  background: color-mix(in srgb, var(--study-accent) 35%, rgba(255, 255, 255, 0.08));
  border-color: color-mix(in srgb, var(--study-accent) 50%, transparent);
}

.study-btn--ghost {
  background: transparent;
}

@media (max-width: 820px) {
  .pomo-study-room {
    grid-template-columns: 1fr;
  }

  .pomo-study-room__head {
    padding-top: 0.85rem;
  }

  .pomo-study-room__head-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .pomo-study-room__clock {
    width: 100%;
    margin: 0 0 0.25rem;
  }

  .pomo-study-room__stage {
    grid-template-columns: 1fr;
    text-align: center;
    padding-bottom: 0.5rem;
  }

  .pomo-study-room__timer-zone {
    text-align: center;
    padding-bottom: 0.5rem;
  }

  .pomo-study-room__controls {
    justify-content: center;
  }

  .pomo-study-room__character {
    max-height: 38vh;
  }

  .pomo-study-room__character img {
    max-height: 34vh;
  }

  .pomo-study-room__side {
    grid-column: 1;
    grid-row: auto;
    max-width: none;
    padding: 0 1rem 0.75rem;
  }

  .pomo-study-room__bar {
    flex-direction: column;
    align-items: stretch;
  }

  .pomo-study-room__credit {
    text-align: center;
  }
}
</style>

<template>
  <transition name="onb-fade">
    <div v-if="visible" class="onb-mask" @click.self="skip">
      <div class="onb-card platform-panel" role="dialog" aria-modal="true" aria-label="进站指引">
        <button type="button" class="onb-close" aria-label="关闭" @click="skip">✕</button>

        <p class="onb-coord">GUIDE · {{ step + 1 }} / {{ steps.length }}</p>

        <transition :name="dir === 'next' ? 'onb-slide-next' : 'onb-slide-prev'" mode="out-in">
          <div :key="step" class="onb-step">
            <span class="onb-glyph" aria-hidden="true">{{ current.glyph }}</span>
            <h2 class="onb-title">{{ current.title }}</h2>
            <p class="onb-desc">{{ current.desc }}</p>
            <router-link
              v-if="current.to"
              :to="current.to"
              class="platform-btn-ghost onb-jump"
              @click="finish"
            >{{ current.linkText }} →</router-link>
          </div>
        </transition>

        <div class="onb-dots" aria-hidden="true">
          <span
            v-for="(s, i) in steps"
            :key="i"
            class="onb-dot"
            :class="{ 'is-active': i === step }"
            @click="goto(i)"
          />
        </div>

        <div class="onb-actions">
          <button type="button" class="onb-skip" @click="skip">不用了，直接逛</button>
          <div class="onb-nav">
            <button
              v-if="step > 0"
              type="button"
              class="platform-btn-ghost"
              @click="prev"
            >上一步</button>
            <button
              v-if="step < steps.length - 1"
              type="button"
              class="platform-btn-primary"
              @click="next"
            >下一步</button>
            <button
              v-else
              type="button"
              class="platform-btn-primary"
              @click="finish"
            >开始逛逛</button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const STORAGE_KEY = 'platform-onboarding-v1'

const steps = [
  {
    glyph: '⌂',
    title: '欢迎来到 CYINC 主站',
    desc: '这里是我的个人小天地 —— 有社区论坛、音乐室、番茄钟，还有一间奇怪的游戏厅。花一分钟看看都有什么吧。',
  },
  {
    glyph: '☷',
    title: '论坛 · 随便聊聊',
    desc: '最热闹的地方。看帖、发帖、点赞、评论，也能翻翻别人的主页。想认识我或者留个言，从这儿开始最合适。',
    to: '/app/forum',
    linkText: '去论坛看看',
  },
  {
    glyph: '♫',
    title: '音乐室 & 番茄钟',
    desc: '音乐室能边听边逛；番茄钟帮你专注学习工作。都是我自己在用的小工具。',
    to: '/app/music',
    linkText: '进音乐室',
  },
  {
    glyph: '◈',
    title: '奇怪的游戏厅',
    desc: '一堆冷门的认知小游戏：舒尔特方格、斯特鲁普测试、反应速度……测测你的注意力和反应力，放松一下。',
    to: '/app/arcade',
    linkText: '去玩两把',
  },
  {
    glyph: '✎',
    title: '也欢迎逛逛博客',
    desc: '想看我写的技术笔记和折腾记录，随时可以从侧栏「返回博客」。逛开心就好，欢迎常来！',
    to: '/',
    linkText: '看看博客',
  },
]

const visible = ref(false)
const step = ref(0)
const dir = ref('next')

const current = computed(() => steps[step.value])

function markDone() {
  try { localStorage.setItem(STORAGE_KEY, '1') } catch { /* ignore */ }
}

function next() {
  if (step.value < steps.length - 1) {
    dir.value = 'next'
    step.value += 1
  }
}

function prev() {
  if (step.value > 0) {
    dir.value = 'prev'
    step.value -= 1
  }
}

function goto(i) {
  dir.value = i > step.value ? 'next' : 'prev'
  step.value = i
}

function skip() {
  visible.value = false
  markDone()
}

function finish() {
  visible.value = false
  markDone()
}

function open() {
  step.value = 0
  dir.value = 'next'
  visible.value = true
}

onMounted(() => {
  let seen = false
  try { seen = localStorage.getItem(STORAGE_KEY) === '1' } catch { seen = false }
  if (!seen) {
    setTimeout(() => { visible.value = true }, 600)
  }
  window.addEventListener('platform-open-onboarding', open)
})

defineExpose({ open })
</script>

<style scoped>
.onb-mask {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.2rem;
  background: color-mix(in srgb, #000 55%, transparent);
  backdrop-filter: blur(4px);
}

.onb-card {
  position: relative;
  width: min(30rem, 100%);
  padding: 1.6rem 1.5rem 1.3rem;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.28);
}

.onb-close {
  position: absolute;
  top: 0.7rem;
  right: 0.7rem;
  width: 28px;
  height: 28px;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  transition: color 0.15s, border-color 0.15s;
}
.onb-close:hover { color: var(--orange); border-color: var(--orange); }

.onb-coord {
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin: 0 0 0.9rem;
}

.onb-step {
  min-height: 9.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.onb-glyph {
  font-family: var(--mono);
  font-size: 2.2rem;
  line-height: 1;
  color: var(--orange);
}

.onb-title {
  font-family: var(--mono);
  font-size: 1.25rem;
  margin: 0.1rem 0 0;
}

.onb-desc {
  color: var(--text-muted);
  line-height: 1.75;
  font-size: 0.9rem;
  margin: 0;
}

.onb-jump {
  margin-top: 0.35rem;
}

.onb-dots {
  display: flex;
  gap: 0.4rem;
  justify-content: center;
  margin: 1.1rem 0;
}

.onb-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border);
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}
.onb-dot.is-active { background: var(--orange); transform: scale(1.25); }

.onb-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.onb-skip {
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.3rem 0;
  transition: color 0.15s;
}
.onb-skip:hover { color: var(--orange); }

.onb-nav { display: flex; gap: 0.5rem; margin-left: auto; }

.onb-fade-enter-active,
.onb-fade-leave-active { transition: opacity 0.3s ease; }
.onb-fade-enter-from,
.onb-fade-leave-to { opacity: 0; }

.onb-slide-next-enter-active,
.onb-slide-prev-enter-active { transition: opacity 0.22s ease, transform 0.22s ease; }
.onb-slide-next-leave-active,
.onb-slide-prev-leave-active { transition: opacity 0.16s ease, transform 0.16s ease; }
.onb-slide-next-enter-from { opacity: 0; transform: translateX(18px); }
.onb-slide-next-leave-to { opacity: 0; transform: translateX(-18px); }
.onb-slide-prev-enter-from { opacity: 0; transform: translateX(-18px); }
.onb-slide-prev-leave-to { opacity: 0; transform: translateX(18px); }

@media (max-width: 480px) {
  .onb-actions { flex-direction: column-reverse; align-items: stretch; }
  .onb-nav { margin-left: 0; justify-content: flex-end; }
  .onb-skip { text-align: center; }
}
</style>
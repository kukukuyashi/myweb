<template>
  <section class="pomo-task-list platform-panel ink-panel reveal-item" data-reveal>
    <header class="panel-head">
      <h2>今日任务与目标</h2>
      <p class="panel-sub">TODAY · 計画</p>
    </header>

    <div class="task-summary">
      <div class="goal-ring" :class="{ 'goal-ring--done': todayDone >= dailyGoal }">
        <svg viewBox="0 0 48 48" class="goal-ring__svg" aria-hidden="true">
          <circle cx="24" cy="24" r="20" class="goal-ring__bg" />
          <circle
            cx="24" cy="24" r="20"
            class="goal-ring__fg"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="ringOffset"
          />
        </svg>
        <div class="goal-ring__center">
          <span class="goal-ring__num">{{ todayDone }}</span>
          <span class="goal-ring__sep">/</span>
          <span class="goal-ring__goal">{{ dailyGoal }}</span>
        </div>
      </div>
      <div class="goal-meta">
        <p class="goal-meta__line">
          今日目标：
          <button v-if="!editingGoal" type="button" class="goal-edit" @click="startEditGoal" title="修改">✎</button>
          <input
            v-else
            ref="goalInputRef"
            v-model.number="goalDraft"
            type="number" min="1" max="20"
            class="goal-input"
            @keydown.enter="commitGoal"
            @keydown.esc="cancelEditGoal"
            @blur="commitGoal"
          />
          <span v-if="!editingGoal" class="goal-num">{{ dailyGoal }}</span>
          <span v-else class="goal-suffix">个番茄</span>
        </p>
        <p v-if="todayDone >= dailyGoal" class="goal-meta__line goal-meta__line--done">
          ✅ 今日目标已达成
        </p>
        <p v-else class="goal-meta__hint">还差 {{ Math.max(0, dailyGoal - todayDone) }} 个番茄</p>
      </div>
    </div>

    <ul class="task-items" v-if="tasks.length">
      <li
        v-for="t in tasks"
        :key="t.id"
        class="task-item"
        :class="{ 'task-item--done': t.done, 'task-item--selected': t.id === selectedId }"
      >
        <button type="button" class="task-check" :aria-label="t.done ? 'mark' : 'mark'" @click="emit('toggle', t.id)">
          <span v-if="t.done">✓</span>
        </button>
        <button type="button" class="task-text" @click="emit('select', t.id === selectedId ? null : t.id)">
          <span class="task-text__title">{{ t.text }}</span>
          <span class="task-text__meta">
            <span v-if="t.pomodoros" class="task-text__count">{{ t.pomodoros }} 番茄</span>
            <span v-if="t.id === selectedId" class="task-text__bind" title="将绑到下次">●</span>
          </span>
        </button>
        <button type="button" class="task-remove" aria-label="del" @click="emit('remove', t.id)">×</button>
      </li>
    </ul>
    <p v-else class="task-empty">还没有任务。点下方添加一个。</p>

    <form class="task-add" @submit.prevent="submitAdd">
      <input
        v-model="draft"
        maxlength="80"
        placeholder="加一个任务（例：写 5 题 LeetCode）"
        aria-label="new"
      />
      <button type="submit" class="platform-btn-ghost" :disabled="!draft.trim()">添加</button>
    </form>
  </section>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'

const props = defineProps({
  tasks: { type: Array, required: true },
  selectedId: { type: [Number, null], default: null },
  dailyGoal: { type: Number, required: true },
  todayDone: { type: Number, required: true },
})

const emit = defineEmits(['add', 'toggle', 'remove', 'select', 'change-goal'])

const draft = ref('')
const editingGoal = ref(false)
const goalDraft = ref(props.dailyGoal)
const goalInputRef = ref(null)

const circumference = 2 * Math.PI * 20
const ringOffset = computed(() => {
  if (props.dailyGoal <= 0) return circumference
  const ratio = Math.min(1, props.todayDone / props.dailyGoal)
  return circumference * (1 - ratio)
})

function submitAdd() {
  const text = draft.value.trim()
  if (!text) return
  emit('add', text)
  draft.value = ''
}

function startEditGoal() {
  goalDraft.value = props.dailyGoal
  editingGoal.value = true
  nextTick(() => goalInputRef.value && goalInputRef.value.focus())
}
function commitGoal() {
  if (!editingGoal.value) return
  const n = Math.max(1, Math.min(20, Number(goalDraft.value) || 1))
  emit('change-goal', n)
  editingGoal.value = false
}
function cancelEditGoal() {
  editingGoal.value = false
}
</script>

<style scoped>
.pomo-task-list { padding: 1.15rem 1.25rem; margin-bottom: 1rem; }
.panel-head { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
.panel-head h2 { margin: 0; font-size: 1rem; }
.panel-sub { margin: 0; font-family: var(--mono); font-size: 0.7rem; color: var(--text-muted); letter-spacing: 0.05em; }

.task-summary { display: flex; align-items: center; gap: 1.1rem; margin-bottom: 1rem; }
.goal-ring { position: relative; width: 72px; height: 72px; flex-shrink: 0; }
.goal-ring__svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.goal-ring__bg { fill: none; stroke: rgba(232, 93, 4, 0.12); stroke-width: 5; }
.goal-ring__fg {
  fill: none;
  stroke: var(--orange, #e85d04);
  stroke-width: 5;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s ease;
}
.goal-ring--done .goal-ring__fg { stroke: #2a9d8f; }
.goal-ring__center {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono);
  font-size: 0.95rem; color: var(--text);
}
.goal-ring__sep { opacity: 0.4; margin: 0 1px; }
.goal-ring__goal { font-size: 0.7rem; opacity: 0.7; }

.goal-meta { flex: 1; min-width: 0; }
.goal-meta__line { margin: 0 0 0.35rem; font-size: 0.85rem; display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.goal-num { color: var(--orange, #e85d04); font-weight: 600; font-family: var(--mono); }
.goal-edit {
  border: 1px solid var(--border); background: transparent; color: var(--text-muted);
  font: inherit; font-size: 0.7rem; padding: 0 0.4rem; border-radius: 3px; cursor: pointer; line-height: 1.4;
}
.goal-edit:hover { color: var(--orange); border-color: var(--orange); }
.goal-input {
  width: 3.5rem; border: 1px solid var(--orange); background: var(--bg); color: var(--text);
  font: inherit; font-family: var(--mono); font-size: 0.85rem; padding: 0.1rem 0.3rem; border-radius: 3px;
}
.goal-suffix { font-size: 0.8rem; color: var(--text-muted); }
.goal-meta__hint { margin: 0; font-size: 0.7rem; color: var(--text-muted); font-family: var(--mono); }
.goal-meta__line--done { color: #2a9d8f; font-weight: 600; }

.task-items { list-style: none; margin: 0 0 0.75rem; padding: 0; display: grid; gap: 0.4rem; }
.task-item {
  display: flex; align-items: center; gap: 0.55rem;
  padding: 0.45rem 0.6rem; border: 1px solid var(--border); border-radius: 4px;
  background: var(--bg);
  transition: border-color 0.15s;
}
.task-item--selected { border-color: var(--orange, #e85d04); background: rgba(232, 93, 4, 0.04); }
.task-item--done .task-text__title { text-decoration: line-through; opacity: 0.5; }

.task-check {
  width: 20px; height: 20px; flex-shrink: 0;
  border: 1.5px solid var(--text-muted); border-radius: 3px;
  background: transparent; color: var(--orange, #e85d04);
  font: inherit; font-size: 0.7rem; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; padding: 0;
}
.task-item--done .task-check { border-color: var(--orange); background: var(--orange); color: #fff; }
.task-item--done .task-check span { color: #fff; }
.task-check:hover { border-color: var(--orange); }

.task-text {
  flex: 1; min-width: 0;
  border: none; background: transparent; padding: 0;
  text-align: left; font: inherit; color: var(--text); cursor: pointer;
  display: flex; flex-direction: column; gap: 0.15rem;
}
.task-text__title { font-size: 0.85rem; line-height: 1.3; word-break: break-word; }
.task-text__meta { display: flex; align-items: center; gap: 0.5rem; font-size: 0.65rem; color: var(--text-muted); font-family: var(--mono); }
.task-text__count { opacity: 0.8; }
.task-text__bind { color: var(--orange, #e85d04); font-size: 0.9rem; line-height: 1; }

.task-remove {
  border: none; background: transparent; color: var(--text-muted);
  font: inherit; font-size: 1rem; line-height: 1; padding: 0 0.3rem; cursor: pointer;
}
.task-remove:hover { color: #c0392b; }

.task-empty { margin: 0 0 0.75rem; font-size: 0.78rem; color: var(--text-muted); }

.task-add { display: flex; gap: 0.5rem; }
.task-add input {
  flex: 1; border: 1px solid var(--border); background: var(--bg); color: var(--text);
  font: inherit; font-size: 0.85rem; padding: 0.4rem 0.6rem; border-radius: 3px;
}
.task-add input:focus { outline: none; border-color: var(--orange, #e85d04); }
</style>

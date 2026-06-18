<template>
  <div class="tag-bar" :class="{ 'tag-bar--expanded': isExpanded, 'tag-bar--filtered': !!modelValue }">
    <div class="tag-bar-head">
      <label>标签</label>
      <div class="tag-bar-actions">
        <button
          v-if="modelValue"
          type="button"
          class="tag-action tag-action--clear"
          @click="emit('update:modelValue', '')"
        >
          清除 · #{{ modelValue }}
        </button>
        <button
          type="button"
          class="tag-action"
          :aria-expanded="isExpanded"
          @click="isExpanded = !isExpanded"
        >
          {{ isExpanded ? '收起' : `全部 ${tagStats.length}` }}
          <span class="tag-action-icon">{{ isExpanded ? '▲' : '▼' }}</span>
        </button>
      </div>
    </div>

    <div class="tag-strip-wrap">
      <div class="tag-strip" role="list">
        <button
          v-for="item in stripTags"
          :key="item.tag"
          type="button"
          role="listitem"
          :class="['tag-chip', { 'tag-chip--active': modelValue === item.tag }]"
          @click="toggleTag(item.tag)"
        >
          <span class="tag-chip-name">{{ item.tag }}</span>
          <span class="tag-chip-count">{{ item.count }}</span>
        </button>
      </div>
    </div>

    <Transition name="tag-panel">
      <div v-if="isExpanded" class="tag-panel">
        <input
          v-model="query"
          type="search"
          class="tag-search"
          placeholder="搜索标签…"
          autocomplete="off"
        >
        <div v-if="filteredStats.length" class="tag-panel-grid">
          <button
            v-for="item in filteredStats"
            :key="item.tag"
            type="button"
            :class="['tag-chip', 'tag-chip--panel', { 'tag-chip--active': modelValue === item.tag }]"
            @click="toggleTag(item.tag)"
          >
            <span class="tag-chip-name">#{{ item.tag }}</span>
            <span class="tag-chip-count">{{ item.count }}</span>
          </button>
        </div>
        <p v-else class="tag-panel-empty">没有匹配「{{ query }}」的标签</p>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { getTagStats } from '../data/posts'

const STRIP_LIMIT = 8

const props = defineProps({
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const isExpanded = ref(false)
const query = ref('')
const tagStats = getTagStats()

const stripTags = computed(() => {
  const hot = tagStats.slice(0, STRIP_LIMIT)
  if (!props.modelValue) return hot
  if (hot.some(item => item.tag === props.modelValue)) return hot
  const selected = tagStats.find(item => item.tag === props.modelValue)
  return selected ? [selected, ...hot.slice(0, STRIP_LIMIT - 1)] : hot
})

const filteredStats = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return tagStats
  return tagStats.filter(item => item.tag.toLowerCase().includes(q))
})

function toggleTag(tag) {
  emit('update:modelValue', props.modelValue === tag ? '' : tag)
}

watch(isExpanded, (open) => {
  if (!open) query.value = ''
})
</script>

<style scoped>
.tag-bar {
  margin-bottom: 1rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px dashed var(--border);
}

.tag-bar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.tag-bar-head label {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  flex-shrink: 0;
}

.tag-bar-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.tag-action {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.04em;
  color: var(--steel);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.1rem 0;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.tag-action:hover {
  color: var(--orange);
}

.tag-action--clear {
  color: var(--orange);
  max-width: 12rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-action-icon {
  font-size: 0.5rem;
  opacity: 0.75;
}

.tag-strip-wrap {
  position: relative;
  margin: 0 -0.15rem;
  padding: 0 0.15rem;
}

.tag-strip-wrap::before,
.tag-strip-wrap::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1.25rem;
  pointer-events: none;
  z-index: 1;
}

.tag-strip-wrap::before {
  left: 0;
  background: linear-gradient(to right, var(--bg), transparent);
}

.tag-strip-wrap::after {
  right: 0;
  background: linear-gradient(to left, var(--bg), transparent);
}

.tag-strip {
  display: flex;
  gap: 0.4rem;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.1rem 0 0.35rem;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.tag-strip::-webkit-scrollbar {
  display: none;
}

.tag-chip {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  line-height: 1;
  padding: 0.38rem 0.55rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text-muted);
  cursor: pointer;
  transition:
    border-color 0.15s,
    color 0.15s,
    background 0.15s,
    transform 0.12s;
}

.tag-chip:hover {
  border-color: var(--steel);
  color: var(--text);
}

.tag-chip--active {
  border-color: var(--orange);
  color: var(--orange);
  background: var(--orange-light);
  box-shadow: inset 0 -2px 0 var(--orange);
}

.tag-chip-name {
  max-width: 7.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-chip-count {
  font-size: 0.52rem;
  color: var(--text-muted);
  opacity: 0.85;
  min-width: 0.85rem;
  text-align: center;
}

.tag-chip--active .tag-chip-count {
  color: var(--orange);
  opacity: 0.75;
}

.tag-panel {
  margin-top: 0.65rem;
  padding: 0.75rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
}

.tag-search {
  width: 100%;
  box-sizing: border-box;
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.45rem 0.65rem;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  margin-bottom: 0.65rem;
}

.tag-search:focus {
  outline: none;
  border-color: var(--orange);
}

.tag-panel-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  max-height: 9.5rem;
  overflow-y: auto;
  padding-right: 0.15rem;
}

.tag-chip--panel {
  flex-shrink: 1;
}

.tag-panel-empty {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  text-align: center;
  padding: 0.75rem 0;
}

.tag-panel-enter-active,
.tag-panel-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.tag-panel-enter-from,
.tag-panel-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 640px) {
  .tag-chip {
    min-height: 32px;
    padding: 0.45rem 0.6rem;
  }

  .tag-action {
    min-height: 28px;
  }

  .tag-strip-wrap::before,
  .tag-strip-wrap::after {
    width: 0.75rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tag-panel-enter-active,
  .tag-panel-leave-active {
    transition: none;
  }

  .tag-panel-enter-from,
  .tag-panel-leave-to {
    transform: none;
  }
}
</style>

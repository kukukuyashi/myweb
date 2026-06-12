<template>
  <div class="tag-bar" :class="{ expanded: isExpanded }">
    <div class="tag-bar-head">
      <label>标签</label>
      <button type="button" class="tag-toggle" @click="isExpanded = !isExpanded">
        {{ isExpanded ? '收起' : `展开全部 (${tags.length})` }}
        <span class="tag-toggle-icon">{{ isExpanded ? '▲' : '▼' }}</span>
      </button>
    </div>
    <div class="tag-bar-inner">
      <button
        v-for="tag in tags"
        :key="tag"
        type="button"
        :class="['filter-btn', 'tag-btn', { active: modelValue === tag }]"
        @click="$emit('update:modelValue', modelValue === tag ? '' : tag)"
      >#{{ tag }}</button>
      <button
        v-if="modelValue"
        type="button"
        class="filter-btn tag-clear"
        @click="$emit('update:modelValue', '')"
      >清除</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  tags: { type: Array, default: () => [] },
  modelValue: { type: String, default: '' },
})

defineEmits(['update:modelValue'])

const isExpanded = ref(false)
</script>

<style scoped>
.tag-bar {
  margin-bottom: 0.75rem;
}

.tag-bar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.tag-bar-head label {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.tag-toggle {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--steel);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.15rem 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.tag-toggle:hover { color: var(--orange); }

.tag-toggle-icon {
  font-size: 0.55rem;
  opacity: 0.7;
}

.tag-bar-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  max-height: 2rem;
  overflow: hidden;
  transition: max-height 0.25s ease;
}

.tag-bar.expanded .tag-bar-inner {
  max-height: 520px;
}

.tag-btn { font-size: 0.65rem !important; }

.tag-clear {
  font-size: 0.65rem !important;
  color: var(--text-muted) !important;
}
</style>

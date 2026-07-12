<template>
  <span v-if="level >= 2" class="level-badge" :class="`level-badge--${level}`">
    Lv.{{ level }} {{ title }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const LEVEL_TITLES = {
  1: '见习',
  2: '旅人',
  3: '同好',
  4: '达人',
  5: '传说',
}

const props = defineProps({
  level: { type: Number, default: 1 },
  levelTitle: { type: String, default: '' },
})

const title = computed(() => props.levelTitle || LEVEL_TITLES[props.level] || '见习')
</script>

<style scoped>
.level-badge {
  display: inline-flex;
  align-items: center;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.03em;
  padding: 0.12rem 0.4rem;
  border-radius: 2px;
  border: 1px solid var(--border);
  color: var(--steel);
  background: var(--bg);
}

.level-badge--2 {
  color: var(--orange);
  border-color: rgba(232, 93, 4, 0.35);
}

.level-badge--3,
.level-badge--4,
.level-badge--5 {
  color: #fff;
  background: var(--orange);
  border-color: var(--orange);
}

.level-badge--5 {
  box-shadow: 0 0 8px rgba(232, 93, 4, 0.45);
}
</style>

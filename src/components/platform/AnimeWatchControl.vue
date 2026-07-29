<template>
  <div class="watch-control" :class="{ compact }">
    <button
      type="button"
      class="wc-btn"
      :class="{ active: status === 'plan' }"
      :disabled="disabled"
      @click="onClick('plan')"
    >想看</button>
    <button
      type="button"
      class="wc-btn"
      :class="{ active: status === 'watching' }"
      :disabled="disabled"
      @click="onClick('watching')"
    >正在追</button>
  </div>
</template>

<script setup>
const props = defineProps({
  /** null | 'plan' | 'watching' */
  status: { type: String, default: null },
  disabled: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
})
const emit = defineEmits(['set', 'clear'])

function onClick(next) {
  // 再点当前状态 = 取消追番
  if (props.status === next) {
    emit('clear')
  } else {
    emit('set', next)
  }
}
</script>

<style scoped>
.watch-control {
  display: inline-flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.wc-btn {
  font-family: var(--mono);
  font-size: 0.68rem;
  padding: 0.28rem 0.55rem;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.wc-btn:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--orange) 55%, var(--border));
  color: var(--orange);
}

.wc-btn.active {
  border-color: var(--orange);
  background: color-mix(in srgb, var(--orange) 14%, var(--bg));
  color: var(--orange);
  font-weight: 600;
}

.wc-btn:disabled {
  opacity: 0.55;
  cursor: default;
}

.compact .wc-btn {
  padding: 0.2rem 0.45rem;
  font-size: 0.64rem;
}
</style>
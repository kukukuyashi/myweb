<template>
  <div class="avatar-frame" :class="frameClass">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  level: { type: Number, default: 1 },
})

const frameClass = computed(() => {
  if (props.level >= 5) return 'avatar-frame--legend'
  if (props.level >= 3) return 'avatar-frame--acg'
  return ''
})
</script>

<style scoped>
.avatar-frame {
  display: inline-flex;
  border-radius: 50%;
}

.avatar-frame--acg :deep(img),
.avatar-frame--acg :deep(.avatar),
.avatar-frame--acg :deep(.avatar-lg),
.avatar-frame--acg :deep(.avatar-wrap) {
  box-shadow: 0 0 0 2px var(--orange), 0 0 12px rgba(232, 93, 4, 0.35);
}

.avatar-frame--legend {
  position: relative;
}

.avatar-frame--legend::after {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: linear-gradient(135deg, var(--orange), #ffb347, var(--orange)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: halo-spin 4s linear infinite;
  pointer-events: none;
}

@keyframes halo-spin {
  to { transform: rotate(360deg); }
}
</style>

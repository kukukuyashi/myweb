<template>
  <h1
    class="article-title typewriter-title"
    :class="{ 'typewriter-title--active': isTyping }"
    :aria-label="text"
  >
    <span class="typewriter-text">{{ displayedText }}</span><span
      v-if="isTyping"
      class="typewriter-cursor"
      aria-hidden="true"
    >▍</span>
  </h1>
</template>

<script setup>
import { watch, toRef } from 'vue'
import { useTypewriter } from '../composables/useTypewriter'

const props = defineProps({
  text: { type: String, default: '' },
  /** 为 true 时开始打字（通常等文章加载完） */
  active: { type: Boolean, default: true },
})

const { displayedText, isTyping, start, reset } = useTypewriter()

watch(
  [toRef(props, 'text'), toRef(props, 'active')],
  ([text, active]) => {
    if (!active || !text) {
      reset()
      if (text && !active) displayedText.value = ''
      return
    }
    start(text)
  },
  { immediate: true }
)
</script>

<style scoped>
.typewriter-title {
  min-height: 1.2em;
}

.typewriter-text {
  white-space: pre-wrap;
}

.typewriter-cursor {
  display: inline-block;
  font-family: var(--mono);
  font-weight: 400;
  color: var(--orange);
  margin-left: 1px;
  animation: typewriter-blink 0.85s step-end infinite;
}

@keyframes typewriter-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .typewriter-cursor {
    display: none;
    animation: none;
  }
}
</style>

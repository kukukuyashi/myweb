import { ref, onUnmounted } from 'vue'

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * 打字机效果 — 每次 start() 播一次，换文章前调 reset()
 */
export function useTypewriter(options = {}) {
  const displayedText = ref('')
  const isTyping = ref(false)
  const isDone = ref(false)

  let timer = null
  const minInterval = options.minInterval ?? 28
  const maxInterval = options.maxInterval ?? 55
  const maxDuration = options.maxDuration ?? 2800

  function clearTimer() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function reset() {
    clearTimer()
    displayedText.value = ''
    isTyping.value = false
    isDone.value = false
  }

  function start(text) {
    clearTimer()
    const full = String(text ?? '')

    if (!full || prefersReducedMotion()) {
      displayedText.value = full
      isTyping.value = false
      isDone.value = true
      return
    }

    displayedText.value = ''
    isTyping.value = true
    isDone.value = false

    const interval = Math.max(
      minInterval,
      Math.min(maxInterval, Math.floor(maxDuration / full.length))
    )

    let i = 0
    timer = setInterval(() => {
      i += 1
      displayedText.value = full.slice(0, i)
      if (i >= full.length) {
        clearTimer()
        isTyping.value = false
        isDone.value = true
      }
    }, interval)
  }

  onUnmounted(clearTimer)

  return { displayedText, isTyping, isDone, start, reset }
}

import { onBeforeUnmount, onMounted, ref } from 'vue'

/** 元素进入视口后再执行回调（用于延迟加载评论、背景图等） */
export function useLazyVisible(targetRef, onVisible, options = {}) {
  const visible = ref(false)
  let observer = null

  onMounted(() => {
    const el = targetRef.value
    if (!el) return

    if (!('IntersectionObserver' in window)) {
      visible.value = true
      onVisible?.()
      return
    }

    observer = new IntersectionObserver(
      (entries) => {
        if (!entries[0]?.isIntersecting) return
        visible.value = true
        onVisible?.()
        observer?.disconnect()
        observer = null
      },
      { rootMargin: '180px', threshold: 0.01, ...options },
    )
    observer.observe(el)
  })

  onBeforeUnmount(() => {
    observer?.disconnect()
  })

  return { visible }
}

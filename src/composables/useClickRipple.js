import { onMounted, onUnmounted } from 'vue'

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * 点击涟漪效果 — 在鼠标点击位置生成扩散波纹
 */
export function useClickRipple() {
  function createRipple(e) {
    if (prefersReducedMotion()) return

    const ripple = document.createElement('div')
    ripple.className = 'click-ripple'
    ripple.style.left = `${e.clientX}px`
    ripple.style.top = `${e.clientY}px`
    document.body.appendChild(ripple)

    ripple.addEventListener('animationend', () => {
      ripple.remove()
    })
  }

  onMounted(() => {
    document.addEventListener('click', createRipple)
  })

  onUnmounted(() => {
    document.removeEventListener('click', createRipple)
  })
}

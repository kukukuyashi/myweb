import { onMounted, onUnmounted } from 'vue'

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

let sharedObserver = null

function getObserver() {
  if (sharedObserver) return sharedObserver
  if (prefersReducedMotion()) return null

  sharedObserver = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed')
          sharedObserver?.unobserve(entry.target)
        }
      })
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }
  )
  return sharedObserver
}

/** 扫描 root 内未揭示的 [data-reveal] 元素 */
export function observeReveal(root, selector = '[data-reveal]') {
  if (!root) return
  const nodes = root.querySelectorAll(selector)

  if (prefersReducedMotion()) {
    nodes.forEach(el => el.classList.add('is-revealed'))
    return
  }

  const observer = getObserver()
  if (!observer) return

  nodes.forEach(el => {
    if (!el.classList.contains('is-revealed')) observer.observe(el)
  })
}

/** 进入视口时给元素加 .is-revealed，配合 main.css 的 .reveal-item */
export function useRevealOnScroll(rootRef, selector = '[data-reveal]') {
  onMounted(() => observeReveal(rootRef?.value, selector))
  onUnmounted(() => {
    /* observer 全局复用，页面切换时元素已 DOM 移除 */
  })
}

/** 鼠标位置驱动背景光晕（App 级） */
export function useGridSpotlight() {
  let raf = 0
  let x = 0
  let y = 0

  function onMove(e) {
    x = e.clientX
    y = e.clientY
    if (raf) return
    raf = requestAnimationFrame(() => {
      document.documentElement.style.setProperty('--spot-x', `${x}px`)
      document.documentElement.style.setProperty('--spot-y', `${y}px`)
      raf = 0
    })
  }

  onMounted(() => {
    if (prefersReducedMotion()) return
    document.documentElement.style.setProperty('--spot-x', '50vw')
    document.documentElement.style.setProperty('--spot-y', '40vh')
    window.addEventListener('mousemove', onMove, { passive: true })
  })

  onUnmounted(() => {
    window.removeEventListener('mousemove', onMove)
    if (raf) cancelAnimationFrame(raf)
  })
}

import { onMounted, onUnmounted, ref } from 'vue'

const KONAMI = [
  'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
  'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
  'KeyB', 'KeyA',
]

const CHEAT_MS = 10000

/** Konami 秘技 → 全站 8-bit 滤镜约 10 秒 */
export function useKonamiCheat() {
  const active = ref(false)
  let step = 0
  let timer = null

  function deactivate() {
    active.value = false
    document.documentElement.classList.remove('cheat-mode')
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  function activate() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    deactivate()
    active.value = true
    document.documentElement.classList.add('cheat-mode')
    timer = setTimeout(deactivate, CHEAT_MS)
  }

  function onKeydown(e) {
    if (e.code === KONAMI[step]) {
      step += 1
      if (step >= KONAMI.length) {
        step = 0
        activate()
      }
      return
    }
    step = e.code === KONAMI[0] ? 1 : 0
  }

  onMounted(() => window.addEventListener('keydown', onKeydown))
  onUnmounted(() => {
    window.removeEventListener('keydown', onKeydown)
    deactivate()
  })

  return { cheatActive: active }
}

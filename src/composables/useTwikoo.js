import { ref, onUnmounted } from 'vue'

const TWIKOO_CDN = 'https://cdn.jsdelivr.net/npm/twikoo@1.6.32/dist/twikoo.all.min.js'
let scriptLoading = null

function loadTwikooScript() {
  if (window.twikoo) return Promise.resolve()
  if (scriptLoading) return scriptLoading
  scriptLoading = new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${TWIKOO_CDN}"]`)
    if (existing) {
      existing.addEventListener('load', () => resolve())
      existing.addEventListener('error', reject)
      return
    }
    const script = document.createElement('script')
    script.src = TWIKOO_CDN
    script.async = true
    script.onload = () => resolve()
    script.onerror = reject
    document.body.appendChild(script)
  })
  return scriptLoading
}

export function useTwikoo(containerId, getOptions) {
  const status = ref('loading')
  let timer = null

  async function init() {
    const envId = import.meta.env.VITE_TWIKOO_ENV_ID
    if (!envId || envId === 'your-env-id') {
      status.value = 'error'
      return
    }

    const el = document.getElementById(containerId)
    if (el) el.innerHTML = ''

    status.value = 'loading'
    try {
      await loadTwikooScript()
      const opts = typeof getOptions === 'function' ? getOptions() : getOptions
      window.twikoo.init({
        envId,
        el: `#${containerId}`,
        lang: 'zh-CN',
        ...opts,
      })
      timer = setTimeout(() => {
        const box = document.getElementById(containerId)
        status.value = box?.children.length ? 'ok' : 'error'
      }, 15000)
    } catch {
      status.value = 'error'
    }
  }

  onUnmounted(() => {
    if (timer) clearTimeout(timer)
  })

  return { status, init }
}

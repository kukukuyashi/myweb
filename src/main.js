import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { initTheme } from './utils/theme.js'
import './styles/main.css'

initTheme()

const app = createApp(App)
app.use(createPinia())
app.use(router)

function hideLoadingScreen() {
  const loadingScreen = document.getElementById('loading-screen')
  if (!loadingScreen || loadingScreen.dataset.hidden === '1') return
  loadingScreen.dataset.hidden = '1'
  loadingScreen.classList.add('fade-out')
  loadingScreen.style.pointerEvents = 'none'
  setTimeout(() => {
    loadingScreen.style.display = 'none'
  }, 500)
}

// GitHub Pages SPA fallback: 404.html 会把原始路径存到 ?p= 参数
const params = new URLSearchParams(window.location.search)
const redirectPath = params.get('p')
if (redirectPath) {
  // 移除 ?p= 参数后替换 URL 并导航
  params.delete('p')
  const qs = params.toString()
  const newUrl = redirectPath + (qs ? '?' + qs : '') + window.location.hash
  window.history.replaceState(null, '', newUrl)
  router.replace(redirectPath)
}

app.mount('#app')
hideLoadingScreen()

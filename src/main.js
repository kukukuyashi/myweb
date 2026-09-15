import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { initTheme } from './utils/theme.js'
import { ensurePostsCatalogLoaded } from './data/posts.js'
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

// 博客目录（posts.json）只在博客相关路由需要就绪后再挂载；
// /app、/admin 等平台页不消费该目录，直接挂载以加快首屏
const base = import.meta.env.BASE_URL
const initialPath = (redirectPath || window.location.pathname).replace(base, '/')
const needsPostsCatalog =
  !initialPath.startsWith('/app') &&
  !initialPath.startsWith('/admin')

const mount = () => {
  app.mount('#app')
  hideLoadingScreen()
}

if (needsPostsCatalog) {
  ensurePostsCatalogLoaded().finally(mount)
} else {
  ensurePostsCatalogLoaded()
  mount()
}

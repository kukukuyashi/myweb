import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

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

<template>
  <div class="guestbook">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <h1 class="page-title">留言板</h1>
          <p>欢迎留下想法、建议或打个招呼。我会尽快回复每一条留言。</p>
          <blockquote>"交流是进步的桥梁，留言是友谊的开始。"</blockquote>
          <p v-if="status === 'loading'" class="guestbook-hint">评论加载中…若首次较慢，可能是后端正在唤醒（约 1～2 分钟）。</p>
          <p v-if="status === 'error'" class="guestbook-hint error">评论服务暂不可用，请稍后再试或刷新页面。</p>
          <div id="tcomment"></div>
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import NavBar from '../components/NavBar.vue'
import MusicPlayer from '../components/MusicPlayer.vue'

const status = ref('loading')

onMounted(() => {
  const envId = import.meta.env.VITE_TWIKOO_ENV_ID
  if (!envId || envId === 'your-env-id') {
    status.value = 'error'
    console.warn('Twikoo 未配置：在 .env.local 中设置 VITE_TWIKOO_ENV_ID')
    return
  }

  const script = document.createElement('script')
  script.src = 'https://cdn.jsdelivr.net/npm/twikoo@1.6.32/dist/twikoo.all.min.js'
  script.async = true
  script.onerror = () => { status.value = 'error' }
  script.onload = () => {
    window.twikoo.init({
      envId,
      el: '#tcomment',
      lang: 'zh-CN',
    })
    // 评论框渲染成功后隐藏提示
    setTimeout(() => {
      const el = document.getElementById('tcomment')
      if (el?.children.length) status.value = 'ok'
      else status.value = 'error'
    }, 15000)
  }
  document.body.appendChild(script)
})
</script>

<style scoped>
.guestbook-hint {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}
.guestbook-hint.error { color: #c0392b; }
</style>

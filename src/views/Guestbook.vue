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
    <SiteFooter />
    <MusicPlayer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { useTwikoo } from '../composables/useTwikoo'
import { usePageMeta } from '../composables/usePageMeta'

usePageMeta({ title: '留言板', description: '欢迎留下想法、建议或打个招呼。' })

const { status, init } = useTwikoo('tcomment')

onMounted(() => init())
</script>

<style scoped>
.guestbook-hint {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}
.guestbook-hint.error { color: #c0392b; }

.guestbook :deep(.tk-extras) {
  display: none;
}
</style>

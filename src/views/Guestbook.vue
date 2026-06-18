<template>
  <div class="guestbook">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <InkRevealPanel
            tag="header"
            root-class="page-ink-header"
            image="img/qqgg/guigui.jpg"
            position="58% center"
            :r-end="125"
            fade-direction="left"
          >
            <p class="page-ink-coord">GUESTBOOK · TWIKOO · <span class="ink-hint">hover 晕染</span></p>
            <h1 class="page-title">留言板</h1>
            <p>欢迎留下想法、建议或打个招呼。我会尽快回复每一条留言。</p>
            <blockquote>"交流是进步的桥梁，留言是友谊的开始。"</blockquote>
          </InkRevealPanel>

          <p v-if="status === 'loading'" class="guestbook-hint">评论加载中…若首次较慢，可能是后端正在唤醒（约 1～2 分钟）。</p>
          <p v-if="status === 'error'" class="guestbook-hint error">评论服务暂不可用，请稍后再试或刷新页面。</p>
          <div id="tcomment" ref="commentBoxRef"></div>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { useTwikoo } from '../composables/useTwikoo'
import { usePageMeta } from '../composables/usePageMeta'
import InkRevealPanel from '../components/InkRevealPanel.vue'
import { useLazyVisible } from '../composables/useLazyVisible'

usePageMeta({ title: '留言板', description: '欢迎留下想法、建议或打个招呼。' })

const { status, init } = useTwikoo('tcomment')
const commentBoxRef = ref(null)

useLazyVisible(commentBoxRef, init)
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

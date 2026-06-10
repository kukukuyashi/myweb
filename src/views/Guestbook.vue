<template>
  <div class="guestbook">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <h1 class="page-title">留言板</h1>
          <p>欢迎留下想法、建议或打个招呼。我会尽快回复每一条留言。</p>
          <blockquote>"交流是进步的桥梁，留言是友谊的开始。"</blockquote>
          <blockquote>"还没做好，不好意思喵"</blockquote>
          <div id="tcomment"></div>
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'
import MusicPlayer from '../components/MusicPlayer.vue'

onMounted(() => {
  const script = document.createElement('script')
  script.src = 'https://cdn.jsdelivr.net/npm/twikoo@1.6.32/dist/twikoo.all.min.js'
  script.async = true
  script.onload = () => {
    window.twikoo.init({
      envId: 'your-env-id',
      el: '#tcomment',
      lang: 'zh-CN',
    })
  }
  document.body.appendChild(script)
})
</script>

<template>
  <div class="not-found">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <h1 class="page-title">404</h1>
          <p>页面不存在或已被移除。</p>
          <router-link to="/" class="back-link">← 返回首页</router-link>
        </div>
      </div>
    </main>
    <SiteFooter />
    <MusicPlayer />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { usePageMeta } from '../composables/usePageMeta'

usePageMeta({ title: '404', description: '页面不存在或已被移除。' })
</script>

<style scoped>
.back-link {
  display: inline-block;
  margin-top: 1rem;
  color: var(--orange);
  font-family: var(--mono);
  font-size: 0.85rem;
}
.back-link:hover { text-decoration: underline; }
</style>

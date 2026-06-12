<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="footer-logo">CYINC.LOG</span>
        <p class="footer-desc">写给自己的技术学习日志</p>
      </div>
      <div class="footer-links">
        <router-link to="/archive">归档</router-link>
        <router-link to="/guestbook">留言板</router-link>
        <router-link to="/music">音乐室</router-link>
        <a :href="rssUrl" target="_blank" rel="noopener">RSS</a>
        <a href="https://github.com/kukukuyashi/myweb" target="_blank" rel="noopener">GitHub</a>
      </div>
      <div class="footer-meta">
        <span>© {{ year }} Cyinc</span>
        <span class="footer-dot">·</span>
        <span>{{ totalPosts }} articles</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { posts } from '../data/posts'

const year = new Date().getFullYear()
const totalPosts = posts.length
const rssUrl = `${import.meta.env.BASE_URL}feed.xml`
</script>

<style scoped>
.site-footer {
  border-top: 1px solid var(--border);
  background: var(--bg-paper);
  margin-top: 3rem;
  padding: 2rem 1.5rem 5rem;
}

.footer-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: flex-start;
  justify-content: space-between;
  font-family: var(--mono);
  font-size: 0.72rem;
}

.footer-logo {
  font-weight: 500;
  letter-spacing: 0.05em;
  color: var(--text);
}

.footer-desc {
  margin-top: 0.35rem;
  color: var(--text-muted);
  font-family: var(--sans);
  font-size: 0.85rem;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.25rem;
}

.footer-links a {
  color: var(--steel);
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.footer-links a:hover {
  color: var(--orange);
}

.footer-meta {
  color: var(--text-muted);
  width: 100%;
  padding-top: 1rem;
  border-top: 1px dashed var(--border);
}

.footer-dot {
  margin: 0 0.35rem;
}

@media (max-width: 768px) {
  .site-footer { padding-bottom: 6rem; }
}
</style>

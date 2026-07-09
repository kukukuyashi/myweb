<template>
  <div class="forum-page">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="forum-shell card">
          <p class="forum-coord">FORUM · PHASE C</p>
          <h1 class="page-title">社区论坛</h1>
          <p class="forum-desc">
            板块、主题帖、回复与 moderation — 计划在 Phase C 实现。
            当前 M5 先保留入口，便于 Hub 信息架构完整。
          </p>
          <ul class="forum-plan">
            <li>板块分类（技术 / 生活 / 项目）</li>
            <li>发帖、回帖、点赞</li>
            <li>与 FastAPI 用户体系打通</li>
          </ul>
          <router-link to="/hub" class="btn-primary">返回平台入口</router-link>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { usePageMeta } from '../composables/usePageMeta'

usePageMeta({
  title: '论坛 · 即将推出',
  description: 'CYINC 社区论坛 Phase C 规划中。',
})
</script>

<style scoped>
.forum-shell {
  max-width: 560px;
  margin-top: 1rem;
  padding: 1.5rem;
  border: 1px solid var(--border);
  background: var(--card-bg, #fff);
}

.forum-coord {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  letter-spacing: 0.12em;
  margin-bottom: 0.5rem;
}

.forum-desc {
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0.75rem 0 1rem;
}

.forum-plan {
  margin: 0 0 1.25rem 1.1rem;
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.7;
}

.btn-primary {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.55rem 1rem;
  background: var(--orange);
  border: 1px solid var(--orange);
  color: #fff;
  text-decoration: none;
}
</style>

<template>
  <div ref="hubRef" class="hub-page">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <header class="hub-header reveal-item" data-reveal>
          <p class="hub-coord">PLATFORM · CYINC v2</p>
          <h1 class="page-title">平台入口</h1>
          <p class="hub-desc">博客、AI、番茄钟与个人中心 — FastAPI + Dify + n8n 全栈平台。</p>
        </header>

        <div class="hub-grid">
          <router-link
            v-for="item in entries"
            :key="item.to"
            :to="item.to"
            class="hub-card reveal-item"
            data-reveal
            :class="{ disabled: item.soon }"
          >
            <span class="hub-card-tag">{{ item.tag }}</span>
            <h2>{{ item.title }}</h2>
            <p>{{ item.desc }}</p>
            <span v-if="item.soon" class="hub-soon">即将推出</span>
            <span v-else class="hub-arrow">进入 →</span>
          </router-link>
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
import { usePageMeta } from '../composables/usePageMeta'
import { useRevealOnScroll } from '../composables/useRevealOnScroll'

const hubRef = ref(null)
useRevealOnScroll(hubRef)

usePageMeta({
  title: '平台入口',
  description: 'CYINC 全栈平台 Hub：博客、AI 助手、番茄钟、个人中心。',
})

const entries = [
  {
    to: '/',
    tag: 'BLOG',
    title: '技术博客',
    desc: 'Vue 3 静态博客、归档、项目与音乐室。',
  },
  {
    to: '/ai',
    tag: 'AI · DIFY',
    title: '站内 AI 助手',
    desc: '基于 Dify Chatflow，可询问博客与技术栈。',
  },
  {
    to: '/pomo',
    tag: 'POMODORO',
    title: '番茄钟',
    desc: '25 分钟专注 + 5 分钟休息，记录专注时长。',
  },
  {
    to: '/me',
    tag: 'ACCOUNT',
    title: '个人中心',
    desc: '登录、资料、我的文章与平台账号管理。',
  },
  {
    to: '/forum',
    tag: 'FORUM',
    title: '社区论坛',
    desc: '板块讨论、发帖回帖 — Phase C 规划中。',
    soon: true,
  },
]
</script>

<style scoped>
.hub-header { margin-bottom: 2rem; }

.hub-coord {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  letter-spacing: 0.12em;
  margin-bottom: 0.5rem;
}

.hub-desc {
  color: var(--text-muted);
  margin-top: 0.5rem;
  max-width: 36rem;
}

.hub-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.hub-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.25rem;
  border: 1px solid var(--border);
  background: var(--card-bg, #fff);
  text-decoration: none;
  color: inherit;
  min-height: 160px;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
}

.hub-card:hover {
  border-color: var(--orange);
  box-shadow: 0 4px 0 var(--orange);
  transform: translateY(-2px);
}

.hub-card.disabled {
  opacity: 0.85;
}

.hub-card-tag {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
  letter-spacing: 0.1em;
}

.hub-card h2 {
  font-size: 1.1rem;
  margin: 0;
}

.hub-card p {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.5;
  flex: 1;
  margin: 0;
}

.hub-arrow,
.hub-soon {
  font-family: var(--mono);
  font-size: 0.72rem;
  margin-top: auto;
}

.hub-soon {
  color: #b45309;
}

.hub-arrow {
  color: var(--orange);
}
</style>

<template>
  <div class="dashboard">
    <section class="platform-panel welcome">
      <h2>👋 欢迎回来</h2>
      <p>这里是你的管理中心，快速查看站点概况并进入各模块。</p>
    </section>

    <section class="stat-grid">
      <div v-for="card in statCards" :key="card.key" class="platform-panel stat-card">
        <div class="stat-head">
          <span class="stat-label">{{ card.label }}</span>
          <span class="stat-icon">{{ card.icon }}</span>
        </div>
        <strong class="stat-value">{{ loading ? '…' : (stats[card.key] ?? '--') }}</strong>
        <small class="stat-hint">{{ card.hint }}</small>
      </div>
    </section>

    <p v-if="error" class="toast" data-type="error">{{ error }}</p>

    <h3 class="section-title">快捷操作</h3>
    <section class="quick-grid">
      <router-link v-for="q in quickActions" :key="q.to" :to="q.to" class="platform-panel quick-card">
        <span class="quick-icon">{{ q.icon }}</span>
        <strong>{{ q.title }}</strong>
        <small>{{ q.desc }}</small>
        <span class="quick-cta">进入管理 →</span>
      </router-link>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { fetchAdminSummary } from '../../api/notesAdmin.js'

const loading = ref(true)
const error = ref('')
const stats = reactive({})

const statCards = [
  { key: 'posts', label: '博客文章', icon: '📝', hint: '已发布文章数量' },
  { key: 'threads', label: '论坛帖子', icon: '💬', hint: '论坛主题总数' },
  { key: 'replies', label: '论坛回复', icon: '↩', hint: '回复总数' },
  { key: 'users', label: '注册用户', icon: '👤', hint: '平台用户数' },
  { key: 'messages', label: '留言', icon: '✉', hint: '留言板消息' },
  { key: 'anime', label: '追番收藏', icon: '📺', hint: '追番条目数' },
  { key: 'botDrafts', label: '机器人草稿', icon: '✦', hint: '待审核投稿' },
]

const quickActions = [
  { to: '/admin/notes', icon: '✎', title: '笔记管理', desc: '新建、编辑、发布你的 Markdown 笔记' },
  { to: '/admin/acg-bot', icon: '✦', title: '发帖机器人', desc: '一键采集资讯，审核后发布到论坛' },
  { to: '/admin/data', icon: '▤', title: '数据管理', desc: '用户 / 文章 / 论坛 / 留言数据表' },
]

onMounted(async () => {
  try {
    const data = await fetchAdminSummary()
    Object.assign(stats, data || {})
  } catch (err) {
    error.value = err.message || '统计加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 1.25rem; }
.welcome h2 { margin: 0 0 0.35rem; font-size: 1.4rem; }
.welcome p { margin: 0; color: var(--text-muted); }

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 0.9rem;
}
.stat-card { display: flex; flex-direction: column; gap: 0.4rem; }
.stat-head { display: flex; align-items: center; justify-content: space-between; }
.stat-label { color: var(--text-muted); font-size: 0.88rem; }
.stat-icon { font-size: 1.1rem; opacity: 0.8; }
.stat-value { font-size: 1.9rem; line-height: 1.1; }
.stat-hint { color: var(--text-muted); font-size: 0.76rem; }

.section-title { margin: 0.25rem 0 0; font-size: 1.05rem; }
.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.9rem;
}
.quick-card {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  text-decoration: none;
  color: var(--text);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.quick-card:hover { transform: translateY(-2px); }
.quick-icon { font-size: 1.5rem; }
.quick-card strong { font-size: 1rem; }
.quick-card small { color: var(--text-muted); }
.quick-cta { margin-top: 0.4rem; color: var(--primary-color); font-size: 0.85rem; }
.toast[data-type='error'] { color: #d64545; font-size: 0.85rem; }
</style>
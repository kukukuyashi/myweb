<template>
  <aside class="platform-home-aside">
    <div class="panel">
      <div class="panel-header">分区</div>
      <nav class="panel-body aside-nav">
        <a
          v-for="item in sectionNav"
          :key="item.id"
          :href="`#${item.id}`"
          class="aside-nav-link"
          @click.prevent="$emit('section', item.id)"
        >
          {{ item.label }}
        </a>
      </nav>
    </div>

    <div class="panel">
      <div class="panel-header">Live</div>
      <div class="panel-body aside-live">
        <PlatformStatsClock :site-days="siteDays" :profile="profile" />
      </div>
    </div>

    <div v-if="stats" class="panel">
      <div class="panel-header">Pomo</div>
      <div class="panel-body aside-pomo">
        <div class="aside-stat-row">
          <span>今日</span>
          <strong>{{ stats.today_minutes }}m</strong>
        </div>
        <div class="aside-stat-row">
          <span>本周</span>
          <strong>{{ stats.week_minutes }}m</strong>
        </div>
        <router-link to="/app/pomo" class="aside-pomo-link">打开番茄钟 →</router-link>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">最新文章</div>
      <div class="panel-body">
        <p v-if="postsLoading" class="aside-muted">加载中…</p>
        <ul v-else-if="recentPosts.length" class="aside-posts">
          <li v-for="p in recentPosts" :key="p.id">
            <router-link :to="`/app/posts/${p.id}`">{{ p.title }}</router-link>
            <time>{{ formatDate(p.published_at || p.created_at) }}</time>
          </li>
        </ul>
        <p v-else class="aside-muted">
          <router-link to="/app/me">去个人中心</router-link>
        </p>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">Quick</div>
      <nav class="panel-body aside-quick">
        <router-link to="/app/pomo">番茄钟</router-link>
        <router-link to="/app/forum">论坛</router-link>
        <router-link to="/app/me">个人中心</router-link>
        <router-link to="/">返回博客</router-link>
      </nav>
    </div>
  </aside>
</template>

<script setup>
import PlatformStatsClock from './PlatformStatsClock.vue'

defineProps({
  sectionNav: { type: Array, required: true },
  siteDays: { type: Number, default: 0 },
  profile: { type: Object, default: null },
  stats: { type: Object, default: null },
  recentPosts: { type: Array, default: () => [] },
  postsLoading: { type: Boolean, default: false },
})

defineEmits(['section'])

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
}
</script>

<style scoped>
.platform-home-aside {
  position: sticky;
  top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.panel {
  margin-bottom: 0.85rem;
}

.aside-nav {
  display: grid;
  gap: 0.35rem;
  padding: 0.75rem !important;
}

.aside-nav-link {
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--border);
  color: inherit;
  text-decoration: none;
  transition: border-color 0.15s, color 0.15s;
}

.aside-nav-link:hover {
  border-color: var(--orange);
  color: var(--orange);
}

.aside-live {
  padding: 0.65rem !important;
}

.aside-pomo {
  display: grid;
  gap: 0.35rem;
}

.aside-stat-row {
  display: flex;
  justify-content: space-between;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

.aside-stat-row strong {
  color: var(--orange);
}

.aside-pomo-link {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
  text-decoration: none;
  margin-top: 0.25rem;
}

.aside-posts {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.55rem;
}

.aside-posts a {
  display: block;
  font-size: 0.8rem;
  color: inherit;
  text-decoration: none;
  line-height: 1.35;
}

.aside-posts a:hover {
  color: var(--orange);
}

.aside-posts time {
  display: block;
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}

.aside-muted {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.aside-muted a {
  color: var(--orange);
}

.aside-quick {
  display: grid;
  gap: 0.3rem;
}

.aside-quick a {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  text-decoration: none;
}

.aside-quick a:hover {
  color: var(--orange);
}

@media (max-width: 960px) {
  .platform-home-aside {
    display: none;
  }
}
</style>

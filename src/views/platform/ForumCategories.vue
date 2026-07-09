<template>
  <div class="container layout-single">
    <header class="page-header">
      <p class="coord">FORUM · BOARDS</p>
      <h1 class="page-title">论坛</h1>
      <div class="head-actions">
        <router-link v-if="token" to="/app/forum/new" class="btn-primary">发帖</router-link>
        <router-link v-else to="/app/me" class="btn-ghost">登录后发帖</router-link>
      </div>
    </header>

    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else class="cat-grid">
      <router-link
        v-for="cat in categories"
        :key="cat.id"
        :to="`/app/forum/c/${cat.slug}`"
        class="cat-card"
      >
        <span class="tag">{{ cat.slug.toUpperCase() }}</span>
        <h2>{{ cat.name }}</h2>
        <p>{{ cat.description }}</p>
        <span class="count">{{ cat.thread_count }} 帖</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { usePageMeta } from '../../composables/usePageMeta'
import { fetchForumCategories, getPlatformToken } from '../../api/platform.js'

usePageMeta({ title: '论坛', description: 'CYINC 主站论坛板块。' })

const token = ref(getPlatformToken())
const categories = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const json = await fetchForumCategories()
    categories.value = json.data || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.coord {
  width: 100%;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  letter-spacing: 0.12em;
}

.head-actions { display: flex; gap: 0.5rem; }

.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.cat-card {
  border: 1px solid var(--border);
  background: var(--card-bg, #fff);
  padding: 1.25rem;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s;
}

.cat-card:hover { border-color: var(--orange); }

.cat-card .tag {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
}

.cat-card h2 { font-size: 1.05rem; margin: 0.35rem 0; }
.cat-card p { font-size: 0.82rem; color: var(--text-muted); margin: 0 0 0.5rem; }

.count {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.btn-primary, .btn-ghost {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.45rem 0.9rem;
  border: 1px solid var(--border);
  text-decoration: none;
  color: inherit;
}

.btn-primary {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.muted { color: var(--text-muted); }
.error { color: #c0392b; }
</style>

<template>
  <div class="container layout-single">
    <PlatformSubPageHeader coord="FORUM · CATEGORY">
      <router-link to="/app/forum" class="back">← 全部板块</router-link>
      <h1 class="page-title">{{ categoryName || '板块' }}</h1>
    </PlatformSubPageHeader>

    <section class="platform-panel ink-panel">
      <p v-if="loading" class="muted">加载中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <template v-else>
        <p v-if="!threads.length" class="muted">暂无帖子。</p>
        <ul v-else class="thread-list">
          <li v-for="t in threads" :key="t.id">
            <router-link :to="`/app/forum/t/${t.id}`" class="thread-title">
              <span v-if="t.is_pinned" class="pin">置顶</span>
              {{ t.title }}
            </router-link>
            <div class="thread-meta">
              <span>{{ t.author?.nickname || t.author?.username || '匿名' }}</span>
              <span>{{ t.reply_count }} 回复</span>
              <span>{{ t.view_count }} 浏览</span>
              <span>{{ formatDate(t.created_at) }}</span>
            </div>
          </li>
        </ul>
      </template>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import PlatformSubPageHeader from '../../components/platform/PlatformSubPageHeader.vue'
import { usePageMeta } from '../../composables/usePageMeta'
import { fetchForumCategories, fetchForumCategoryThreads } from '../../api/platform.js'

const props = defineProps({ slug: { type: String, required: true } })

const threads = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref('')

const categoryName = computed(() => {
  const cat = categories.value.find((c) => c.slug === props.slug)
  return cat?.name || props.slug
})

usePageMeta(() => ({
  title: categoryName.value || '板块',
  description: '论坛板块帖子列表。',
}))

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [catJson, threadJson] = await Promise.all([
      fetchForumCategories(),
      fetchForumCategoryThreads(props.slug),
    ])
    categories.value = catJson.data || []
    threads.value = threadJson.data.items || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch(() => props.slug, load)
onMounted(load)
</script>

<style scoped>
.back {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--orange);
  text-decoration: none;
  margin-bottom: 0.35rem;
}

.page-title {
  margin: 0.25rem 0 0;
  font-size: clamp(1.25rem, 3vw, 1.65rem);
}

.thread-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.thread-list li {
  padding: 0.85rem 0;
  border-bottom: 1px dashed var(--border);
}

.thread-list li:last-child {
  border-bottom: none;
}

.thread-title {
  color: inherit;
  text-decoration: none;
  font-weight: 500;
}

.thread-title:hover { color: var(--orange); }

.pin {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
  margin-right: 0.35rem;
}

.thread-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.35rem;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.muted { color: var(--text-muted); }
.error { color: #c0392b; }
</style>

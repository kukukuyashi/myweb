<template>
  <div class="container layout-single">
    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else-if="post">
      <PlatformSubPageHeader
        coord="POST · READ"
        :image="PLATFORM_POST_INK_IMAGE"
        :position="PLATFORM_POST_INK_POSITION"
      >
        <router-link to="/app/me" class="back">← 个人中心</router-link>
        <h1 class="page-title">{{ post.title }}</h1>
        <p class="meta">
          {{ post.author?.nickname || post.author?.username }} ·
          {{ post.category }} · {{ formatDate(post.published_at || post.created_at) }}
        </p>
        <div v-if="canEdit" class="toolbar">
          <router-link :to="`/app/posts/${post.id}/edit`" class="btn-ghost">编辑</router-link>
        </div>
      </PlatformSubPageHeader>

      <figure v-if="post.cover_url" class="platform-panel ink-panel post-cover">
        <img :src="coverUrl" :alt="post.title">
      </figure>

      <article class="platform-panel ink-panel body">
        <MarkdownBody :content="post.content" />
      </article>
      <p v-if="post.ai_summary" class="platform-panel ink-panel summary">
        <strong>AI 摘要</strong> · {{ post.ai_summary }}
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import PlatformSubPageHeader from '../../components/platform/PlatformSubPageHeader.vue'
import { PLATFORM_POST_INK_IMAGE, PLATFORM_POST_INK_POSITION } from '../../data/inkTheme.js'
import { usePageMeta } from '../../composables/usePageMeta'
import MarkdownBody from '../../components/MarkdownBody.vue'
import { fetchPost, fetchProfile, getPlatformToken, resolveMediaUrl } from '../../api/platform.js'

const props = defineProps({ id: { type: [String, Number], required: true } })

const post = ref(null)
const profile = ref(null)
const loading = ref(true)
const error = ref('')
const token = ref(getPlatformToken())

const canEdit = computed(() => {
  if (!post.value || !profile.value) return false
  return post.value.user_id === profile.value.id
})

const coverUrl = computed(() => resolveMediaUrl(post.value?.cover_url))

usePageMeta(() => ({
  title: post.value?.title || '文章',
  description: post.value?.ai_summary || '主站文章阅读。',
  image: coverUrl.value || undefined,
}))

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const json = await fetchPost(props.id, { auth: !!token.value })
    post.value = json.data
    if (token.value) {
      try {
        const me = await fetchProfile()
        profile.value = me.data
      } catch {
        profile.value = null
      }
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch(() => props.id, load)
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
  font-size: clamp(1.25rem, 3vw, 1.75rem);
}

.meta {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
}

.toolbar { margin-top: 0.75rem; }

.btn-ghost {
  font-family: var(--mono);
  font-size: 0.75rem;
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  text-decoration: none;
  color: inherit;
}

.body {
  font-size: 0.95rem;
  margin-top: 1rem;
}

.post-cover {
  margin-top: 0.75rem;
  padding: 0;
  overflow: hidden;
}

.post-cover img {
  display: block;
  width: 100%;
  max-height: 360px;
  object-fit: cover;
  aspect-ratio: 16 / 9;
}

.summary {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 1rem;
}

.muted { color: var(--text-muted); }
.error { color: #c0392b; }
</style>

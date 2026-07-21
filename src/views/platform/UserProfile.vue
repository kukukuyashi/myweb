<template>
  <div class="container layout-single">
    <PlatformSubPageHeader coord="FORUM · USER">
      <router-link to="/app/forum" class="back">← 论坛</router-link>
      <p v-if="loading" class="muted">加载中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else-if="profile" class="up-head">
        <img
          v-if="avatarUrl"
          :src="avatarUrl"
          alt=""
          class="up-avatar"
        >
        <span v-else class="up-avatar up-avatar--placeholder" aria-hidden="true">
          {{ (profile.nickname || profile.username || '?').slice(0, 1) }}
        </span>
        <div class="up-meta">
          <h1 class="page-title">
            {{ profile.nickname || profile.username }}
            <LevelBadge
              v-if="profile.level >= 2"
              :level="profile.level"
              :level-title="profile.level_title"
            />
          </h1>
          <p class="up-sub">@{{ profile.username }} · 注册于 {{ formatDate(profile.created_at) }}</p>
          <p class="up-stats">
            <span>Lv.{{ profile.level }} {{ profile.level_title }}</span>
            <span>· {{ profile.xp }} XP</span>
            <span>· {{ profile.thread_count }} 帖</span>
          </p>
        </div>
      </div>
    </PlatformSubPageHeader>

    <section v-if="profile" class="platform-panel ink-panel up-threads">
      <h2 class="up-threads-title">TA 的帖子</h2>
      <p v-if="!threads.length" class="muted">还没有发过帖子。</p>
      <ul v-else class="up-thread-list">
        <li v-for="t in threads" :key="t.id" class="up-thread-item">
          <router-link :to="`/app/forum/t/${t.id}`" class="up-thread-link">
            <img
              v-if="t.cover_url"
              :src="resolvePublicUrl(t.cover_url)"
              alt=""
              class="up-thread-cover"
              loading="lazy"
            >
            <div class="up-thread-body">
              <h3 class="up-thread-title">{{ t.title }}</h3>
              <p class="up-thread-info">
                <span v-if="t.category_name">{{ t.category_name }}</span>
                · {{ formatDate(t.created_at) }}
                · 👁 {{ t.view_count || 0 }}
                · 💬 {{ t.reply_count || 0 }}
                · ♥ {{ t.like_count || 0 }}
              </p>
            </div>
          </router-link>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import PlatformSubPageHeader from '../../components/platform/PlatformSubPageHeader.vue'
import LevelBadge from '../../components/LevelBadge.vue'
import { usePageMeta } from '../../composables/usePageMeta'
import {
  fetchUserProfile,
  fetchUserThreads,
  resolvePublicUrl,
} from '../../api/platform.js'

const props = defineProps({ id: { type: [String, Number], required: true } })

const profile = ref(null)
const threads = ref([])
const loading = ref(true)
const error = ref('')

usePageMeta({ title: '用户主页', description: '查看用户的公开资料与帖子。' })

const avatarUrl = ref('')

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('zh-CN')
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [pJson, tJson] = await Promise.all([
      fetchUserProfile(props.id),
      fetchUserThreads(props.id),
    ])
    profile.value = pJson.data
    avatarUrl.value = resolvePublicUrl(pJson.data?.avatar || '')
    threads.value = tJson.data?.items || []
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
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--orange);
  text-decoration: none;
}

.up-head {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.up-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.up-avatar--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--orange-light);
  color: var(--orange);
  font-family: var(--mono);
  font-size: 1.8rem;
}

.up-meta .page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 0;
}

.up-sub,
.up-stats {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin: 0.35rem 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.up-threads {
  margin-top: 0.75rem;
}

.up-threads-title {
  font-size: 0.95rem;
  margin: 0 0 0.75rem;
}

.up-thread-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.6rem;
}

.up-thread-link {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  padding: 0.6rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s, background 0.15s;
}

.up-thread-link:hover {
  border-color: color-mix(in srgb, var(--orange) 45%, var(--border));
  background: color-mix(in srgb, var(--orange) 5%, transparent);
}

.up-thread-cover {
  width: 96px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.up-thread-title {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.up-thread-info {
  margin: 0.3rem 0 0;
  font-family: var(--mono);
  font-size: 0.66rem;
  color: var(--text-muted);
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.muted { color: var(--text-muted); font-size: 0.85rem; }
.error { color: #c0392b; font-size: 0.85rem; }
</style>
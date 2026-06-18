<template>
  <div class="tag-view">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <header class="tag-header">
            <p class="page-ink-coord">TAG · FILTER · ARCHIVE</p>
            <h1 class="page-title">#{{ tagName }}</h1>
            <p class="tag-meta">{{ posts.length }} 篇文章</p>
          </header>

          <ul v-if="posts.length" class="tag-post-list">
            <li v-for="post in posts" :key="post.id" class="tag-post-row">
              <span class="tag-post-date">{{ post.date }}</span>
              <router-link :to="post.url" class="tag-post-title">{{ post.title }}</router-link>
              <span class="tag-post-cat">{{ post.category }}</span>
            </li>
          </ul>

          <SystemHaltPanel
            v-else
            compact
            code="EMPTY"
            headline="NO POSTS"
            message="该标签下暂无文章"
            status="TAG_IDLE"
            :lines="[`TAG:: ${tagName}`, 'HINT:: try another tag from archive']"
            home-label="← 返回首页"
          />

          <nav v-if="relatedTags.length" class="tag-related">
            <span class="tag-related-label">相关标签</span>
            <router-link
              v-for="t in relatedTags"
              :key="t"
              :to="tagUrl(t)"
              class="tag-related-link"
            >#{{ t }}</router-link>
          </nav>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import SystemHaltPanel from '../components/SystemHaltPanel.vue'
import { usePageMeta, pageUrl } from '../composables/usePageMeta'
import { getPostsByTag, getTags, tagUrl } from '../data/posts'

const route = useRoute()
const tagName = computed(() => decodeURIComponent(route.params.tag || ''))
const posts = computed(() => getPostsByTag(tagName.value))

const relatedTags = computed(() => {
  const current = new Set(posts.value.flatMap(p => p.tags || []))
  current.delete(tagName.value)
  return getTags().filter(t => current.has(t)).slice(0, 8)
})

usePageMeta(() => ({
  title: `#${tagName.value}`,
  description: `标签 #${tagName.value} 下的 ${posts.value.length} 篇文章。`,
  url: pageUrl(`tags/${encodeURIComponent(tagName.value)}`),
}))
</script>

<style scoped>
.tag-header {
  margin-bottom: 1.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed var(--border);
}

.tag-meta {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
}

.tag-post-list {
  list-style: none;
}

.tag-post-row {
  display: grid;
  grid-template-columns: 6.5rem 1fr auto;
  gap: 1rem;
  align-items: baseline;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.9rem;
}

.tag-post-date {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
}

.tag-post-title {
  color: var(--text);
  text-decoration: none;
  line-height: 1.4;
}

.tag-post-title:hover {
  color: var(--orange);
}

.tag-post-cat {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--steel);
  white-space: nowrap;
}

.tag-related {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  margin-top: 2rem;
  padding-top: 1.25rem;
  border-top: 1px dashed var(--border);
}

.tag-related-label {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  letter-spacing: 0.08em;
}

.tag-related-link {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--steel);
  text-decoration: none;
  padding: 0.15rem 0.45rem;
  border: 1px solid var(--border);
}

.tag-related-link:hover {
  color: var(--orange);
  border-color: var(--orange);
}

@media (max-width: 640px) {
  .tag-post-row {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }
}
</style>

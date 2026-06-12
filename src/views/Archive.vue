<template>
  <div class="archive">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <h1 class="page-title">文章归档</h1>
          <div class="archive-meta">
            TOTAL {{ totalPosts }} POSTS · {{ totalTags }} TAGS · LAST UPDATE {{ lastUpdate }}
          </div>

          <div v-if="allTags.length" class="archive-tags">
            <router-link
              v-for="tag in allTags"
              :key="tag"
              :to="{ path: '/', query: { tag } }"
              class="archive-tag"
            >#{{ tag }}</router-link>
          </div>

          <template v-for="group in archiveGroups" :key="group.year">
            <h2 class="archive-year">{{ group.year }}</h2>
            <template v-for="month in group.months" :key="`${group.year}-${month.month}`">
              <h3 class="archive-month">{{ month.label }}</h3>
              <ul class="archive-items">
                <li v-for="post in month.posts" :key="post.id">
                  <span class="date">{{ post.date }}</span>
                  <router-link :to="post.url">{{ post.title }}</router-link>
                  <span v-if="post.tags?.length" class="post-tags">
                    <span v-for="t in post.tags.slice(0, 2)" :key="t" class="mini-tag">{{ t }}</span>
                  </span>
                </li>
              </ul>
            </template>
          </template>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { computed } from 'vue'
import { posts, buildArchive, getLastUpdateDate, getTags } from '../data/posts'
import { usePageMeta } from '../composables/usePageMeta'

usePageMeta({ title: '归档', description: '按年月浏览全部技术学习笔记。' })

const totalPosts = computed(() => posts.length)
const totalTags = computed(() => getTags().length)
const allTags = computed(() => getTags())
const lastUpdate = computed(() => getLastUpdateDate())
const archiveGroups = computed(() => buildArchive())
</script>

<style scoped>
.archive-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 2rem;
}

.archive-tag {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--steel);
  text-decoration: none;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border);
}

.archive-tag:hover {
  color: var(--orange);
  border-color: var(--orange);
}

.post-tags {
  margin-left: auto;
  display: flex;
  gap: 0.25rem;
}

.mini-tag {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}

.archive-items li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
</style>

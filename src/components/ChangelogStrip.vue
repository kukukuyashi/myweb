<template>
  <section v-if="entries.length" class="changelog-strip reveal-item" data-reveal :style="{ '--reveal-delay': `${delay}ms` }">
    <div class="changelog-strip-head">
      <span class="changelog-strip-label">站点更新</span>
      <router-link to="/changelog" class="changelog-strip-all">全部日志 →</router-link>
    </div>
    <ul class="changelog-strip-list">
      <li v-for="entry in entries" :key="entry.version + entry.date" class="changelog-strip-item">
        <router-link :to="linkFor(entry)" class="changelog-strip-link">
          <span class="changelog-strip-meta">
            <time :datetime="entry.date">{{ entry.date }}</time>
            <span class="changelog-strip-ver">{{ entry.version }}</span>
          </span>
          <span class="changelog-strip-title">{{ entry.title }}</span>
          <span class="changelog-strip-summary">{{ entry.summary }}</span>
        </router-link>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { getRecentChangelog } from '../data/changelog'
import { postUrl } from '../data/posts'

const props = defineProps({
  limit: { type: Number, default: 2 },
  delay: { type: Number, default: 90 },
})

const entries = computed(() => getRecentChangelog(props.limit))

function linkFor(entry) {
  if (entry.postId) return postUrl(entry.postId)
  return '/changelog'
}
</script>

<style scoped>
.changelog-strip {
  margin-bottom: 1.25rem;
  padding: 0.85rem 1rem 0.95rem;
  border: 1px solid var(--border);
  border-left: 3px solid var(--steel);
  background: var(--bg-paper);
}

.changelog-strip-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.65rem;
}

.changelog-strip-label {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--steel);
}

.changelog-strip-all {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  text-decoration: none;
}

.changelog-strip-all:hover {
  color: var(--orange);
}

.changelog-strip-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.changelog-strip-item {
  border-top: 1px dashed var(--border);
  padding-top: 0.55rem;
}

.changelog-strip-item:first-child {
  border-top: none;
  padding-top: 0;
}

.changelog-strip-link {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.2rem;
  text-decoration: none;
  color: inherit;
  transition: color 0.15s;
}

.changelog-strip-link:hover .changelog-strip-title {
  color: var(--orange);
}

.changelog-strip-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.changelog-strip-ver {
  color: var(--orange);
  opacity: 0.85;
}

.changelog-strip-title {
  font-size: 0.88rem;
  font-weight: 500;
  line-height: 1.35;
  color: var(--text);
  transition: color 0.15s;
}

.changelog-strip-summary {
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 640px) {
  .changelog-strip {
    padding: 0.75rem 0.85rem;
  }
}
</style>

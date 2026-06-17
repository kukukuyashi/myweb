<template>
  <section v-if="series.length" class="series-section reveal-item" data-reveal :style="{ '--reveal-delay': `${delay}ms` }">
    <div class="section-head">
      <h2>系列</h2>
      <span class="series-head-note">按主题读，不必从归档里翻</span>
    </div>
    <div class="series-grid">
      <article
        v-for="item in series"
        :key="item.slug"
        class="series-card"
        :style="{ '--series-accent': item.accent }"
      >
        <header class="series-card-head">
          <span class="series-card-slug">{{ item.slug }}</span>
          <span class="series-card-count">{{ item.count }} 篇</span>
        </header>
        <h3 class="series-card-title">{{ item.title }}</h3>
        <p class="series-card-sub">{{ item.subtitle }}</p>
        <p class="series-card-desc">{{ item.description }}</p>
        <ol class="series-card-posts">
          <li v-for="post in item.posts.slice(0, 4)" :key="post.id">
            <router-link :to="post.url">{{ post.title }}</router-link>
          </li>
          <li v-if="item.count > 4" class="series-card-more">+{{ item.count - 4 }} 篇…</li>
        </ol>
      </article>
    </div>
  </section>
</template>

<script setup>
import { getSeriesList } from '../data/series'

defineProps({
  delay: { type: Number, default: 140 },
})

const series = getSeriesList()
</script>

<style scoped>
.series-head-note {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.series-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.series-card {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  padding: 1rem 1.1rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  border-top: 3px solid var(--series-accent, var(--orange));
  transition: border-color 0.15s, transform 0.15s;
}

.series-card:hover {
  border-color: var(--series-accent, var(--orange));
  transform: translateY(-2px);
}

.series-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.series-card-slug {
  color: var(--series-accent, var(--orange));
  text-transform: uppercase;
}

.series-card-title {
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
}

.series-card-sub {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--steel);
  margin: 0;
  letter-spacing: 0.03em;
}

.series-card-desc {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.45;
  margin: 0.15rem 0 0.35rem;
  flex: 1;
}

.series-card-posts {
  list-style: none;
  margin: 0;
  padding: 0.65rem 0 0;
  border-top: 1px dashed var(--border);
  counter-reset: series-post;
}

.series-card-posts li {
  padding: 0.3rem 0;
  font-size: 0.78rem;
  line-height: 1.35;
}

.series-card-posts li::before {
  counter-increment: series-post;
  content: counter(series-post, decimal-leading-zero) ' · ';
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
}

.series-card-posts a {
  color: var(--text);
  text-decoration: none;
}

.series-card-posts a:hover {
  color: var(--series-accent, var(--orange));
}

.series-card-more {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.series-card-more::before {
  content: none !important;
}
</style>

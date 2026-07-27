<template>
  <div class="links-page platform-page container layout-single">
    <header class="links-hero platform-panel ink-panel">
      <p class="platform-coord">FRIENDS · LINKS · WEB</p>
      <h1 class="links-title">友链</h1>
      <p class="links-lead">
        这里收录一些<strong>朋友的博客</strong>、有意思的<strong>视频</strong>和值得一逛的角落。
        点开卡片即可跳转到对应站点。
      </p>
    </header>

    <div v-if="categories.length > 1" class="links-filter">
      <button
        type="button"
        class="links-chip"
        :class="{ active: activeCat === '' }"
        @click="activeCat = ''"
      >全部</button>
      <button
        v-for="c in categories"
        :key="c"
        type="button"
        class="links-chip"
        :class="{ active: activeCat === c }"
        @click="activeCat = c"
      >{{ c }}</button>
    </div>

    <p v-if="loading" class="links-state">加载中…</p>
    <p v-else-if="!filtered.length" class="links-state">还没有友链，敬请期待。</p>

    <section v-else class="links-gallery">
      <a
        v-for="x in filtered"
        :key="x.id"
        :href="x.url"
        target="_blank"
        rel="noopener"
        class="links-card platform-panel"
      >
        <div class="links-card-media">
          <img v-if="x.image_url" :src="x.image_url" :alt="x.name" loading="lazy" />
          <span v-else class="links-card-fallback" aria-hidden="true">{{ initial(x.name) }}</span>
        </div>
        <div class="links-card-main">
          <div class="links-card-top">
            <h2 class="links-card-name">{{ x.name }}</h2>
            <span v-if="x.category" class="links-card-tag">{{ x.category }}</span>
          </div>
          <p v-if="x.description" class="links-card-desc">{{ x.description }}</p>
          <span class="links-card-go">访问 →</span>
        </div>
      </a>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchFriendLinksPublic } from '../../api/friendLinks'

const links = ref([])
const loading = ref(true)
const activeCat = ref('')

const categories = computed(() => {
  const set = new Set()
  for (const x of links.value) if (x.category) set.add(x.category)
  return [...set]
})

const filtered = computed(() => {
  if (!activeCat.value) return links.value
  return links.value.filter((x) => x.category === activeCat.value)
})

function initial(name) {
  return (name || '?').trim().charAt(0).toUpperCase()
}

onMounted(async () => {
  try {
    const data = await fetchFriendLinksPublic()
    links.value = data.links || []
  } catch {
    links.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.links-hero { text-align: left; }
.links-title {
  font-family: var(--mono);
  font-size: clamp(1.5rem, 4vw, 2.1rem);
  margin: 0.35rem 0 0.5rem;
}
.links-lead {
  color: var(--text-muted);
  line-height: 1.7;
  margin: 0;
  max-width: 46rem;
}
.links-lead strong { color: var(--orange); }

.links-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}
.links-chip {
  font-family: var(--mono);
  font-size: 0.74rem;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--bg-paper);
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}
.links-chip:hover { color: var(--text); border-color: var(--orange); }
.links-chip.active {
  color: #fff;
  background: var(--orange);
  border-color: var(--orange);
}

.links-state {
  margin-top: 1.5rem;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 0.85rem;
}

.links-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(17rem, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.links-card {
  display: flex;
  gap: 0.85rem;
  text-decoration: none;
  color: inherit;
  overflow: hidden;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}
.links-card:hover {
  transform: translateY(-3px);
  border-color: color-mix(in srgb, var(--orange) 45%, var(--border));
  box-shadow: 0 8px 22px color-mix(in srgb, var(--text) 10%, transparent);
}

.links-card-media {
  flex: 0 0 4.5rem;
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
}
.links-card-media img { width: 100%; height: 100%; object-fit: cover; }
.links-card-fallback {
  font-family: var(--mono);
  font-size: 1.8rem;
  color: var(--orange);
}

.links-card-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.links-card-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.links-card-name {
  font-family: var(--mono);
  font-size: 1.02rem;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.links-card-tag {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.04em;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: var(--orange-light);
  color: var(--orange);
  white-space: nowrap;
}
.links-card-desc {
  color: var(--text-muted);
  font-size: 0.82rem;
  line-height: 1.55;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.links-card-go {
  font-family: var(--mono);
  font-size: 0.74rem;
  color: var(--orange);
  margin-top: auto;
  padding-top: 0.25rem;
}
</style>
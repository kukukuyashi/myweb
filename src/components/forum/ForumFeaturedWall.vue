<template>
  <div class="forum-featured-wall">
    <header class="forum-featured-head">
      <h2 class="forum-featured-title">精选话题</h2>
      <p class="forum-featured-sub">贴纸墙 · 共 {{ items.length }} 篇</p>
    </header>
    <StickerWall mode="forum" :items="wallItems" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StickerWall from '../StickerWall.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const wallItems = computed(() =>
  props.items.map((item, index) => ({
    path: item.cover || '',
    label: String(index + 1).padStart(2, '0'),
    title: item.title,
    subtitle: item.category_name || '',
    to: item.id ? `/app/forum/t/${item.id}` : null,
  })),
)
</script>

<style scoped>
.forum-featured-head {
  margin-bottom: 0.85rem;
}

.forum-featured-title {
  margin: 0;
  font-size: 1.05rem;
}

.forum-featured-sub {
  margin: 0.25rem 0 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}
</style>

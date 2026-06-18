<template>
  <article
    class="post-card reveal-item"
    :class="{ 'post-card--featured': featured }"
    data-reveal
    :style="{ '--cat-color': categoryColor, '--reveal-delay': `${revealDelay}ms` }"
  >
    <div class="post-card-accent" aria-hidden="true" />
    <div class="post-card-body">
      <div class="post-card-top">
        <span v-if="featured" class="post-card-badge">精选</span>
        <span class="post-card-category">{{ post.category }}</span>
        <span class="post-card-meta">{{ post.date }} · {{ readingMinutes }} min</span>
      </div>
      <div class="post-card-main">
        <div v-if="thumbUrl" class="post-card-thumb">
          <img :src="thumbUrl" :alt="post.title" loading="lazy">
        </div>
        <div v-else class="post-card-icon" aria-hidden="true">{{ categoryIcon }}</div>
        <div class="post-card-text">
          <h3>
            <router-link :to="post.url" @mouseenter="onArticleHover(post)">{{ post.title }}</router-link>
          </h3>
          <p>{{ post.excerpt }}</p>
        </div>
      </div>
      <div v-if="post.tags?.length" class="post-card-tags">
        <router-link
          v-for="tag in post.tags.slice(0, 4)"
          :key="tag"
          :to="tagUrl(tag)"
          class="post-card-tag"
        >#{{ tag }}</router-link>
      </div>
      <router-link :to="post.url" class="post-card-read" @mouseenter="onArticleHover(post)">阅读笔记 →</router-link>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { getCategoryColor, getCategoryIcon, estimateReadingMinutesFromText, imgUrl, tagUrl, getPostCover, hasPostCover } from '../data/posts'
import { onArticleHover } from '../composables/useLinkPrefetch'

const props = defineProps({
  post: { type: Object, required: true },
  featured: { type: Boolean, default: false },
  revealDelay: { type: Number, default: 0 },
})

const categoryColor = computed(() => getCategoryColor(props.post.category))
const categoryIcon = computed(() => getCategoryIcon(props.post.category))
const readingMinutes = computed(() => estimateReadingMinutesFromText(`${props.post.title}${props.post.excerpt}`))
const thumbUrl = computed(() => {
  if (!hasPostCover(props.post)) return ''
  return imgUrl(getPostCover(props.post))
})
</script>

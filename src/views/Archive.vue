<template>
  <div class="archive">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <h1 class="page-title">文章归档</h1>
          <div class="archive-meta">
            TOTAL {{ totalPosts }} POSTS · LAST UPDATE {{ lastUpdate }}
          </div>

          <template v-for="group in archiveGroups" :key="group.year">
            <h2 class="archive-year">{{ group.year }}</h2>
            <template v-for="month in group.months" :key="`${group.year}-${month.month}`">
              <h3 class="archive-month">{{ month.label }}</h3>
              <ul class="archive-items">
                <li v-for="post in month.posts" :key="post.id">
                  <span class="date">{{ post.date }}</span>
                  <router-link :to="postUrl(post.title)">{{ post.title }}</router-link>
                </li>
              </ul>
            </template>
          </template>
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { computed } from 'vue'
import { posts, buildArchive, getLastUpdateDate, postUrl } from '../data/posts'

const totalPosts = computed(() => posts.length)
const lastUpdate = computed(() => getLastUpdateDate())
const archiveGroups = computed(() => buildArchive())
</script>

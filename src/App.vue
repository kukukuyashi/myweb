<template>
  <PageRails />
  <router-view />
  <MusicPlayer />
</template>

<script setup>
import PageRails from './components/PageRails.vue'
import MusicPlayer from './components/MusicPlayer.vue'
</script>

<template>
  <div class="music">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content music-room">
          <InkRevealPanel
            tag="header"
            root-class="page-ink-header"
            :image="MUSIC_HEADER_INK_IMAGE"
            :position="MUSIC_HEADER_INK_POSITION"
            :r-end="125"
            fade-direction="left"
          >
            <p class="page-ink-coord">MUSIC · OST · FLAC · <span class="ink-hint">hover 晕染</span></p>
            <h1 class="page-title">音乐室</h1>
            <p class="music-sub">收录 Cyinc 最喜欢的曲目</p>
          </InkRevealPanel>

          <MusicRoomBody />
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import InkRevealPanel from '../components/InkRevealPanel.vue'
import MusicRoomBody from '../components/MusicRoomBody.vue'
import { usePageMeta } from '../composables/usePageMeta'
import {
  MUSIC_HEADER_INK_IMAGE,
  MUSIC_HEADER_INK_POSITION,
} from '../data/inkTheme'

usePageMeta({ title: '音乐室', description: 'Cyinc 最喜欢的曲目，葬送のフリーレン OST、SANABI 等。' })
</script>

<style scoped>
.music-sub {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
}
</style>

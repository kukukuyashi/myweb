<template>
  <PlatformPageShell
    coord="MUSIC · OST · FLAC"
    title="音乐室"
    lead="收录 Cyinc 最喜欢的曲目 — 与博客音乐室共享播放列表，换页续播。"
    :ink-image="PLATFORM_MUSIC_INK_IMAGE"
    :ink-position="PLATFORM_MUSIC_INK_POSITION"
    :ink-r-end="116"
  >
    <section class="platform-panel ink-panel music-room-panel">
      <MusicRoomBody :show-ink="true" />
    </section>
  </PlatformPageShell>
</template>

<script setup>
import PlatformPageShell from '../../components/platform/PlatformPageShell.vue'
import MusicRoomBody from '../../components/MusicRoomBody.vue'
import { usePageMeta } from '../../composables/usePageMeta'
import { PLATFORM_MUSIC_INK_IMAGE, PLATFORM_MUSIC_INK_POSITION } from '../../data/inkTheme.js'

usePageMeta({
  title: '音乐室',
  description: 'Cyinc 最喜欢的曲目，葬送のフリーレン OST、SANABI 等。',
})
</script>

<style scoped>
.music-room-panel {
  padding: clamp(1rem, 2.5vw, 1.35rem);
}

.music-room-panel :deep(.player-panel) {
  border-radius: 0;
}

.music-room-panel :deep(.album-section) {
  margin-top: 0.5rem;
}
</style>

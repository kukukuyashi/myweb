<template>
  <InkRevealPanel
    v-if="ink"
    tag="section"
    root-class="album-section album-section--ink"
    :class="{ 'is-last': isLast }"
    :image="inkImage"
    :position="inkPosition"
    :r-end="112"
    :max-stamps="100"
    fade-direction="left"
  >
    <AlbumInner
      :album="album"
      :failed-covers="failedCovers"
      :playing-index="playingIndex"
      :is-album-active="isAlbumActive"
      :show-ink-hint="true"
      @select="$emit('select', $event)"
      @cover-error="$emit('cover-error', $event)"
    />
  </InkRevealPanel>

  <section v-else class="album-section" :class="{ 'is-last': isLast }">
    <AlbumInner
      :album="album"
      :failed-covers="failedCovers"
      :playing-index="playingIndex"
      :is-album-active="isAlbumActive"
      :show-ink-hint="false"
      @select="$emit('select', $event)"
      @cover-error="$emit('cover-error', $event)"
    />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import InkRevealPanel from './InkRevealPanel.vue'
import AlbumInner from './MusicAlbumInner.vue'

const props = defineProps({
  album: { type: Object, required: true },
  failedCovers: { type: Object, required: true },
  playingIndex: { type: Number, default: -1 },
  isPlaying: { type: Boolean, default: false },
  ink: { type: Boolean, default: false },
  inkImage: { type: String, default: '' },
  inkPosition: { type: String, default: 'center' },
  isLast: { type: Boolean, default: false },
})

defineEmits(['select', 'cover-error'])

const isAlbumActive = computed(() =>
  props.isPlaying &&
  props.playingIndex >= 0 &&
  props.album.tracks.some(t => t.index === props.playingIndex)
)
</script>

<style scoped>
.album-section {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed var(--border);
}

.album-section.is-last,
.album-section--ink.is-last {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.album-section--ink {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 2.5rem;
}

:deep(.album-section--ink .ink-panel__content) {
  padding: 1.25rem 1.35rem 1.5rem;
}

:deep(.album-section--ink + .album-section) {
  margin-top: 0.5rem;
}
</style>

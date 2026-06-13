<template>
  <div class="album-section-inner">
    <div class="album-head">
      <div
        class="album-cover-lg acg-frame"
        :class="{ 'album-cover-lg--pulse': isAlbumActive }"
      >
        <img
          v-if="album.coverUrl && !failedCovers.has(album.source)"
          :src="album.coverUrl"
          :alt="album.source"
          loading="lazy"
          @error="$emit('cover-error', album.source)"
        >
        <span v-else class="album-cover-lg-fallback">{{ albumLabel(album.source) }}</span>
      </div>
      <div class="album-meta">
        <h2 class="album-title">
          <span class="album-tag">{{ album.source }}</span>
          <span class="album-count">{{ album.tracks.length }} tracks</span>
        </h2>
        <p v-if="album.coverUrl && !failedCovers.has(album.source)" class="album-cover-hint">folder.jpg</p>
        <p v-if="showInkHint" class="album-ink-hint"><span class="ink-hint">hover 晕染</span></p>
      </div>
    </div>
    <table class="post-table music-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Track</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="track in album.tracks"
          :key="track.index"
          :class="{ active: playingIndex === track.index }"
          @click="$emit('select', track.index)"
        >
          <td class="idx">{{ String(track.index + 1).padStart(2, '0') }}</td>
          <td>{{ track.name }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  album: { type: Object, required: true },
  failedCovers: { type: Object, required: true },
  playingIndex: { type: Number, default: -1 },
  isAlbumActive: { type: Boolean, default: false },
  showInkHint: { type: Boolean, default: false },
})

defineEmits(['select', 'cover-error'])

function albumLabel(source) {
  return String(source || '♪').slice(0, 2)
}
</script>

<style scoped>
.album-head {
  display: flex;
  gap: 1.25rem;
  align-items: flex-end;
  margin-bottom: 1rem;
}

.album-cover-lg {
  width: 132px;
  height: 132px;
  flex-shrink: 0;
  overflow: hidden;
}

.album-cover-lg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.album-cover-lg-fallback {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  font-family: var(--mono);
  font-size: 1.25rem;
  color: var(--steel);
  background: var(--bg);
}

.album-cover-lg--pulse {
  animation: cover-pulse 2s ease-in-out infinite;
}

@keyframes cover-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(232, 93, 4, 0.35); }
  50% { box-shadow: 0 0 0 6px rgba(232, 93, 4, 0); }
}

.album-meta {
  flex: 1;
  min-width: 0;
  padding-bottom: 0.15rem;
}

.album-title {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 0;
  font-family: var(--mono);
  font-size: 0.85rem;
  font-weight: 500;
}

.album-cover-hint,
.album-ink-hint {
  margin: 0.35rem 0 0;
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  opacity: 0.7;
}

.album-tag {
  color: var(--orange);
  letter-spacing: 0.04em;
}

.album-count {
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 400;
}

.music-table tr {
  cursor: pointer;
}

.music-table tr.active td {
  background: color-mix(in srgb, var(--bg-paper) 70%, var(--orange-light));
}

.music-table tr.active td:first-child {
  color: var(--orange);
}

@media (max-width: 640px) {
  .album-head {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .album-title {
    justify-content: center;
  }

  .album-cover-lg {
    width: 100%;
    max-width: 220px;
    height: auto;
    aspect-ratio: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .album-cover-lg--pulse {
    animation: none;
  }
}
</style>

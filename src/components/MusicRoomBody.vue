<template>
  <div class="music-room-body">
    <p v-if="musicNoticeText" class="music-notice">
      {{ musicNoticeText }}
    </p>

    <div class="player-panel">
      <div class="player-main">
        <div
          class="album-cover"
          :class="{ 'album-cover--pulse': musicStore.isPlaying && currentCoverUrl }"
        >
          <img
            v-if="currentCoverUrl && coverVisible"
            :src="currentCoverUrl"
            :alt="currentTrack?.album || '专辑封面'"
            @error="coverVisible = false"
          >
          <span v-else class="album-cover-fallback">{{ currentAlbumLabel }}</span>
        </div>
        <div class="player-screen">
          <span class="screen-line">{{ playerStatus }}</span>
          <span class="screen-line dim">{{ systemStatus }}</span>
        </div>
      </div>
      <div class="player-btns">
        <button class="ctrl-btn" :disabled="!musicStore.hasPrev()" @click="playPrev" aria-label="上一首">PREV</button>
        <button class="ctrl-btn" @click="togglePlay" :disabled="!currentTrack" :aria-label="musicStore.isPlaying ? '暂停' : '播放'">
          {{ musicStore.isPlaying ? 'PAUSE' : 'PLAY' }}
        </button>
        <button class="ctrl-btn" :disabled="!musicStore.hasNext()" @click="playNext" aria-label="下一首">NEXT</button>
        <button class="ctrl-btn" @click="stopPlay" :disabled="!currentTrack" aria-label="停止">STOP</button>
      </div>
    </div>

    <MusicAlbumSection
      v-for="(album, i) in albumGroups"
      :key="album.source"
      :album="album"
      :failed-covers="failedCovers"
      :playing-index="musicStore.currentIndex"
      :is-playing="musicStore.isPlaying"
      :ink="showInk && i === 0"
      :ink-image="MUSIC_FREREN_INK_IMAGE"
      :ink-position="MUSIC_FREREN_INK_POSITION"
      :is-last="i === albumGroups.length - 1"
      @select="selectTrack"
      @cover-error="markCoverFailed"
    />

    <p class="now-playing">
      {{ currentTrack ? '▶ ' + currentTrack.name : 'Select a track →' }}
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useMusicStore } from '../store'
import { musicTracks } from '../data/musicTracks'
import { buildTrackList, getMusicBase, groupTracksByAlbum, getCurrentAlbumCover, isServerHostedMusic } from '../utils/music'
import { playTrackAtIndex, pausePlayback, playCurrentTrack } from '../composables/useMusicPlayback.js'
import MusicAlbumSection from './MusicAlbumSection.vue'
import { MUSIC_FREREN_INK_IMAGE, MUSIC_FREREN_INK_POSITION } from '../data/inkTheme'

defineProps({
  /** 博客页首专辑区块是否带墨染 */
  showInk: { type: Boolean, default: true },
})

const musicStore = useMusicStore()
const coverVisible = ref(true)
const failedCovers = ref(new Set())

function markCoverFailed(source) {
  failedCovers.value = new Set([...failedCovers.value, source])
}

const musicNoticeText = computed(() => {
  if (getMusicBase()) return '音频从 CDN 加载。'
  if (import.meta.env.DEV) return '本地 dev：Music/ 由 Vite 中间件提供。'
  if (isServerHostedMusic()) {
    return '音频由服务器 /myweb/Music/ 提供（不打包进前端，部署更快）。若无法播放请检查 Nginx 是否挂载 Music 目录。'
  }
  return '音频从本站静态资源加载。'
})

const tracks = ref(buildTrackList(musicTracks))
const albumGroups = computed(() => groupTracksByAlbum(tracks.value))

const currentTrack = computed(() => {
  const idx = musicStore.currentIndex
  if (idx < 0 || idx >= tracks.value.length) return null
  return tracks.value[idx]
})

const currentCoverUrl = computed(() =>
  getCurrentAlbumCover(tracks.value, musicStore.currentIndex)
)

watch(() => musicStore.currentIndex, () => {
  coverVisible.value = true
})

const currentAlbumLabel = computed(() => {
  const track = currentTrack.value
  if (!track) return '♪'
  return (track.album || track.source || '♪').slice(0, 2)
})

const playerStatus = ref('▶ STOPPED')
const systemStatus = ref('SYSTEM READY...')

function syncPanelFromStore() {
  if (musicStore.currentIndex >= 0 && musicStore.currentSong) {
    playerStatus.value = musicStore.isPlaying ? '▶ PLAYING' : '▶ PAUSED'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  } else {
    playerStatus.value = '▶ STOPPED'
    systemStatus.value = 'SYSTEM READY...'
  }
}

function selectTrack(index) {
  void playTrackAtIndex(index).then((ok) => {
    if (!ok) return
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  })
}

function playPrev() {
  if (musicStore.currentIndex <= 0) return
  void playTrackAtIndex(musicStore.currentIndex - 1).then((ok) => {
    if (!ok) return
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  })
}

function playNext() {
  if (musicStore.currentIndex < 0 || musicStore.currentIndex >= musicStore.playlist.length - 1) return
  void playTrackAtIndex(musicStore.currentIndex + 1).then((ok) => {
    if (!ok) return
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  })
}

function togglePlay() {
  if (musicStore.isPlaying) {
    pausePlayback()
    playerStatus.value = '▶ PAUSED'
    systemStatus.value = 'PLAYBACK PAUSED'
    return
  }
  void playCurrentTrack().then((ok) => {
    if (!ok) return
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  })
}

function stopPlay() {
  musicStore.resetPlayback()
  playerStatus.value = '▶ STOPPED'
  systemStatus.value = 'PLAYBACK STOPPED'
}

onMounted(() => {
  musicStore.setPlaylist(tracks.value)
  syncPanelFromStore()
})
</script>

<style scoped>
.music-notice {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  margin: 0 0 1.5rem;
  line-height: 1.6;
}

.music-notice code {
  font-size: 0.65rem;
  background: var(--orange-light);
  padding: 0.1rem 0.35rem;
}

.player-panel {
  background: var(--topbar-bg);
  color: #fff;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  border: 1px solid var(--border);
}

[data-theme="dark"] .player-panel {
  background: #0d0d0d;
}

.player-main {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.album-cover {
  flex-shrink: 0;
  width: 96px;
  height: 96px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  overflow: hidden;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.35);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.album-cover-fallback {
  font-family: var(--mono);
  font-size: 0.85rem;
  opacity: 0.6;
}

.album-cover--pulse {
  animation: cover-pulse 2s ease-in-out infinite;
}

@keyframes cover-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(232, 93, 4, 0.35); }
  50% { box-shadow: 0 0 0 6px rgba(232, 93, 4, 0); }
}

.player-screen {
  flex: 1;
  min-width: 0;
  font-family: var(--mono);
  font-size: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.screen-line.dim { opacity: 0.5; font-size: 0.7rem; }

.player-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.ctrl-btn {
  font-family: var(--mono);
  font-size: 0.75rem;
  padding: 0.4rem 1rem;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.15s;
}

.ctrl-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
}

.ctrl-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.now-playing {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 1rem;
}

@media (max-width: 640px) {
  .player-main {
    flex-direction: column;
    align-items: stretch;
  }

  .album-cover {
    width: 100%;
    max-width: 200px;
    height: 200px;
    align-self: center;
  }

  .player-btns {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }

  .ctrl-btn {
    width: 100%;
    text-align: center;
    min-height: 40px;
  }

  .player-screen {
    font-size: 0.72rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .album-cover--pulse {
    animation: none;
  }
}
</style>

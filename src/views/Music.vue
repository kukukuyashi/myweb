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
            :ink="i === 0"
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
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { ref, onMounted, computed, watch } from 'vue'
import { useMusicStore } from '../store'
import { usePageMeta } from '../composables/usePageMeta'
import { musicTracks } from '../data/musicTracks'
import { buildTrackList, getMusicBase, groupTracksByAlbum, getCurrentAlbumCover } from '../utils/music'
import InkRevealPanel from '../components/InkRevealPanel.vue'
import MusicAlbumSection from '../components/MusicAlbumSection.vue'
import {
  MUSIC_HEADER_INK_IMAGE,
  MUSIC_HEADER_INK_POSITION,
  MUSIC_FREREN_INK_IMAGE,
  MUSIC_FREREN_INK_POSITION,
} from '../data/inkTheme'

usePageMeta({ title: '音乐室', description: 'Cyinc 最喜欢的曲目，葬送のフリーレン OST、SANABI 等。' })

const musicStore = useMusicStore()
const coverVisible = ref(true)
const failedCovers = ref(new Set())

function markCoverFailed(source) {
  failedCovers.value = new Set([...failedCovers.value, source])
}

const musicNoticeText = computed(() => {
  if (getMusicBase()) return ''
  if (import.meta.env.DEV) return '本地 dev 需项目根目录有 Music/ 文件夹。'
  return '音频从本站静态资源加载；若播放失败可配置 VITE_MUSIC_BASE_URL 使用 CDN。'
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
  musicStore.playAtIndex(index)
  playerStatus.value = '▶ PLAYING'
  systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
}

function playPrev() {
  if (musicStore.playPrev()) {
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  }
}

function playNext() {
  if (musicStore.playNext()) {
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  }
}

function togglePlay() {
  if (musicStore.isPlaying) {
    musicStore.setPlaying(false)
    playerStatus.value = '▶ PAUSED'
    systemStatus.value = 'PLAYBACK PAUSED'
  } else {
    musicStore.setPlaying(true)
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${musicStore.currentSong.title}`
  }
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
.music-sub {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
}

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

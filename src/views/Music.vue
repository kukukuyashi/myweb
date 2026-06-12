<template>
  <div class="music">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content music-room">
          <InkRevealPanel
            tag="header"
            root-class="page-ink-header"
            image="img/关于/FjtOo61UoAAWpMY.jfif"
            position="82% center"
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
            <div class="player-screen">
              <span class="screen-line">{{ playerStatus }}</span>
              <span class="screen-line dim">{{ systemStatus }}</span>
            </div>
            <div class="player-btns">
              <button class="ctrl-btn" :disabled="!musicStore.hasPrev()" @click="playPrev">PREV</button>
              <button class="ctrl-btn" @click="togglePlay" :disabled="!currentTrack">
                {{ musicStore.isPlaying ? 'PAUSE' : 'PLAY' }}
              </button>
              <button class="ctrl-btn" :disabled="!musicStore.hasNext()" @click="playNext">NEXT</button>
              <button class="ctrl-btn" @click="stopPlay" :disabled="!currentTrack">STOP</button>
            </div>
          </div>

          <section
            v-for="album in albumGroups"
            :key="album.source"
            class="album-section"
          >
            <h2 class="album-title">
              <span class="album-tag">{{ album.source }}</span>
              <span class="album-count">{{ album.tracks.length }} tracks</span>
            </h2>
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
                  :class="{ active: musicStore.currentIndex === track.index }"
                  @click="selectTrack(track.index)"
                >
                  <td class="idx">{{ String(track.index + 1).padStart(2, '0') }}</td>
                  <td>{{ track.name }}</td>
                </tr>
              </tbody>
            </table>
          </section>

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
import { ref, onMounted, computed } from 'vue'
import { useMusicStore } from '../store'
import { usePageMeta } from '../composables/usePageMeta'
import { musicTracks } from '../data/musicTracks'
import { buildTrackList, getMusicBase, groupTracksByAlbum } from '../utils/music'
import InkRevealPanel from '../components/InkRevealPanel.vue'

usePageMeta({ title: '音乐室', description: 'Cyinc 最喜欢的曲目，葬送のフリーレン OST、SANABI 等。' })

const musicStore = useMusicStore()

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

.player-screen {
  font-family: var(--mono);
  font-size: 0.8rem;
  margin-bottom: 1rem;
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

.album-section {
  margin-bottom: 2rem;
}

.album-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.75rem;
  font-family: var(--mono);
  font-size: 0.8rem;
  font-weight: 400;
}

.album-tag {
  color: var(--orange);
  letter-spacing: 0.04em;
}

.album-count {
  color: var(--text-muted);
  font-size: 0.7rem;
}

.music-table tr { cursor: pointer; }
.music-table tr.active td { background: var(--orange-light); }
.music-table tr.active td:first-child { color: var(--orange); }

.now-playing {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 1rem;
}
</style>

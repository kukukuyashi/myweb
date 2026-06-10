<template>
  <div class="music">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content music-room">
          <h1 class="page-title">音乐室</h1>
          <p class="music-sub">收录 Cyinc 最喜欢的曲目</p>

          <div class="player-panel">
            <div class="player-screen">
              <span class="screen-line">{{ playerStatus }}</span>
              <span class="screen-line dim">{{ systemStatus }}</span>
            </div>
            <div class="player-btns">
              <button class="ctrl-btn" @click="togglePlay" :disabled="!currentTrack">
                {{ musicStore.isPlaying ? 'PAUSE' : 'PLAY' }}
              </button>
              <button class="ctrl-btn" @click="stopPlay" :disabled="!currentTrack">STOP</button>
            </div>
          </div>

          <table class="post-table music-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Track</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(track, index) in tracks"
                :key="index"
                :class="{ active: currentTrackIndex === index }"
                @click="selectTrack(index)"
              >
                <td class="idx">{{ String(index + 1).padStart(2, '0') }}</td>
                <td>{{ track.name }}</td>
                <td><span class="tag">{{ track.source }}</span></td>
              </tr>
            </tbody>
          </table>

          <p class="now-playing">
            {{ currentTrack ? '▶ ' + currentTrack.name : 'Select a track →' }}
          </p>
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { ref, onMounted } from 'vue'
import { useMusicStore } from '../store'

const musicStore = useMusicStore()

const tracks = ref([
  { name: 'SANBAI OST - Ending Means Starting Again', source: 'Local', url: '/Music/SANABI/SANBAI OST  Ending Means Starting Again.mp3' },
  { name: 'りりあ。 - あんたなんて。', source: 'Local', url: '/Music/[Hi-Res][241013]TVアニメ『らんま1／2』EDテーマ「あんたなんて。」／りりあ。[48kHz／24bit][FLAC]/01.あんたなんて。.flac' },
  { name: '小林家的龙女仆 - 愛のシュプリーム!', source: 'Local', url: '/Music/小林家的龙女仆/0018865633.flac' },
  { name: '超かぐや姫！ - IROHA\'S Dancing All Night', source: 'Local', url: '/Music/[Hi-Res][260123]映画『超かぐや姫！』オリジナル・サウンドトラック[48kHz／24bit][FLAC]/33.ヤチヨ絵巻.flac' },
  { name: '超かぐや姫！ - ヤチヨ絵巻', source: 'Local', url: '/Music/[Hi-Res][260123]映画『超かぐや姫！』オリジナル・サウンドトラック[48kHz／24bit][FLAC]/33.ヤチヨ絵巻.flac' }
])

const currentTrackIndex = ref(-1)
const currentTrack = ref(null)
const playerStatus = ref('▶ STOPPED')
const systemStatus = ref('SYSTEM READY...')

function selectTrack(index) {
  currentTrackIndex.value = index
  currentTrack.value = tracks.value[index]
  systemStatus.value = 'LOADING TRACK...'
  musicStore.setCurrentSong({ title: currentTrack.value.name, src: currentTrack.value.url })
  musicStore.setPlaying(true)
  playerStatus.value = '▶ PLAYING'
  systemStatus.value = `NOW PLAYING: ${currentTrack.value.name}`
}

function togglePlay() {
  if (musicStore.isPlaying) {
    musicStore.setPlaying(false)
    playerStatus.value = '▶ PAUSED'
    systemStatus.value = 'PLAYBACK PAUSED'
  } else {
    musicStore.setPlaying(true)
    playerStatus.value = '▶ PLAYING'
    systemStatus.value = `NOW PLAYING: ${currentTrack.value.name}`
  }
}

function stopPlay() {
  musicStore.setPlaying(false)
  musicStore.setCurrentSong(null)
  playerStatus.value = '▶ STOPPED'
  systemStatus.value = 'PLAYBACK STOPPED'
}

onMounted(() => {
  if (musicStore.currentSong) {
    const idx = tracks.value.findIndex(t => t.name === musicStore.currentSong.title)
    if (idx !== -1) {
      currentTrackIndex.value = idx
      currentTrack.value = tracks.value[idx]
      playerStatus.value = musicStore.isPlaying ? '▶ PLAYING' : '▶ PAUSED'
      systemStatus.value = `NOW PLAYING: ${currentTrack.value.name}`
    }
  }
})
</script>

<style scoped>
.music-sub {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: -1rem 0 1.5rem;
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

.player-btns { display: flex; gap: 0.5rem; }

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

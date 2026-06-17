<template>
  <div class="music-player" :class="{ collapsed: isCollapsed, 'has-song': musicStore.currentSong }">
    <button
      v-if="musicStore.currentSong"
      type="button"
      class="collapse-btn"
      :title="isCollapsed ? '展开播放器' : '收起播放器'"
      @click="toggleCollapse"
    >
      {{ isCollapsed ? '▲' : '▼' }}
    </button>
    <div v-if="musicStore.currentSong && !isCollapsed" class="player-info">
      <PlayerSpectrum :playing="musicStore.isPlaying" />
      <span class="song-title">{{ musicStore.currentSong.title }}</span>
      <div class="progress-wrap">
        <span class="time">{{ formatTime(sliderTime) }}</span>
        <input
          type="range"
          class="progress-slider"
          min="0"
          :max="sliderMax"
          step="0.01"
          :value="sliderTime"
          :disabled="!sliderMax"
          @input="onSeekInput"
          @pointerdown="onDragStart"
          @pointerup="onSeekEnd"
          @pointercancel="onSeekEnd"
        >
        <span class="time">{{ formatTime(musicStore.duration) }}</span>
      </div>
      <div class="controls">
        <button
          type="button"
          class="nav-btn"
          :disabled="!musicStore.hasPrev()"
          aria-label="上一首"
          @click="musicStore.playPrev()"
        >
          PREV
        </button>
        <button type="button" @click="togglePlay" class="play-btn" :aria-label="musicStore.isPlaying ? '暂停' : '播放'">
          {{ musicStore.isPlaying ? 'PAUSE' : 'PLAY' }}
        </button>
        <button
          type="button"
          class="nav-btn"
          :disabled="!musicStore.hasNext()"
          aria-label="下一首"
          @click="musicStore.playNext()"
        >
          NEXT
        </button>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          class="volume-slider"
          :value="musicStore.volume"
          aria-label="音量"
          @input="onVolumeInput"
        >
      </div>
    </div>
    <p v-if="loadError && musicStore.currentSong && !isCollapsed" class="load-error">{{ loadError }}</p>
    <div v-if="musicStore.currentSong && isCollapsed" class="player-mini" @click="isCollapsed = false">
      <PlayerSpectrum :playing="musicStore.isPlaying" collapsed />
      <span class="mini-title">{{ musicStore.currentSong.title }}</span>
      <span class="mini-state">{{ musicStore.isPlaying ? '▶' : '❚❚' }}</span>
    </div>
  </div>
</template>

<script setup>
import { useMusicStore } from '../store'
import { musicTracks } from '../data/musicTracks'
import { buildTrackList } from '../utils/music'
import PlayerSpectrum from './PlayerSpectrum.vue'
import { ref, computed, onMounted, watch } from 'vue'

const musicStore = useMusicStore()
const loadError = ref('')
const sliderTime = ref(0)
const isDragging = ref(false)
const isCollapsed = ref(localStorage.getItem('playerCollapsed') === 'true')

if (!window.globalAudio) {
  window.globalAudio = new Audio()
}
const audio = window.globalAudio

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('playerCollapsed', isCollapsed.value ? 'true' : 'false')
}

const sliderMax = computed(() => {
  const d = musicStore.duration
  return d && Number.isFinite(d) ? d : 0
})

function onDragStart() {
  isDragging.value = true
}

function onSeekInput(e) {
  isDragging.value = true
  sliderTime.value = Number(e.target.value)
}

function onSeekEnd(e) {
  if (!isDragging.value && !e) return
  isDragging.value = false
  if (!musicStore.currentSong || !sliderMax.value) return
  const t = Number(e?.target?.value ?? sliderTime.value)
  if (!Number.isFinite(t)) return
  sliderTime.value = t
  audio.currentTime = t
  musicStore.setCurrentTime(t)
  musicStore.saveState()
}

function formatTime(sec) {
  if (!sec || !Number.isFinite(sec)) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

function resolveSrc(src) {
  try {
    return new URL(src, window.location.origin).href
  } catch {
    return src
  }
}

function sameSrc(a, b) {
  try {
    return new URL(a).href === new URL(b).href
  } catch {
    return a === b || a.endsWith(b) || b.endsWith(a)
  }
}

function syncFromAudio() {
  if (!audio.src) return
  sliderTime.value = audio.currentTime
  musicStore.setCurrentTime(audio.currentTime)
  if (audio.duration && Number.isFinite(audio.duration)) {
    musicStore.setDuration(audio.duration)
  }
}

function applySeek(time) {
  const d = audio.duration
  const t = d && Number.isFinite(d) ? Math.min(Math.max(0, time), d) : Math.max(0, time)
  audio.currentTime = t
  sliderTime.value = t
  musicStore.setCurrentTime(t)
}

function playWhenReady() {
  if (!audio.src) return
  const run = () => {
    audio.play().catch(err => {
      console.error('播放失败:', err)
      if (err?.name === 'NotAllowedError') {
        loadError.value = '播放被浏览器阻止，请再点一次播放'
      } else if (audio.error) {
        showLoadFailure()
      }
    })
  }
  if (audio.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA) {
    run()
  } else {
    audio.addEventListener('canplay', run, { once: true })
  }
}

function showLoadFailure() {
  loadError.value = import.meta.env.DEV
    ? '音频加载失败，请确认 Music/ 文件夹及文件名正确'
    : '音频加载失败，请稍后再试或刷新页面'
  musicStore.setPlaying(false)
}

function loadSong(src, startTime = 0) {
  loadError.value = ''
  const resolved = resolveSrc(src)

  const onReady = () => {
    applyVolume()
    applySeek(startTime)
    if (musicStore.isPlaying) playWhenReady()
  }

  if (!audio.src || !sameSrc(audio.src, resolved)) {
    audio.pause()
    audio.addEventListener('canplay', onReady, { once: true })
    audio.src = resolved
    audio.load()
  } else {
    onReady()
  }
}

/** 同一首歌已在播放时只同步 UI，避免路由切换后重头加载 */
function resumeExistingPlayback() {
  if (!musicStore.currentSong || !audio.src) return false
  if (!sameSrc(audio.src, resolveSrc(musicStore.currentSong.src))) return false

  applyVolume()
  syncFromAudio()
  if (musicStore.isPlaying && audio.paused) {
    playWhenReady()
  } else if (!musicStore.isPlaying && !audio.paused) {
    audio.pause()
  }
  return true
}

function resetAudio() {
  loadError.value = ''
  isDragging.value = false
  sliderTime.value = 0
  audio.pause()
  audio.removeAttribute('src')
  audio.load()
  musicStore.setCurrentTime(0)
  musicStore.setDuration(0)
}

function onAudioError() {
  showLoadFailure()
}

const togglePlay = () => musicStore.setPlaying(!musicStore.isPlaying)

function applyVolume(vol = musicStore.volume) {
  musicStore.setVolume(vol)
  audio.volume = musicStore.volume
}

function onVolumeInput(e) {
  applyVolume(Number(e.target.value))
}

const updateTime = () => {
  if (isDragging.value) return
  const t = audio.currentTime
  musicStore.setCurrentTime(t)
  sliderTime.value = t
}

const handleEnded = () => {
  if (musicStore.hasNext()) {
    musicStore.playNext()
    return
  }
  musicStore.setPlaying(false)
  musicStore.setCurrentTime(0)
  sliderTime.value = 0
}

const updateDuration = () => {
  if (audio.duration) musicStore.setDuration(audio.duration)
}

if (!window.__musicPlayerListenersBound) {
  window.__musicPlayerListenersBound = true
  audio.addEventListener('timeupdate', updateTime)
  audio.addEventListener('ended', handleEnded)
  audio.addEventListener('loadedmetadata', updateDuration)
  audio.addEventListener('error', onAudioError)
}

watch(() => musicStore.currentTime, (t) => {
  if (!isDragging.value) sliderTime.value = t
})

watch(() => musicStore.isPlaying, (playing) => {
  if (!musicStore.currentSong) return
  if (playing) {
    if (audio.paused) playWhenReady()
  } else {
    audio.pause()
  }
})

watch(
  () => musicStore.currentSong,
  (newSong, oldSong) => {
    if (!newSong) {
      resetAudio()
      return
    }
    const newSrc = resolveSrc(newSong.src)
    const oldSrc = oldSong ? resolveSrc(oldSong.src) : ''
    if (oldSong && sameSrc(newSrc, oldSrc)) return
    loadSong(newSong.src, 0)
  }
)

onMounted(() => {
  if (!musicStore.playlist.length) {
    musicStore.setPlaylist(buildTrackList(musicTracks))
  }

  applyVolume()

  if (resumeExistingPlayback()) return

  if (musicStore.currentSong) {
    loadSong(musicStore.currentSong.src, musicStore.currentTime)
  } else {
    sliderTime.value = musicStore.currentTime
  }
})
</script>

<style scoped>
.music-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--topbar-bg);
  color: #fff;
  padding: 0.6rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-top: 2px solid var(--orange);
  z-index: 1003;
  font-family: var(--mono);
}

.music-player.collapsed {
  padding: 0.35rem 1rem;
}

.collapse-btn {
  position: absolute;
  top: -14px;
  right: 1rem;
  width: 28px;
  height: 28px;
  border: 1px solid var(--orange);
  background: var(--topbar-bg);
  color: #fff;
  font-size: 0.65rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background: var(--orange);
}

.player-mini {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  max-width: var(--content-width);
  cursor: pointer;
  font-size: 0.75rem;
  gap: 0.65rem;
}

.mini-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  opacity: 0.85;
  flex: 1;
  min-width: 0;
}

.mini-state {
  flex-shrink: 0;
  color: var(--orange);
  margin-left: auto;
}

[data-theme="dark"] .music-player {
  background: #0d0d0d;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  max-width: var(--content-width);
  flex-wrap: wrap;
}

.song-title {
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 120px;
  max-width: 220px;
  opacity: 0.85;
}

.progress-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 180px;
}

.time {
  font-size: 0.7rem;
  opacity: 0.7;
  min-width: 2.5rem;
  text-align: center;
}

.progress-slider {
  flex: 1;
  cursor: pointer;
  accent-color: var(--orange);
  min-width: 80px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.play-btn,
.nav-btn {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 0.35rem 1rem;
  font-family: var(--mono);
  font-size: 0.75rem;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.15s;
}

.play-btn:hover,
.nav-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.volume-slider {
  width: 80px;
  cursor: pointer;
  accent-color: var(--orange);
}

.load-error {
  font-size: 0.7rem;
  color: #ff8a80;
  margin: 0.25rem 0 0;
  max-width: var(--content-width);
  width: 100%;
}

@media (max-width: 768px) {
  .music-player {
    padding: 0.5rem 0.875rem calc(0.5rem + var(--safe-bottom));
  }

  .song-title {
    max-width: none;
    flex: 1;
    min-width: 0;
    font-size: 0.7rem;
  }

  .player-info {
    gap: 0.5rem;
  }

  .progress-wrap {
    order: 3;
    width: 100%;
    min-width: 0;
  }

  .controls {
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .play-btn,
  .nav-btn {
    padding: 0.45rem 0.75rem;
    min-height: 36px;
  }

  .volume-slider { display: none; }

  .collapse-btn { right: 0.75rem; }
}

@media (max-width: 480px) {
  .music-player.collapsed {
    padding: 0.35rem 0.75rem calc(0.35rem + var(--safe-bottom));
  }

  .player-mini { gap: 0.5rem; }
}
</style>

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
          @click="onPrev"
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
          @click="onNext"
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
    <div v-if="musicStore.currentSong && isCollapsed" class="player-mini" @click="isCollapsed = false">
      <PlayerSpectrum :playing="musicStore.isPlaying" collapsed />
      <span class="mini-title">{{ musicStore.currentSong.title }}</span>
      <span class="mini-state">{{ musicStore.isPlaying ? '▶' : '❚❚' }}</span>
    </div>
  </div>
</template>

<script setup>
import { useMusicStore } from '../store'
import { getGlobalAudio } from '../utils/musicAudio.js'
import { playCurrentTrack, pausePlayback, playTrackAtIndex } from '../composables/useMusicPlayback.js'
import PlayerSpectrum from './PlayerSpectrum.vue'
import { ref, computed, watch } from 'vue'

const musicStore = useMusicStore()
const sliderTime = ref(0)
const isDragging = ref(false)
const isCollapsed = ref(localStorage.getItem('playerCollapsed') === 'true')

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
  const audio = getGlobalAudio()
  if (!musicStore.currentSong || !sliderMax.value || !audio) return
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

const togglePlay = () => {
  if (musicStore.isPlaying) {
    pausePlayback()
    return
  }
  void playCurrentTrack()
}

const onPrev = () => {
  if (musicStore.currentIndex <= 0) return
  void playTrackAtIndex(musicStore.currentIndex - 1)
}

const onNext = () => {
  if (musicStore.currentIndex < 0 || musicStore.currentIndex >= musicStore.playlist.length - 1) return
  void playTrackAtIndex(musicStore.currentIndex + 1)
}

function onVolumeInput(e) {
  const vol = Number(e.target.value)
  musicStore.setVolume(vol)
  const audio = getGlobalAudio()
  if (audio) audio.volume = musicStore.volume
}

watch(() => musicStore.currentTime, (t) => {
  if (!isDragging.value) sliderTime.value = t
})

watch(() => musicStore.currentSong, (song) => {
  if (!song) sliderTime.value = 0
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

<template>
  <div class="music-player">
    <div v-if="musicStore.currentSong" class="player-info">
      <span class="song-title">{{ musicStore.currentSong.title }}</span>
      <div class="controls">
        <button @click="togglePlay" class="play-btn">
          {{ musicStore.isPlaying ? 'PAUSE' : 'PLAY' }}
        </button>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          v-model="musicStore.volume"
          class="volume-slider"
          @input="updateVolume"
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { useMusicStore } from '../store'
import { ref, onMounted, onUnmounted, watch } from 'vue'

const musicStore = useMusicStore()
const audio = ref(null)

if (!window.globalAudio) {
  window.globalAudio = new Audio()
}
audio.value = window.globalAudio

onMounted(() => {
  audio.value.volume = musicStore.volume

  if (musicStore.currentSong) {
    if (audio.value.src !== musicStore.currentSong.src) {
      audio.value.src = musicStore.currentSong.src
      audio.value.currentTime = musicStore.currentTime
    }
    if (musicStore.isPlaying && audio.value.paused) {
      audio.value.play().catch(err => console.error('播放失败:', err))
    }
  }

  audio.value.addEventListener('timeupdate', updateTime)
  audio.value.addEventListener('ended', handleEnded)
  audio.value.addEventListener('loadedmetadata', updateDuration)

  watch(() => musicStore.isPlaying, (newValue) => {
    if (newValue) {
      audio.value.play().catch(err => console.error('播放失败:', err))
    } else {
      audio.value.pause()
    }
  })

  watch(() => musicStore.currentSong, (newSong) => {
    if (newSong) {
      audio.value.src = newSong.src
      if (musicStore.isPlaying) {
        audio.value.play().catch(err => console.error('播放失败:', err))
      }
    }
  })
})

onUnmounted(() => {
  if (audio.value) {
    audio.value.removeEventListener('timeupdate', updateTime)
    audio.value.removeEventListener('ended', handleEnded)
    audio.value.removeEventListener('loadedmetadata', updateDuration)
  }
  sessionStorage.setItem('musicState', JSON.stringify({
    currentSong: musicStore.currentSong,
    isPlaying: musicStore.isPlaying,
    currentTime: audio.value ? audio.value.currentTime : 0,
    volume: musicStore.volume
  }))
})

const togglePlay = () => musicStore.setPlaying(!musicStore.isPlaying)

const updateVolume = () => {
  if (audio.value) audio.value.volume = musicStore.volume
}

const updateTime = () => {
  if (audio.value) musicStore.setCurrentTime(audio.value.currentTime)
}

const handleEnded = () => {
  musicStore.setPlaying(false)
  musicStore.setCurrentTime(0)
}

const updateDuration = () => {
  if (audio.value) musicStore.setDuration(audio.value.duration)
}
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
  justify-content: center;
  align-items: center;
  border-top: 2px solid var(--orange);
  z-index: 1003;
  font-family: var(--mono);
}

[data-theme="dark"] .music-player {
  background: #0d0d0d;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
  max-width: 1100px;
}

.song-title {
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  opacity: 0.85;
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.play-btn {
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

.play-btn:hover {
  background: var(--orange);
  border-color: var(--orange);
}

.volume-slider {
  width: 100px;
  cursor: pointer;
  accent-color: var(--orange);
}

@media (max-width: 768px) {
  .music-player { padding: 0.5rem 1rem; }
  .song-title { max-width: 120px; font-size: 0.7rem; }
  .volume-slider { width: 70px; }
}
</style>

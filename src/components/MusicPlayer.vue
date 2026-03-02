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

// 创建全局 Audio 对象（如果还没有创建）
if (!window.globalAudio) {
  window.globalAudio = new Audio()
}
audio.value = window.globalAudio

// 初始化Audio对象
onMounted(() => {
  audio.value.volume = musicStore.volume
  
  // 加载之前的播放状态
  if (musicStore.currentSong) {
    // 检查是否需要重新设置src
    if (audio.value.src !== musicStore.currentSong.src) {
      audio.value.src = musicStore.currentSong.src
      audio.value.currentTime = musicStore.currentTime
    }
    if (musicStore.isPlaying && audio.value.paused) {
      audio.value.play().catch(err => console.error('播放失败:', err))
    }
  }
  
  // 监听事件
  audio.value.addEventListener('timeupdate', updateTime)
  audio.value.addEventListener('ended', handleEnded)
  audio.value.addEventListener('loadedmetadata', updateDuration)
  
  // 监听store变化
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
  
  // 保存状态到sessionStorage
  sessionStorage.setItem('musicState', JSON.stringify({
    currentSong: musicStore.currentSong,
    isPlaying: musicStore.isPlaying,
    currentTime: audio.value ? audio.value.currentTime : 0,
    volume: musicStore.volume
  }))
})

const togglePlay = () => {
  musicStore.setPlaying(!musicStore.isPlaying)
}

const updateVolume = () => {
  if (audio.value) {
    audio.value.volume = musicStore.volume
  }
}

const updateTime = () => {
  if (audio.value) {
    musicStore.setCurrentTime(audio.value.currentTime)
  }
}

const handleEnded = () => {
  musicStore.setPlaying(false)
  musicStore.setCurrentTime(0)
}

const updateDuration = () => {
  if (audio.value) {
    musicStore.setDuration(audio.value.duration)
  }
}
</script>

<style scoped>
.music-player {
  position: fixed;
  bottom: 0;
  left: var(--sidebar-width);
  right: 0;
  background: #f6f8fa;
  color: var(--primary-darker);
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  border-top: 2px solid var(--primary-color);
  z-index: 1003;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
}

.player-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
  max-width: 1200px;
  padding: 0 1rem;
}

.song-title {
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  color: var(--primary-darker);
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.play-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.play-btn:hover {
  background: var(--primary-darker);
  transform: translateY(-2px);
}

.play-btn:active {
  transform: translateY(0);
}

.volume-slider {
  width: 120px;
  cursor: pointer;
  accent-color: var(--primary-color);
}

/* 深色模式样式 */
[data-theme="dark"] .music-player {
  background: #1a1a1a;
  border-top-color: #4a90e2;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.3);
}

[data-theme="dark"] .song-title {
  color: #ffffff;
}

[data-theme="dark"] .play-btn {
  background: #4a90e2;
}

[data-theme="dark"] .play-btn:hover {
  background: #3a7bc8;
}

[data-theme="dark"] .volume-slider {
  accent-color: #4a90e2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .music-player {
    padding: 0.75rem 0.5rem;
  }
  
  .song-title {
    font-size: 0.9rem;
    max-width: 120px;
  }
  
  .play-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .volume-slider {
    width: 80px;
  }
  
  .player-info {
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .song-title {
    font-size: 0.8rem;
    max-width: 80px;
  }
  
  .play-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
  
  .volume-slider {
    width: 60px;
  }
}
</style>
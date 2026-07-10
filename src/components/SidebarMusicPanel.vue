<template>
  <div
    class="sidebar-music"
    :class="[
      `sidebar-music--${variant}`,
      { 'sidebar-music--idle': !hasTrack, 'sidebar-music--playing': musicStore.isPlaying },
    ]"
  >
    <div class="sidebar-music__head">
      <span class="sidebar-music__label">{{ hasTrack ? 'NOW PLAYING' : 'MUSIC' }}</span>
      <router-link :to="musicRoomTo" class="sidebar-music__room" @click="$emit('navigate')">
        {{ variant === 'rail' ? '♫' : '音乐室 →' }}
      </router-link>
    </div>

    <p v-if="!hasTrack" class="sidebar-music__idle">
      {{ variant === 'rail' ? '— idle —' : '未在播放 · 去音乐室选曲' }}
    </p>

    <template v-else>
      <p class="sidebar-music__title" :title="musicStore.currentSong.title">
        <span v-if="musicStore.isPlaying" class="sidebar-music__state" aria-hidden="true">▶</span>
        <span v-else class="sidebar-music__state" aria-hidden="true">❚❚</span>
        {{ musicStore.currentSong.title }}
      </p>

      <div v-if="showProgress" class="sidebar-music__progress">
        <span class="sidebar-music__time">{{ formatTime(musicStore.currentTime) }}</span>
        <input
          type="range"
          class="sidebar-music__seek"
          min="0"
          :max="seekMax"
          step="0.1"
          :value="musicStore.currentTime"
          :disabled="!seekMax"
          aria-label="播放进度"
          @input="onSeekInput"
          @change="onSeekEnd"
        >
        <span class="sidebar-music__time">{{ formatTime(musicStore.duration) }}</span>
      </div>

      <div class="sidebar-music__controls">
        <button
          type="button"
          class="sidebar-music__btn"
          :disabled="!musicStore.hasPrev()"
          aria-label="上一首"
          @click="onPrev"
        >
          PREV
        </button>
        <button
          type="button"
          class="sidebar-music__btn sidebar-music__btn--main"
          :aria-label="musicStore.isPlaying ? '暂停' : '播放'"
          @click="onToggle"
        >
          {{ musicStore.isPlaying ? 'PAUSE' : 'PLAY' }}
        </button>
        <button
          type="button"
          class="sidebar-music__btn"
          :disabled="!musicStore.hasNext()"
          aria-label="下一首"
          @click="onNext"
        >
          NEXT
        </button>
      </div>

      <label v-if="showVolume" class="sidebar-music__vol-wrap">
        <span class="sidebar-music__vol-label">VOL</span>
        <input
          type="range"
          class="sidebar-music__vol"
          min="0"
          max="1"
          step="0.01"
          :value="musicStore.volume"
          aria-label="音量"
          @input="onVolumeInput"
        >
      </label>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMusicStore } from '../store'
import { getGlobalAudio } from '../utils/musicAudio.js'
import {
  playCurrentTrack,
  pausePlayback,
  playTrackAtIndex,
} from '../composables/useMusicPlayback.js'

defineProps({
  /** sidebar = 主站侧栏；rail = 宽屏装饰侧栏 */
  variant: { type: String, default: 'sidebar' },
  showProgress: { type: Boolean, default: true },
  showVolume: { type: Boolean, default: true },
})

defineEmits(['navigate'])

const musicStore = useMusicStore()
const route = useRoute()

const hasTrack = computed(() => !!musicStore.currentSong)

const musicRoomTo = computed(() =>
  route.path.startsWith('/app') ? '/app/music' : '/music'
)

const seekMax = computed(() => {
  const d = musicStore.duration
  return d && Number.isFinite(d) ? d : 0
})

function formatTime(sec) {
  if (!sec || !Number.isFinite(sec)) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

function onSeekInput(e) {
  const t = Number(e.target.value)
  if (!Number.isFinite(t)) return
  musicStore.setCurrentTime(t)
}

function onSeekEnd(e) {
  const t = Number(e.target.value)
  const audio = getGlobalAudio()
  if (!Number.isFinite(t) || !audio) return
  audio.currentTime = t
  musicStore.setCurrentTime(t)
  musicStore.saveState()
}

function onVolumeInput(e) {
  const vol = Number(e.target.value)
  musicStore.setVolume(vol)
  const audio = getGlobalAudio()
  if (audio) audio.volume = musicStore.volume
}

function onToggle() {
  if (musicStore.isPlaying) {
    pausePlayback()
    return
  }
  void playCurrentTrack()
}

function onPrev() {
  if (musicStore.currentIndex <= 0) return
  void playTrackAtIndex(musicStore.currentIndex - 1)
}

function onNext() {
  if (musicStore.currentIndex < 0 || musicStore.currentIndex >= musicStore.playlist.length - 1) return
  void playTrackAtIndex(musicStore.currentIndex + 1)
}
</script>

<style scoped>
.sidebar-music {
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg-paper) 92%, var(--orange-light));
  padding: 0.65rem 0.7rem;
  font-family: var(--mono);
}

.sidebar-music--rail {
  padding: 0;
  border: none;
  background: transparent;
}

.sidebar-music__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem;
  margin-bottom: 0.45rem;
}

.sidebar-music--rail .sidebar-music__head {
  margin-bottom: 0.25rem;
}

.sidebar-music__label {
  font-size: 0.52rem;
  letter-spacing: 0.12em;
  color: var(--orange);
}

.sidebar-music__room {
  font-size: 0.62rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.sidebar-music__room:hover {
  color: var(--orange);
}

.sidebar-music__idle {
  margin: 0;
  font-size: 0.68rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.sidebar-music--rail .sidebar-music__idle {
  font-size: 0.55rem;
}

.sidebar-music__title {
  margin: 0 0 0.5rem;
  font-size: 0.72rem;
  line-height: 1.4;
  color: var(--text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.sidebar-music--rail .sidebar-music__title {
  font-size: 0.55rem;
  -webkit-line-clamp: 3;
  margin-bottom: 0.35rem;
}

.sidebar-music__state {
  color: var(--orange);
  margin-right: 0.2rem;
}

.sidebar-music--playing .sidebar-music__title {
  color: var(--steel);
}

.sidebar-music__progress {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
}

.sidebar-music__time {
  font-size: 0.58rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  min-width: 2rem;
}

.sidebar-music__seek,
.sidebar-music__vol {
  width: 100%;
  accent-color: var(--orange);
  cursor: pointer;
}

.sidebar-music__controls {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.25rem;
  margin-bottom: 0.45rem;
}

.sidebar-music--rail .sidebar-music__controls {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.15rem;
  margin-bottom: 0.25rem;
}

.sidebar-music__btn {
  font-family: inherit;
  font-size: 0.58rem;
  letter-spacing: 0.04em;
  padding: 0.35rem 0.15rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.sidebar-music--rail .sidebar-music__btn {
  font-size: 0.48rem;
  padding: 0.28rem 0.1rem;
}

.sidebar-music__btn:hover:not(:disabled) {
  border-color: var(--orange);
  color: var(--orange);
}

.sidebar-music__btn--main {
  color: var(--text);
  font-weight: 500;
}

.sidebar-music__btn--main:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.sidebar-music__btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.sidebar-music__vol-wrap {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 0.4rem;
}

.sidebar-music__vol-label {
  font-size: 0.52rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

[data-theme="dark"] .sidebar-music {
  background: color-mix(in srgb, var(--bg-paper) 88%, #1a1208);
}
</style>

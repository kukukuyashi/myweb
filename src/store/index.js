import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

function clampVolume(value) {
  const n = Number(value)
  if (!Number.isFinite(n)) return 0.5
  return Math.min(1, Math.max(0, n))
}

function readStoredVolume(fallback = 0.5) {
  const fromSession = sessionStorage.getItem('musicState')
  if (fromSession) {
    try {
      const v = JSON.parse(fromSession).volume
      if (v !== undefined && v !== null) return clampVolume(v)
    } catch { /* ignore */ }
  }
  const fromLocal = localStorage.getItem('volume')
  if (fromLocal !== null && fromLocal !== '') return clampVolume(fromLocal)
  return fallback
}

let saveTimer = null

export const useMusicStore = defineStore('music', () => {
  const savedState = sessionStorage.getItem('musicState')
  const parsedState = savedState ? JSON.parse(savedState) : null

  const currentSong = ref(parsedState?.currentSong ?? null)
  const isPlaying = ref(parsedState?.isPlaying ?? false)
  const volume = ref(
    parsedState?.volume != null ? clampVolume(parsedState.volume) : readStoredVolume()
  )
  const currentTime = ref(parsedState?.currentTime ?? 0)
  const duration = ref(0)
  const playlist = ref([])
  const currentIndex = ref(-1)

  function saveState() {
    clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      sessionStorage.setItem('musicState', JSON.stringify({
        currentSong: currentSong.value,
        isPlaying: isPlaying.value,
        volume: volume.value,
        currentTime: currentTime.value
      }))
    }, 5000)
  }

  function setCurrentSong(song) {
    const changed = !currentSong.value
      || !song
      || currentSong.value.src !== song.src
      || currentSong.value.title !== song.title
    currentSong.value = song
    if (changed) {
      currentTime.value = 0
      duration.value = 0
    }
    if (song && playlist.value.length) {
      const idx = playlist.value.findIndex(t => t.src === song.src)
      if (idx !== -1) currentIndex.value = idx
    }
    saveState()
  }

  function setPlaylist(tracks) {
    playlist.value = tracks.map(t => ({ title: t.name, src: t.url }))
    if (currentSong.value) {
      const idx = playlist.value.findIndex(t => t.src === currentSong.value.src)
      currentIndex.value = idx
    }
  }

  function playAtIndex(index) {
    if (index < 0 || index >= playlist.value.length) return false
    currentIndex.value = index
    setCurrentSong(playlist.value[index])
    setPlaying(true)
    return true
  }

  function playNext() {
    return playAtIndex(currentIndex.value + 1)
  }

  function playPrev() {
    return playAtIndex(currentIndex.value - 1)
  }

  function hasNext() {
    return currentIndex.value >= 0 && currentIndex.value < playlist.value.length - 1
  }

  function hasPrev() {
    return currentIndex.value > 0
  }

  function setPlaying(playing) {
    isPlaying.value = playing
    saveState()
  }

  function setVolume(vol) {
    const v = clampVolume(vol)
    volume.value = v
    localStorage.setItem('volume', String(v))
    saveState()
  }

  function setCurrentTime(time) {
    currentTime.value = time
  }

  function setDuration(dur) {
    duration.value = dur
  }

  function resetPlayback() {
    currentSong.value = null
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
    currentIndex.value = -1
    saveState()
  }

  return {
    currentSong,
    isPlaying,
    volume,
    currentTime,
    duration,
    playlist,
    currentIndex,
    setCurrentSong,
    setPlaylist,
    playAtIndex,
    playNext,
    playPrev,
    hasNext,
    hasPrev,
    setPlaying,
    setVolume,
    setCurrentTime,
    setDuration,
    resetPlayback,
    saveState
  }
})

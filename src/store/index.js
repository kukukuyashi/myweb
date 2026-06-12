import { defineStore } from 'pinia'

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

export const useMusicStore = defineStore('music', {
  state: () => {
    // 从sessionStorage加载之前的状态
    const savedState = sessionStorage.getItem('musicState')
    if (savedState) {
      const parsedState = JSON.parse(savedState)
      return {
        currentSong: parsedState.currentSong,
        isPlaying: parsedState.isPlaying,
        volume: parsedState.volume != null
          ? clampVolume(parsedState.volume)
          : readStoredVolume(),
        currentTime: parsedState.currentTime || 0,
        duration: 0,
        playlist: [],
        currentIndex: -1,
      }
    }
    return {
      currentSong: null,
      isPlaying: false,
      volume: readStoredVolume(),
      currentTime: 0,
      duration: 0,
      playlist: [],
      currentIndex: -1,
    }
  },
  actions: {
    setCurrentSong(song) {
      const changed = !this.currentSong
        || !song
        || this.currentSong.src !== song.src
        || this.currentSong.title !== song.title
      this.currentSong = song
      if (changed) {
        this.currentTime = 0
        this.duration = 0
      }
      if (song && this.playlist.length) {
        const idx = this.playlist.findIndex(t => t.src === song.src)
        if (idx !== -1) this.currentIndex = idx
      }
      this.saveState()
    },
    setPlaylist(tracks) {
      this.playlist = tracks.map(t => ({ title: t.name, src: t.url }))
      if (this.currentSong) {
        const idx = this.playlist.findIndex(t => t.src === this.currentSong.src)
        this.currentIndex = idx
      }
    },
    playAtIndex(index) {
      if (index < 0 || index >= this.playlist.length) return false
      this.currentIndex = index
      this.setCurrentSong(this.playlist[index])
      this.setPlaying(true)
      return true
    },
    playNext() {
      return this.playAtIndex(this.currentIndex + 1)
    },
    playPrev() {
      return this.playAtIndex(this.currentIndex - 1)
    },
    hasNext() {
      return this.currentIndex >= 0 && this.currentIndex < this.playlist.length - 1
    },
    hasPrev() {
      return this.currentIndex > 0
    },
    setPlaying(playing) {
      this.isPlaying = playing
      // 保存状态到sessionStorage
      this.saveState()
    },
    setVolume(volume) {
      const v = clampVolume(volume)
      this.volume = v
      localStorage.setItem('volume', String(v))
      this.saveState()
    },
    setCurrentTime(time) {
      this.currentTime = time
    },
    setDuration(duration) {
      this.duration = duration
    },
    resetPlayback() {
      this.currentSong = null
      this.isPlaying = false
      this.currentTime = 0
      this.duration = 0
      this.currentIndex = -1
      this.saveState()
    },
    saveState() {
      sessionStorage.setItem('musicState', JSON.stringify({
        currentSong: this.currentSong,
        isPlaying: this.isPlaying,
        volume: this.volume,
        currentTime: this.currentTime
      }))
    }
  }
})
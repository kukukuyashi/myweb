import { defineStore } from 'pinia'

export const useMusicStore = defineStore('music', {
  state: () => {
    // 从sessionStorage加载之前的状态
    const savedState = sessionStorage.getItem('musicState')
    if (savedState) {
      const parsedState = JSON.parse(savedState)
      return {
        currentSong: parsedState.currentSong,
        isPlaying: parsedState.isPlaying,
        volume: Number(parsedState.volume ?? localStorage.getItem('volume') ?? 0.5),
        currentTime: parsedState.currentTime || 0,
        duration: 0
      }
    }
    return {
      currentSong: null,
      isPlaying: false,
      volume: Number(localStorage.getItem('volume') ?? 0.5),
      currentTime: 0,
      duration: 0
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
      this.saveState()
    },
    setPlaying(playing) {
      this.isPlaying = playing
      // 保存状态到sessionStorage
      this.saveState()
    },
    setVolume(volume) {
      this.volume = volume
      localStorage.setItem('volume', volume)
      // 保存状态到sessionStorage
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
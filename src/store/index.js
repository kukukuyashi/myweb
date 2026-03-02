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
        volume: parsedState.volume || localStorage.getItem('volume') || 0.5,
        currentTime: parsedState.currentTime || 0,
        duration: 0
      }
    }
    return {
      currentSong: null,
      isPlaying: false,
      volume: localStorage.getItem('volume') || 0.5,
      currentTime: 0,
      duration: 0
    }
  },
  actions: {
    setCurrentSong(song) {
      this.currentSong = song
      // 保存状态到sessionStorage
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
      // 保存状态到sessionStorage
      this.saveState()
    },
    setDuration(duration) {
      this.duration = duration
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
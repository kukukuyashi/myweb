import { watch } from 'vue'
import { useMusicStore } from '../store'
import { musicTracks } from '../data/musicTracks'
import { buildTrackList } from '../utils/music'
import { getGlobalAudio } from '../utils/musicAudio.js'

let engineStarted = false
let engineInitialized = false
const R2_HOST = 'pub-17cd91d3e6a44ab4b50085daaf02beda.r2.dev' 

function resolveSrc(src) {
  try {
    return new URL(src, window.location.origin).href
  } catch {
    return src
  }
}

function sameSrc(a, b) {
  if (!a || !b) return false
  try {
    return new URL(a).href === new URL(b).href
  } catch {
    return a === b || a.endsWith(b) || b.endsWith(a)
  }
}

function waitCanPlay(audio) {
  if (audio.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA) {
    return Promise.resolve()
  }
  return new Promise((resolve, reject) => {
    const onReady = () => {
      cleanup()
      resolve()
    }
    const onError = () => {
      cleanup()
      reject(audio.error || new Error('audio load failed'))
    }
    const cleanup = () => {
      audio.removeEventListener('canplay', onReady)
      audio.removeEventListener('error', onError)
    }
    audio.addEventListener('canplay', onReady, { once: true })
    audio.addEventListener('error', onError, { once: true })
  })
}

/** 在用户点击时直接播放，保证浏览器手势策略 */
export async function playCurrentTrack() {
  const musicStore = useMusicStore()
  const audio = getGlobalAudio()
  const song = musicStore.currentSong
  if (!audio || !song) {
    console.warn('[music] 无 audio 元素或未选曲')
    return false
  }

  const resolved = resolveSrc(song.src)
  let playRetried = false
  musicStore.setPlaying(true)

  try {
    if (!audio.src || !sameSrc(audio.src, resolved)) {
      audio.pause()
      audio.src = resolved
      audio.load()
    }

    const vol = musicStore.volume
    audio.volume = Math.max(0, Math.min(1, Number.isFinite(vol) ? vol : 0.8))
    await waitCanPlay(audio)
    await audio.play()
    if (audio.duration && Number.isFinite(audio.duration)) {
      musicStore.setDuration(audio.duration)
    }
    return true
  } catch (err) {
    // R2 不稳定时降级到本地(同源,走 nginx)
    if (resolved.includes(R2_HOST) && !playRetried) {
      playRetried = true
      const localUrl = resolved.replace('https://' + R2_HOST, window.location.origin + '/myweb')
      console.warn('[music] R2 失败,降级到本地', localUrl)
      try {
        audio.pause()
        audio.src = localUrl
        audio.load()
        await waitCanPlay(audio)
        audio.volume = Math.max(0, Math.min(1, Number.isFinite(musicStore.volume) ? musicStore.volume : 0.8))
        await audio.play()
        if (audio.duration && Number.isFinite(audio.duration)) musicStore.setDuration(audio.duration)
        return true
      } catch (err2) {
        console.error('[music] 本地也失败', err2, { src: localUrl, readyState: audio.readyState })
      }
    }
    console.error('[music] 播放失败', err, { src: resolved, readyState: audio.readyState })
    musicStore.setPlaying(false)
    return false
  }
}

export async function playTrackAtIndex(index) {
  const musicStore = useMusicStore()
  if (index < 0 || index >= musicStore.playlist.length) return false
  musicStore.playAtIndex(index)
  return playCurrentTrack()
}

export function pausePlayback() {
  const audio = getGlobalAudio()
  const musicStore = useMusicStore()
  musicStore.setPlaying(false)
  audio?.pause()
}

function resetAudio() {
  const audio = getGlobalAudio()
  const musicStore = useMusicStore()
  audio?.pause()
  if (audio) {
    audio.removeAttribute('src')
    audio.load()
  }
  musicStore.setCurrentTime(0)
  musicStore.setDuration(0)
}

function loadSong(src, startTime = 0) {
  const musicStore = useMusicStore()
  const audio = getGlobalAudio()
  if (!audio) return

  const resolved = resolveSrc(src)
  const apply = () => {
    audio.currentTime = startTime
    musicStore.setCurrentTime(startTime)
    if (audio.duration && Number.isFinite(audio.duration)) {
      musicStore.setDuration(audio.duration)
    }
  }

  if (!audio.src || !sameSrc(audio.src, resolved)) {
    audio.pause()
    audio.src = resolved
    audio.load()
    void waitCanPlay(audio).then(apply).catch((err) => {
      console.error('[music] 加载失败', err, resolved)
      musicStore.setPlaying(false)
    })
  } else {
    apply()
  }
}

function bindListeners(audio) {
  const musicStore = useMusicStore()
  if (!audio || window.__musicPlayerListenersBound) return
  window.__musicPlayerListenersBound = true

  audio.addEventListener('timeupdate', () => {
    musicStore.setCurrentTime(audio.currentTime)
  })

  audio.addEventListener('ended', () => {
    if (musicStore.hasNext()) {
      void playTrackAtIndex(musicStore.currentIndex + 1)
      return
    }
    musicStore.setPlaying(false)
    musicStore.setCurrentTime(0)
  })

  audio.addEventListener('loadedmetadata', () => {
    if (audio.duration) musicStore.setDuration(audio.duration)
  })

  audio.addEventListener('error', () => {
    console.error('[music] audio error', audio.error, audio.src)
    musicStore.setPlaying(false)
  })
}

export function useMusicPlayback() {
  if (engineStarted) return
  engineStarted = true

  const musicStore = useMusicStore()

  watch(() => musicStore.isPlaying, (playing) => {
    const audio = getGlobalAudio()
    if (!playing && audio) audio.pause()
  })

  watch(
    () => musicStore.currentSong,
    (newSong) => {
      if (!newSong) resetAudio()
    }
  )
}

export function initMusicEngine() {
  if (engineInitialized) return
  engineInitialized = true

  const musicStore = useMusicStore()
  const audio = getGlobalAudio()
  bindListeners(audio)

  if (!musicStore.playlist.length) {
    musicStore.setPlaylist(buildTrackList(musicTracks))
  }

  if (audio) {
    const vol = musicStore.volume
    audio.volume = Math.max(0, Math.min(1, Number.isFinite(vol) ? vol : 0.8))
  }

  if (musicStore.currentSong) {
    loadSong(musicStore.currentSong.src, musicStore.currentTime)
    if (musicStore.isPlaying) musicStore.setPlaying(false)
  }
}

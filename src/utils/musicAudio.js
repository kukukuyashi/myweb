/**
 * 全局 <audio> — 使用 App.vue 内嵌元素，避免 detached Audio 在部分浏览器下无声。
 */

export function bindGlobalAudio(el) {
  if (!el) return null
  window.globalAudio = el
  el.preload = 'auto'
  return el
}

export function getGlobalAudio() {
  return window.globalAudio || null
}

/** 保留接口；不再用 Web Audio 接管播放（会导致无声），频谱用动画占位 */
export function primeMusicPlayback() {
  return Promise.resolve(null)
}

export function ensureMusicAnalyser() {
  return Promise.resolve(null)
}

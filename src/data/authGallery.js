/**
 * 登录 / 注册页视觉 — 同一套样式；F5 每次随机一张线稿
 */
import { aboutGallery } from './aboutGallery.js'

/** 构图较稳的候选（登录/注册同一套池） */
const AUTH_VISUAL_POOL = [0, 12, 24, 80, 150, 165, 169, 170, 180, 175]

function aboutImg(index, fallbackIndex = 0) {
  return aboutGallery[index]?.path || aboutGallery[fallbackIndex]?.path || 'img/xiaoqing.png'
}

function pickIndex() {
  return AUTH_VISUAL_POOL[Math.floor(Math.random() * AUTH_VISUAL_POOL.length)]
}

/**
 * 每次调用（含 F5）随机一张；登录/注册样式相同（同池、同图用于侧栏与墨染底）。
 * @returns {{ panel: string, backdrop: string }}
 */
export function getAuthVisuals() {
  const img = aboutImg(pickIndex())
  return { panel: img, backdrop: img }
}

/** @deprecated 兼容旧引用；请用 getAuthVisuals() */
export const authPageBackdrop = aboutImg(24)
export const authLoginPanel = aboutImg(0)
export const authRegisterPanel = aboutImg(0)

export const authDefaultStats = [
  { value: '论坛', label: '板块讨论' },
  { value: 'FLAC', label: '音乐室' },
  { value: '24/7', label: '全天在线' },
]

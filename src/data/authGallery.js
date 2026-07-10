/**
 * 登录 / 注册页视觉 — img/关于/ 贴纸墙 + 墨染背景
 */
import { aboutGallery } from './aboutGallery.js'

function aboutImg(index, fallbackIndex = 0) {
  return aboutGallery[index]?.path || aboutGallery[fallbackIndex]?.path || 'img/xiaoqing.png'
}

/** 全页模糊背景 */
export const authPageBackdrop = aboutImg(24)

/** 登录卡左侧封面 */
export const authLoginPanel = aboutImg(0)

/** 注册卡左侧封面 */
export const authRegisterPanel = aboutImg(12)

export const authDefaultStats = [
  { value: '论坛', label: '板块讨论' },
  { value: 'FLAC', label: '音乐室' },
  { value: '24/7', label: '全天在线' },
]

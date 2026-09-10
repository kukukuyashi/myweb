/**
 * 展示用缩略图工具：命中 manifest 就返回 `.thumb.webp` 版本，否则回落原路径。
 *
 * - 原图（`img/关于/xx.jpg`）继续可用于灯箱/大图；
 * - 列表/贴纸墙/轮播用 `thumbUrl(...)` 拿到 ~720px 的 webp；
 * - 后台上传的图（`/uploads/...`）没有缩略图，按 API 域名解析原图；
 * - 删除任何 .thumb.webp 或 manifest 后自动降级为原图；
 * - 缩略图 404 时用 `onThumbError` 切回原图，防止部署漂移破图。
 */
import { imgUrl } from '../data/profile.js'
import { resolveMediaUrl } from '../api/platform.js'
import manifest from '../data/thumbManifest.json'

const set = new Set(manifest)
const SUFFIX = '.thumb.webp'

function isAbsoluteLike(s) {
  return (
    s.startsWith('http://') ||
    s.startsWith('https://') ||
    s.startsWith('data:') ||
    s.startsWith('blob:')
  )
}

/** 站内静态资源（img/…）：走缩略图清单 + BASE_URL；其余（/uploads/… 等）走 API 域名 */
function isSiteAsset(s) {
  return s.startsWith('img/') || s.startsWith('/img/')
}

function toThumbRel(rel) {
  const clean = String(rel || '').replace(/^\//, '').replace(/\\/g, '/')
  if (!clean) return ''
  const dot = clean.lastIndexOf('.')
  const base = dot >= 0 ? clean.slice(0, dot) : clean
  return `${base}${SUFFIX}`
}

export function hasThumb(relativePath) {
  const clean = String(relativePath || '').replace(/^\//, '').replace(/\\/g, '/')
  return set.has(clean)
}

/**
 * 若 manifest 存在原图 → 返回缩略图 URL；否则回落原图 URL。
 */
export function thumbUrl(relativePath) {
  if (!relativePath) return ''
  const s = String(relativePath).trim()
  if (!s) return ''
  if (isAbsoluteLike(s)) return s
  if (isSiteAsset(s)) {
    return hasThumb(s) ? imgUrl(toThumbRel(s)) : imgUrl(s)
  }
  return resolveMediaUrl(s)
}

/**
 * `<img @error="onThumbError($event, originalRel)">`
 * 缩略图加载失败时切回原图；用 dataset 防止死循环。
 */
export function onThumbError(event, originalRel) {
  const el = event?.target
  if (!el || !originalRel) return
  if (el.dataset.thumbFallback === '1') return
  el.dataset.thumbFallback = '1'
  const s = String(originalRel).trim()
  if (isAbsoluteLike(s)) {
    el.src = s
    return
  }
  el.src = isSiteAsset(s) ? imgUrl(s) : resolveMediaUrl(s)
}

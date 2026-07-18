/**
 * 展示用缩略图工具：命中 manifest 就返回 `.thumb.webp` 版本，否则回落原路径。
 *
 * - 原图（`img/关于/xx.jpg`）继续可用于灯箱/大图；
 * - 列表/贴纸墙/轮播用 `thumbUrl(...)` 拿到 ~720px 的 webp；
 * - 删除任何 .thumb.webp 或 manifest 后自动降级为原图。
 */
import { imgUrl } from '../data/profile.js'
import manifest from '../data/thumbManifest.json'

const set = new Set(manifest)
const SUFFIX = '.thumb.webp'

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
  if (hasThumb(relativePath)) return imgUrl(toThumbRel(relativePath))
  return imgUrl(relativePath)
}

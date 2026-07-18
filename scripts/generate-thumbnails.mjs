/**
 * 批量生成展示用缩略图（.webp，≤ 720px）。
 *
 * - 只处理"前端实际引用"的图片：`img/关于/` 全量 + platformBaGallery.js / pomoAcg.js 里的 path。
 * - 输出路径：把原文件名换成 `<basename>.thumb.webp`，与原图放同一目录。
 * - 幂等：若缩略图存在且原图 mtime 更旧，跳过。
 * - 生成清单 `src/data/thumbManifest.json`（相对路径数组，前端据此判断能不能用缩略图）。
 * - 原图不动，任何时候删掉 .thumb.webp 就自动回落原图。
 *
 * 运行：node scripts/generate-thumbnails.mjs
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import sharp from 'sharp'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const IMG_ROOT = path.join(ROOT, 'img')
const MANIFEST_OUT = path.join(ROOT, 'src/data/thumbManifest.json')

const THUMB_MAX = 720
const QUALITY = 80
const SUFFIX = '.thumb.webp'
const IMAGE_RE = /\.(jpe?g|jfif|png|webp)$/i
const THUMB_RE = /\.thumb\.webp$/i

/** 从数据文件里正则抠 path/img 字段，只把 img/... 的路径纳入压图集合 */
function extractPathsFromFile(filePath) {
  if (!fs.existsSync(filePath)) return []
  const txt = fs.readFileSync(filePath, 'utf8')
  const re = /['"](img\/[^'"]+?\.(jpe?g|jfif|png|webp))['"]/gi
  const set = new Set()
  let m
  while ((m = re.exec(txt))) set.add(m[1].replace(/\\/g, '/'))
  return [...set]
}

function walkDir(dir) {
  if (!fs.existsSync(dir)) return []
  const out = []
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name)
    const stat = fs.statSync(full)
    if (stat.isDirectory()) out.push(...walkDir(full))
    else if (IMAGE_RE.test(name) && !THUMB_RE.test(name)) out.push(full)
  }
  return out
}

function relPosix(absPath) {
  return path.relative(ROOT, absPath).replace(/\\/g, '/')
}

function thumbAbs(originalAbs) {
  const dir = path.dirname(originalAbs)
  const base = path.basename(originalAbs, path.extname(originalAbs))
  return path.join(dir, `${base}${SUFFIX}`)
}

async function processOne(originalAbs) {
  const outAbs = thumbAbs(originalAbs)
  const relIn = relPosix(originalAbs)

  try {
    const inStat = fs.statSync(originalAbs)
    if (fs.existsSync(outAbs)) {
      const outStat = fs.statSync(outAbs)
      if (outStat.mtimeMs >= inStat.mtimeMs) {
        return { rel: relPosix(outAbs), skipped: true }
      }
    }
    const img = sharp(originalAbs, { failOn: 'none' })
    const meta = await img.metadata()
    const needResize = (meta.width || 0) > THUMB_MAX || (meta.height || 0) > THUMB_MAX
    let pipeline = img
    if (needResize) {
      pipeline = pipeline.resize({ width: THUMB_MAX, height: THUMB_MAX, fit: 'inside' })
    }
    await pipeline.webp({ quality: QUALITY, effort: 4 }).toFile(outAbs)
    const savedIn = inStat.size
    const savedOut = fs.statSync(outAbs).size
    return {
      rel: relPosix(outAbs),
      inKB: (savedIn / 1024).toFixed(0),
      outKB: (savedOut / 1024).toFixed(0),
    }
  } catch (err) {
    console.warn(`[skip] ${relIn}: ${err.message}`)
    return null
  }
}

async function main() {
  const referenced = new Set()

  // 1. img/关于 全量（贴纸墙 + 封面）
  walkDir(path.join(IMG_ROOT, '关于')).forEach((p) => referenced.add(p))

  // 2. 前端数据文件里被引用的 BA / pomo 等图
  const dataFiles = [
    'src/data/platformBaGallery.js',
    'src/data/pomoAcg.js',
    'src/data/authGallery.js',
    'src/data/seasonTheme.js',
    'src/data/profile.js',
    'src/data/posts.js',
  ]
  for (const rel of dataFiles) {
    for (const p of extractPathsFromFile(path.join(ROOT, rel))) {
      const abs = path.join(ROOT, p)
      if (fs.existsSync(abs)) referenced.add(abs)
    }
  }

  const list = [...referenced].sort()
  console.log(`==> ${list.length} referenced images to thumbnail`)

  const manifest = []
  let done = 0
  let skipped = 0
  let totalIn = 0
  let totalOut = 0

  for (const abs of list) {
    const r = await processOne(abs)
    if (!r) continue
    if (r.skipped) {
      skipped += 1
    } else {
      done += 1
      totalIn += Number(r.inKB) || 0
      totalOut += Number(r.outKB) || 0
    }
    // manifest 保存"原图相对路径 -> 缩略图相对路径"里的原图侧 key
    const originalRel = relPosix(abs)
    manifest.push(originalRel)
  }

  // 去重 + 排序
  const dedup = [...new Set(manifest)].sort()
  fs.mkdirSync(path.dirname(MANIFEST_OUT), { recursive: true })
  fs.writeFileSync(MANIFEST_OUT, JSON.stringify(dedup, null, 2), 'utf8')

  console.log(`==> generated ${done}, skipped ${skipped}`)
  if (done) {
    console.log(`==> size: ${(totalIn / 1024).toFixed(1)} MB → ${(totalOut / 1024).toFixed(1)} MB`)
  }
  console.log(`==> manifest → ${relPosix(MANIFEST_OUT)} (${dedup.length} entries)`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})

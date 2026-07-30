/**
 * 批量把 Music/ 下的无损/大文件音频转码为 160k AAC (.m4a)，就地生成在原文件旁。
 * 保留原始 FLAC/MP3 作为母带；部署时 pack-media 只打包 .m4a + 封面。
 * 用法: npm run music:transcode
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { spawnSync } from 'child_process'
import ffmpegPath from 'ffmpeg-static'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const musicRoot = path.join(__dirname, '../Music')
const SRC_RE = /\.(flac|wav|mp3)$/i
const BITRATE = process.env.MUSIC_BITRATE || '160k'

if (!fs.existsSync(musicRoot)) {
  console.log('Music/ 不存在，跳过转码')
  process.exit(0)
}
if (!ffmpegPath) {
  console.error('未找到 ffmpeg-static，请先 npm i -D ffmpeg-static')
  process.exit(1)
}

function walk(dir) {
  const out = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) out.push(...walk(full))
    else if (SRC_RE.test(entry.name)) out.push(full)
  }
  return out
}

const files = walk(musicRoot)
let done = 0
let skipped = 0
let failed = 0
let srcBytes = 0
let outBytes = 0

for (const src of files) {
  const out = src.replace(SRC_RE, '.m4a')
  const srcStat = fs.statSync(src)
  if (fs.existsSync(out) && fs.statSync(out).mtimeMs >= srcStat.mtimeMs) {
    skipped++
    outBytes += fs.statSync(out).size
    srcBytes += srcStat.size
    continue
  }
  const r = spawnSync(ffmpegPath, [
    '-hide_banner', '-loglevel', 'error', '-y',
    '-i', src,
    '-map', 'a:0',
    '-c:a', 'aac', '-b:a', BITRATE,
    '-movflags', '+faststart',
    out,
  ], { stdio: 'inherit' })
  if (r.status === 0 && fs.existsSync(out)) {
    done++
    srcBytes += srcStat.size
    outBytes += fs.statSync(out).size
    console.log(`OK  ${path.relative(musicRoot, out)}`)
  } else {
    failed++
    console.error(`FAIL ${path.relative(musicRoot, src)}`)
  }
}

const mb = (b) => (b / 1024 / 1024).toFixed(1)
console.log(`\n转码完成: 新增 ${done}，跳过 ${skipped}，失败 ${failed}`)
console.log(`体积: 源 ${mb(srcBytes)}MB → m4a ${mb(outBytes)}MB (${(srcBytes / (outBytes || 1)).toFixed(1)}x)`)
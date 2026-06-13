import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const musicRoot = path.join(__dirname, '../Music')
const outFile = path.join(__dirname, '../src/data/musicTracks.js')

if (!fs.existsSync(musicRoot)) {
  console.log(`Music/ 不存在，保留现有曲目表 → ${outFile}`)
  process.exit(0)
}

const AUDIO_RE = /\.(flac|mp3)$/i
const COVER_NAMES = ['folder.jpg', 'COVER.jpg', 'cover.jpg', 'Folder.jpg']

function findCoverPath(dirFull, dirRel) {
  for (const name of COVER_NAMES) {
    const full = path.join(dirFull, name)
    if (fs.existsSync(full) && fs.statSync(full).isFile()) {
      const relPath = dirRel === '.' ? name : `${dirRel}/${name}`
      return `/Music/${relPath.replace(/\\/g, '/')}`
    }
  }
  return ''
}

/** 专辑文件夹排序：葬送のフリーレン优先，其余按路径 */
const ALBUM_PRIORITY = [
  /葬送のフリーレン|Frieren/i,
  /SANABI/i,
  /小林家的龙女仆/,
]

function sourceLabel(dirName) {
  if (/葬送のフリーレン|Frieren/i.test(dirName)) return '葬送のフリーレン'
  if (/SANABI/i.test(dirName)) return 'SANABI'
  if (/小林家的龙女仆/.test(dirName)) return '小林家的龙女仆'
  if (/らんま1|らんま1／2/.test(dirName)) return 'らんま1/2'
  if (/超かぐや姫/.test(dirName)) return '超かぐや姫！'
  return dirName.length > 24 ? `${dirName.slice(0, 22)}…` : dirName
}

function trackName(filename, dirName) {
  const base = filename.replace(AUDIO_RE, '')
  const stripped = base.replace(/^\d+\.\s*/, '')
  if (/葬送のフリーレン|Frieren/i.test(dirName)) {
    return stripped.replace(/^Evan Call - /, '')
  }
  if (/SANABI/i.test(dirName)) return stripped
  if (/小林家的龙女仆/.test(dirName)) return '愛のシュプリーム!'
  if (/らんま1/.test(dirName)) return 'あんたなんて。'
  if (/超かぐや姫/.test(dirName)) return 'ヤチヨ絵巻'
  return stripped || base
}

function trackSortKey(filename) {
  const m = filename.match(/^(\d+)\./)
  return m ? Number(m[1]) : 999
}

function walkAudio(dir, rel = '') {
  const items = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const relPath = rel ? `${rel}/${entry.name}` : entry.name
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      items.push(...walkAudio(full, relPath))
    } else if (AUDIO_RE.test(entry.name)) {
      const dirRel = rel || '.'
      const dirFull = path.dirname(full)
      items.push({
        name: trackName(entry.name, dirRel),
        source: sourceLabel(dirRel),
        path: `/Music/${relPath.replace(/\\/g, '/')}`,
        cover: findCoverPath(dirFull, dirRel),
        _dir: dirRel,
        _sort: trackSortKey(entry.name),
      })
    }
  }
  return items
}

function albumPriority(dir) {
  const idx = ALBUM_PRIORITY.findIndex(re => re.test(dir))
  return idx === -1 ? ALBUM_PRIORITY.length : idx
}

const tracks = walkAudio(musicRoot).sort((a, b) => {
  const pa = albumPriority(a._dir)
  const pb = albumPriority(b._dir)
  if (pa !== pb) return pa - pb
  if (a._dir !== b._dir) return a._dir.localeCompare(b._dir, 'en')
  return a._sort - b._sort
})

const lines = tracks.map(({ name, source, path: p, cover }) => {
  const esc = (s) => s.replace(/\\/g, '\\\\').replace(/'/g, "\\'")
  const coverPart = cover ? `, cover: '${esc(cover)}'` : ''
  return `  { name: '${esc(name)}', source: '${esc(source)}', path: '${esc(p)}'${coverPart} },`
})

const content = `/**
 * 自动生成 — 勿手改。运行: node scripts/generate-music-tracks.mjs
 * 扫描 Music/ 下的音频，供音乐室使用
 */
export const musicTracks = [
${lines.join('\n')}
]
`

fs.writeFileSync(outFile, content, 'utf8')
console.log(`Generated ${tracks.length} tracks → ${outFile}`)

/**
 * 将 musicTracks 条目转为播放器可用的曲目列表（含 URL）
 */

function encodePathSegments(relativePath) {
  return relativePath
    .replace(/\\/g, '/')
    .split('/')
    .map((seg) => (seg ? encodeURIComponent(seg) : ''))
    .join('/')
}

export function getMusicBase() {
  return (import.meta.env.VITE_MUSIC_BASE_URL || '').replace(/\/$/, '')
}

export function musicUrl(relativePath) {
  if (!relativePath) return ''
  const normalized = relativePath.replace(/^\//, '')
  const encoded = encodePathSegments(normalized)
  const musicBase = getMusicBase()
  if (musicBase) return `${musicBase}/${encoded}`
  const base = import.meta.env.BASE_URL || '/'
  return `${base}${encoded}`
}

export function buildTrackList(rawTracks) {
  const musicBase = getMusicBase()
  return rawTracks.map(t => ({
    name: t.name,
    source: musicBase ? 'CDN' : t.source,
    album: t.source,
    path: t.path,
    cover: t.cover || '',
    url: musicUrl(t.path),
  }))
}

const COVER_NAMES = ['folder.jpg', 'COVER.jpg', 'cover.jpg']

export function albumCoverUrl(trackPath, explicitCover = '') {
  if (explicitCover) return musicUrl(explicitCover)
  if (!trackPath) return ''
  const dir = trackPath.replace(/\/[^/]+$/, '')
  return musicUrl(`${dir}/${COVER_NAMES[0]}`)
}

export function groupTracksByAlbum(tracks) {
  const groups = []
  let lastAlbum = null
  for (let i = 0; i < tracks.length; i++) {
    const track = tracks[i]
    const albumKey = track.album || track.source
    if (albumKey !== lastAlbum) {
      groups.push({ source: albumKey, tracks: [], coverUrl: '' })
      lastAlbum = albumKey
    }
    groups[groups.length - 1].tracks.push({ ...track, index: i })
  }
  for (const group of groups) {
    const first = group.tracks[0]
    group.coverUrl = albumCoverUrl(first?.path, first?.cover)
  }
  return groups
}

export function getCurrentAlbumCover(tracks, currentIndex) {
  if (currentIndex < 0 || currentIndex >= tracks.length) return ''
  const track = tracks[currentIndex]
  return albumCoverUrl(track?.path, track?.cover)
}

/** 音乐是否由服务器/Nginx 同域提供（非打包进 dist） */
export function isServerHostedMusic() {
  if (getMusicBase()) return true
  return import.meta.env.PROD && import.meta.env.VITE_BUNDLE_STATIC_MEDIA !== '1'
}

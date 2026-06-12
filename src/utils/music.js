/**
 * 将 musicTracks 条目转为播放器可用的曲目列表（含 URL）
 */
export function getMusicBase() {
  return (import.meta.env.VITE_MUSIC_BASE_URL || '').replace(/\/$/, '')
}

export function musicUrl(relativePath) {
  const musicBase = getMusicBase()
  if (musicBase) return `${musicBase}${relativePath}`
  const base = import.meta.env.BASE_URL || '/'
  const clean = relativePath.replace(/^\//, '')
  return base + encodeURI(clean)
}

export function buildTrackList(rawTracks) {
  const musicBase = getMusicBase()
  return rawTracks.map(t => ({
    name: t.name,
    source: musicBase ? 'CDN' : t.source,
    url: musicUrl(t.path),
  }))
}

export function groupTracksByAlbum(tracks) {
  const groups = []
  let lastSource = null
  for (let i = 0; i < tracks.length; i++) {
    const track = tracks[i]
    if (track.source !== lastSource) {
      groups.push({ source: track.source, tracks: [] })
      lastSource = track.source
    }
    groups[groups.length - 1].tracks.push({ ...track, index: i })
  }
  return groups
}

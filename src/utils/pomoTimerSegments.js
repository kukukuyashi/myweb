/** 番茄钟 UI 分段：长时段合并显示，避免 45 格挤成一团 */

const MAX_VISUAL = 12

function pickCols(count) {
  const n = Math.max(1, count)
  if (n <= 5) return n
  if (n <= 6) return 6
  if (n <= 9) return 3
  if (n <= 12) return 4
  return 6
}

/**
 * @param {number} totalMinutes
 * @returns {{ visualCount: number, minutesPerSlot: number, cols: number }}
 */
export function getTimerSegments(totalMinutes) {
  const total = Math.max(1, Math.round(totalMinutes))

  if (total <= MAX_VISUAL) {
    return { visualCount: total, minutesPerSlot: 1, cols: pickCols(total) }
  }
  if (total <= 24) {
    const minutesPerSlot = 2
    const visualCount = Math.ceil(total / minutesPerSlot)
    return { visualCount, minutesPerSlot, cols: pickCols(visualCount) }
  }
  if (total <= 36) {
    const minutesPerSlot = 3
    const visualCount = Math.ceil(total / minutesPerSlot)
    return { visualCount, minutesPerSlot, cols: pickCols(visualCount) }
  }
  const minutesPerSlot = 5
  const visualCount = Math.ceil(total / minutesPerSlot)
  return { visualCount, minutesPerSlot, cols: pickCols(visualCount) }
}

/** 专注：已击发的整格数 */
export function spentSegmentCount(minutesElapsed, minutesPerSlot, visualCount) {
  const spent = Math.floor(minutesElapsed / minutesPerSlot)
  return Math.min(visualCount, spent)
}

/** 休息：已充能的整格数 */
export function chargedSegmentCount(minutesElapsed, minutesPerSlot, visualCount) {
  return spentSegmentCount(minutesElapsed, minutesPerSlot, visualCount)
}

/**
 * 当前格内进度 0~1（专注=剩余弹药比例，休息=充能比例）
 * @param {'focus'|'break'} mode
 */
export function segmentFillRatio(index, minutesElapsed, minutesPerSlot, mode) {
  const i = index + 1
  const spent = Math.floor(minutesElapsed / minutesPerSlot)
  const partial = (minutesElapsed % minutesPerSlot) / minutesPerSlot

  if (mode === 'break') {
    if (i <= spent) return 1
    if (i === spent + 1) return partial
    return 0
  }

  if (i <= spent) return 0
  if (i === spent + 1) return 1 - partial
  return 1
}

export function segmentHint(minutesPerSlot, visualCount) {
  if (minutesPerSlot <= 1) return ''
  return `每格 ${minutesPerSlot} min · ${visualCount} 段`
}

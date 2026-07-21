import { ref } from 'vue'

const BLUR_KEY = 'cyinc_forum_backdrop_blur'
const DARK_KEY = 'cyinc_forum_backdrop_dark'

const DEFAULT_BLUR = 22
const DEFAULT_DARK = 45

export const BLUR_RANGE = { min: 0, max: 40 }
export const DARK_RANGE = { min: 0, max: 80 }

function clamp(value, min, max) {
  const n = Number(value)
  if (Number.isNaN(n)) return min
  return Math.min(max, Math.max(min, n))
}

function readNumber(key, fallback, range) {
  if (typeof localStorage === 'undefined') return fallback
  try {
    const raw = localStorage.getItem(key)
    if (raw === null) return fallback
    return clamp(raw, range.min, range.max)
  } catch {
    return fallback
  }
}

const blur = ref(readNumber(BLUR_KEY, DEFAULT_BLUR, BLUR_RANGE))
const dark = ref(readNumber(DARK_KEY, DEFAULT_DARK, DARK_RANGE))

export function setForumBlur(value) {
  blur.value = clamp(value, BLUR_RANGE.min, BLUR_RANGE.max)
  try {
    localStorage.setItem(BLUR_KEY, String(blur.value))
  } catch {
    /* ignore */
  }
}

export function setForumDark(value) {
  dark.value = clamp(value, DARK_RANGE.min, DARK_RANGE.max)
  try {
    localStorage.setItem(DARK_KEY, String(dark.value))
  } catch {
    /* ignore */
  }
}

export function useForumBackdrop() {
  return {
    blur,
    dark,
    setForumBlur,
    setForumDark,
    BLUR_RANGE,
    DARK_RANGE,
  }
}

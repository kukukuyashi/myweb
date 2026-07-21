import { ref } from 'vue'

const BLUR_KEY = 'cyinc_forum_backdrop_blur'
const DARK_KEY = 'cyinc_forum_backdrop_dark'
const CARD_KEY = 'cyinc_forum_card_opacity'
const BG_HIDDEN_KEY = 'cyinc_forum_bg_hidden'
const CARD_SOLID_KEY = 'cyinc_forum_card_solid'

const DEFAULT_BLUR = 22
const DEFAULT_DARK = 45
const DEFAULT_CARD = 62

export const BLUR_RANGE = { min: 0, max: 40 }
export const DARK_RANGE = { min: 0, max: 80 }
export const CARD_RANGE = { min: 20, max: 100 }

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

function readBool(key, fallback) {
  if (typeof localStorage === 'undefined') return fallback
  try {
    const raw = localStorage.getItem(key)
    if (raw === null) return fallback
    return raw === '1' || raw === 'true'
  } catch {
    return fallback
  }
}

const blur = ref(readNumber(BLUR_KEY, DEFAULT_BLUR, BLUR_RANGE))
const dark = ref(readNumber(DARK_KEY, DEFAULT_DARK, DARK_RANGE))
const cardOpacity = ref(readNumber(CARD_KEY, DEFAULT_CARD, CARD_RANGE))
const bgHidden = ref(readBool(BG_HIDDEN_KEY, false))
const cardSolid = ref(readBool(CARD_SOLID_KEY, false))

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

export function setForumCardOpacity(value) {
  cardOpacity.value = clamp(value, CARD_RANGE.min, CARD_RANGE.max)
  try {
    localStorage.setItem(CARD_KEY, String(cardOpacity.value))
  } catch {
    /* ignore */
  }
}

export function setForumBgHidden(value) {
  bgHidden.value = !!value
  try {
    localStorage.setItem(BG_HIDDEN_KEY, bgHidden.value ? '1' : '0')
  } catch {
    /* ignore */
  }
}

export function setForumCardSolid(value) {
  cardSolid.value = !!value
  try {
    localStorage.setItem(CARD_SOLID_KEY, cardSolid.value ? '1' : '0')
  } catch {
    /* ignore */
  }
}

export function useForumBackdrop() {
  return {
    blur,
    dark,
    cardOpacity,
    bgHidden,
    cardSolid,
    setForumBlur,
    setForumDark,
    setForumCardOpacity,
    setForumBgHidden,
    setForumCardSolid,
    BLUR_RANGE,
    DARK_RANGE,
    CARD_RANGE,
  }
}
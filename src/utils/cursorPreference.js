const STORAGE_KEY = 'cyinc-native-cursor'
const CLASS_NAME = 'use-native-cursor'
const EVENT_NAME = 'cyinc-cursor-change'

export function prefersNativeCursor() {
  try {
    return localStorage.getItem(STORAGE_KEY) === '1'
  } catch {
    return false
  }
}

function applyClass(native) {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle(CLASS_NAME, native)
}

export function setNativeCursor(native) {
  const enabled = !!native
  try {
    if (enabled) localStorage.setItem(STORAGE_KEY, '1')
    else localStorage.removeItem(STORAGE_KEY)
  } catch {}
  applyClass(enabled)
  window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: { native: enabled } }))
}

export function onCursorPreferenceChange(handler) {
  const listener = (e) => handler(!!e?.detail?.native)
  window.addEventListener(EVENT_NAME, listener)
  return () => window.removeEventListener(EVENT_NAME, listener)
}

applyClass(prefersNativeCursor())

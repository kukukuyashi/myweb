const STORAGE_KEY = 'theme'

export function isDarkTheme() {
  return document.documentElement.getAttribute('data-theme') === 'dark'
}

export function applyTheme(dark) {
  if (dark) {
    document.documentElement.setAttribute('data-theme', 'dark')
    localStorage.setItem(STORAGE_KEY, 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
    localStorage.setItem(STORAGE_KEY, 'light')
  }
}

/** 在 Vue 挂载前调用，避免首屏闪烁与 /app 路由未初始化主题 */
export function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark')
    return true
  }
  if (saved === 'light') {
    document.documentElement.removeAttribute('data-theme')
    return false
  }
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  if (prefersDark) {
    document.documentElement.setAttribute('data-theme', 'dark')
  }
  return prefersDark
}

export function toggleTheme() {
  applyTheme(!isDarkTheme())
  return isDarkTheme()
}

export function getInitialDarkState() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'dark') return true
  if (saved === 'light') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

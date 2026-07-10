import { ref } from 'vue'

const STORAGE_KEY = 'cyinc_platform_sidebar_collapsed'

function readCollapsed() {
  if (typeof localStorage === 'undefined') return false
  try {
    return localStorage.getItem(STORAGE_KEY) === '1'
  } catch {
    return false
  }
}

const collapsed = ref(typeof window !== 'undefined' ? readCollapsed() : false)

function applyDataset() {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.platformSidebar = collapsed.value ? 'collapsed' : 'expanded'
}

if (typeof window !== 'undefined') applyDataset()

export function setPlatformSidebarCollapsed(value) {
  collapsed.value = !!value
  try {
    if (collapsed.value) localStorage.setItem(STORAGE_KEY, '1')
    else localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* ignore */
  }
  applyDataset()
  window.dispatchEvent(new CustomEvent('platform-sidebar-changed'))
}

export function togglePlatformSidebar() {
  setPlatformSidebarCollapsed(!collapsed.value)
}

export function usePlatformSidebar() {
  return {
    collapsed,
    setPlatformSidebarCollapsed,
    togglePlatformSidebar,
  }
}

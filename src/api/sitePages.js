import { clearNotesAdminToken, getNotesAdminToken } from './notesAdmin'

function apiRoot() {
  return (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')
}

function unwrap(json) {
  if (json && typeof json === 'object' && Object.prototype.hasOwnProperty.call(json, 'code')) {
    if (json.code !== 0) throw new Error(json.message || 'error')
    return json.data
  }
  return json
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json; charset=utf-8', ...(options.headers || {}) }
  const token = getNotesAdminToken()
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${apiRoot()}/site-pages${path}`, { ...options, headers, credentials: 'include' })
  let json = {}
  try { json = await res.json() } catch { json = {} }
  if (res.status === 401) clearNotesAdminToken()
  if (!res.ok) {
    const detail = json.detail || json.error || json.message || `HTTP ${res.status}`
    throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg || item).join('; ') : detail)
  }
  return unwrap(json)
}

export function fetchSitePage(pageKey) {
  if (!['about', 'archive'].includes(pageKey)) throw new Error('不支持的页面配置')
  return request(`/${pageKey}`)
}

export function saveSitePage(pageKey, content) {
  if (!['about', 'archive'].includes(pageKey)) throw new Error('不支持的页面配置')
  return request(`/${pageKey}`, { method: 'PUT', body: JSON.stringify({ content }) })
}

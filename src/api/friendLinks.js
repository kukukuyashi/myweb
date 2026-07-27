import { getNotesAdminToken, clearNotesAdminToken } from './notesAdmin'

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
  const res = await fetch(`${apiRoot()}/friend-links${path}`, { ...options, headers, credentials: 'include' })
  let json = {}
  try { json = await res.json() } catch { json = {} }
  if (res.status === 401) clearNotesAdminToken()
  if (!res.ok) {
    const detail = json.detail || json.error || json.message || `HTTP ${res.status}`
    const msg = Array.isArray(detail) ? detail.map((d) => d.msg || d).join('; ') : detail
    throw new Error(msg)
  }
  return unwrap(json)
}

export function fetchFriendLinksPublic() {
  return request('')
}

export function fetchFriendLinksAdmin({ q = '', category = '', page = 1, pageSize = 20 } = {}) {
  const params = new URLSearchParams({ q, category, page: String(page), pageSize: String(pageSize) })
  return request(`/admin?${params.toString()}`)
}

export function fetchFriendLinkCategories() {
  return request('/admin/categories')
}

export function createFriendLink(payload) {
  return request('/admin', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateFriendLink(id, payload) {
  return request(`/admin/${id}`, { method: 'PATCH', body: JSON.stringify(payload) })
}

export function deleteFriendLink(id) {
  return request(`/admin/${id}`, { method: 'DELETE' })
}
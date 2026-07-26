import { getNotesAdminToken, clearNotesAdminToken } from './notesAdmin'

function apiRoot() {
  return (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')
}

function unwrap(json) {
  if (json && typeof json === 'object' && Object.prototype.hasOwnProperty.call(json, 'code')) {
    if (json.code !== 0) throw new Error(json.message || '????')
    return json.data
  }
  return json
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json; charset=utf-8', ...(options.headers || {}) }
  const token = getNotesAdminToken()
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${apiRoot()}/glossary${path}`, { ...options, headers, credentials: 'include' })
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

// ??????????????
export function fetchGlossaryPublic() {
  return request('')
}

// ???????
export function fetchGlossaryAdmin({ q = '', page = 1, pageSize = 20 } = {}) {
  const params = new URLSearchParams({ q, page: String(page), pageSize: String(pageSize) })
  return request(`/admin?${params.toString()}`)
}

export function createGlossaryTerm(payload) {
  return request('/admin', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateGlossaryTerm(id, payload) {
  return request(`/admin/${id}`, { method: 'PATCH', body: JSON.stringify(payload) })
}

export function deleteGlossaryTerm(id) {
  return request(`/admin/${id}`, { method: 'DELETE' })
}

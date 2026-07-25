import { clearNotesAdminToken, getNotesAdminToken } from './notesAdmin.js'

function apiBase() {
  const env = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')
  return `${env}/admin/crud`
}

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    ...(options.headers || {}),
  }
  const token = getNotesAdminToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${apiBase()}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  let json = {}
  try {
    json = await res.json()
  } catch {
    json = {}
  }

  if (res.status === 401) clearNotesAdminToken()

  if (!res.ok) {
    const detail = json.detail || json.error || json.message || `HTTP ${res.status}`
    const msg = Array.isArray(detail) ? detail.map((d) => d.msg || d).join('; ') : detail
    throw new Error(msg)
  }

  if (json && typeof json === 'object' && Object.prototype.hasOwnProperty.call(json, 'code')) {
    if (json.code !== 0) throw new Error(json.message || '请求失败')
    return json.data
  }
  return json
}

export function listResource(resource, { page = 1, pageSize = 20, q = '', sort = '-id' } = {}) {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
    sort,
  })
  if (q) params.set('q', q)
  return request(`/${resource}?${params.toString()}`)
}

export function getResource(resource, id) {
  return request(`/${resource}/${id}`)
}

export function updateResource(resource, id, payload) {
  return request(`/${resource}/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload || {}),
  })
}

export function deleteResource(resource, id) {
  return request(`/${resource}/${id}`, { method: 'DELETE' })
}

export function bulkDeleteResource(resource, ids) {
  return request(`/${resource}/bulk-delete`, {
    method: 'POST',
    body: JSON.stringify({ ids }),
  })
}
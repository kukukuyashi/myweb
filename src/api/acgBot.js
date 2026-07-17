// ACG 资讯机器人管理 API —— 复用笔记管理台的运维账号 token。
import {
  clearNotesAdminToken,
  getNotesAdminToken,
} from './notesAdmin'

function apiBase() {
  const env = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')
  return `${env}/acg-bot`
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
  })

  let json = {}
  try {
    json = await res.json()
  } catch {
    json = {}
  }

  if (res.status === 401) {
    clearNotesAdminToken()
  }

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

export function generateDigest({ useAi = false, categoryId = null } = {}) {
  return request('/generate', {
    method: 'POST',
    body: JSON.stringify({ use_ai: useAi, category_id: categoryId }),
  })
}

export function fetchSubmissions(status = 'all') {
  const q = status && status !== 'all' ? `?status=${encodeURIComponent(status)}` : ''
  return request(`/submissions${q}`)
}

export function fetchSubmission(id) {
  return request(`/submissions/${id}`)
}

export function updateSubmission(id, payload) {
  return request(`/submissions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function previewSubmission(id) {
  return request(`/submissions/${id}/preview`, { method: 'POST' })
}

export function publishSubmission(id) {
  return request(`/submissions/${id}/publish`, { method: 'POST' })
}

export function discardSubmission(id) {
  return request(`/submissions/${id}`, { method: 'DELETE' })
}

export function fetchForumCategories() {
  return request('/categories')
}

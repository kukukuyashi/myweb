// 留言板防护设置 API —— 复用笔记管理台的运维账号 token。
// 留言本身的列表/删除走 adminCrud.js 的 qa 资源。
import {
  clearNotesAdminToken,
  getNotesAdminToken,
} from './notesAdmin'

function apiBase() {
  const env = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')
  return `${env}/qa`
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

export function fetchQaSettings() {
  return request('/admin/settings')
}

export function saveQaSettings(payload) {
  return request('/admin/settings', { method: 'PUT', body: JSON.stringify(payload) })
}

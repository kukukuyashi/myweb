const TOKEN_KEY = 'cyinc_notes_admin_token'

function apiBase() {
  // 与 platform.js 一致：本地默认直连 FastAPI；生产用 /api/v1 相对路径
  const env = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')
  return `${env}/notes-admin`
}

export function getNotesAdminToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setNotesAdminToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function clearNotesAdminToken() {
  localStorage.removeItem(TOKEN_KEY)
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

  // FastAPI ok() wrapper OR legacy flat JSON
  if (json && typeof json === 'object' && Object.prototype.hasOwnProperty.call(json, 'code')) {
    if (json.code !== 0) throw new Error(json.message || '请求失败')
    return json.data
  }
  return json
}

export function loginNotesAdmin(username, password) {
  return request('/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  }).then((data) => {
    if (data?.token) setNotesAdminToken(data.token)
    return data
  })
}

export function fetchNotesAdminMe() {
  return request('/me')
}

export function fetchCategories() {
  return request('/categories')
}

export function fetchNotes(category = '全部') {
  const q = category && category !== '全部' ? `?category=${encodeURIComponent(category)}` : ''
  return request(`/notes${q}`)
}

export function fetchNote(relPath) {
  return request(`/notes/${encodeURIComponent(relPath)}`)
}

export function saveNote(relPath, payload) {
  return request(`/notes/${encodeURIComponent(relPath)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function createNote(payload) {
  return request('/notes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function publishNote(relPath) {
  return request(`/notes/${encodeURIComponent(relPath)}/publish`, {
    method: 'POST',
  })
}

export function previewNote(payload) {
  return request('/preview', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function moveNote(relPath, category) {
  return request(`/notes/${encodeURIComponent(relPath)}/move`, {
    method: 'POST',
    body: JSON.stringify({ category }),
  })
}

export function deleteNote(relPath, { unpublish = false } = {}) {
  const q = unpublish ? '?unpublish=1' : ''
  return request(`/notes/${encodeURIComponent(relPath)}${q}`, {
    method: 'DELETE',
  })
}

/** 线上无 Vite build；保留函数避免旧 UI 报错 */
export function runBuild() {
  return Promise.reject(new Error('线上发布写入 Content + posts.json 即可，无需整站 Build'))
}

export function fetchCovers() {
  return request('/covers')
}

export function fetchContentStatus() {
  return request('/content/status')
}

export function adoptSiteNote(htmlFile) {
  return request('/notes/adopt', {
    method: 'POST',
    body: JSON.stringify({ htmlFile }),
  })
}

export function adoptAllSiteNotes() {
  return request('/notes/adopt-all', {
    method: 'POST',
  })
}

export function syncContent(files = null) {
  return request('/content/sync', {
    method: 'POST',
    body: JSON.stringify({ files }),
  })
}

/** 上传笔记正文图片，返回 { url, markdown } */
export async function uploadNoteImage(file) {
  const form = new FormData()
  form.append('file', file)
  const token = getNotesAdminToken()
  const headers = {}
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${apiBase()}/uploads/image`, {
    method: 'POST',
    headers,
    body: form,
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
    if (json.code !== 0) throw new Error(json.message || '上传失败')
    return json.data
  }
  return json
}

import { formatApiError } from '../utils/apiError.js'
import { imgUrl } from '../data/profile.js'

const BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')

/** API 服务根 URL（静态文件 /uploads 用） */
export function apiOrigin() {
  return BASE.replace(/\/api\/v1$/i, '')
}

/** 解析头像等相对路径 */
export function resolveMediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('blob:')) return url
  const origin = apiOrigin()
  return `${origin}${url.startsWith('/') ? url : `/${url}`}`
}

/**
 * 站点静态资源（img/…）+ API 上传（/uploads/…）+ 外链统一解析。
 * 论坛头像、封面等混用路径时用这个，不要用 imgUrl 硬拼外链。
 */
export function resolvePublicUrl(url) {
  if (!url) return ''
  const s = String(url).trim()
  if (!s) return ''
  if (s.startsWith('http://') || s.startsWith('https://') || s.startsWith('data:') || s.startsWith('blob:')) {
    return s
  }
  if (s.startsWith('img/') || s.startsWith('/img/')) {
    return imgUrl(s.replace(/^\//, ''))
  }
  return resolveMediaUrl(s)
}

export function getPlatformToken() {
  return localStorage.getItem('cyinc_platform_token') || ''
}

export function setPlatformToken(token) {
  if (token && typeof token === 'string') {
    localStorage.setItem('cyinc_platform_token', token)
  } else {
    localStorage.removeItem('cyinc_platform_token')
  }
  window.dispatchEvent(new CustomEvent('platform-auth-changed'))
}

export function requirePlatformToken() {
  const token = getPlatformToken()
  if (!token) {
    const err = new Error('登录已过期，请重新登录')
    err.code = 'AUTH_REQUIRED'
    throw err
  }
  return token
}

export async function platformFetch(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json; charset=utf-8' }
  if (auth) {
    headers.Authorization = `Bearer ${requirePlatformToken()}`
  }
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body != null ? JSON.stringify(body) : undefined,
  })
  let json
  try {
    json = await res.json()
  } catch {
    throw new Error(res.statusText || '请求失败')
  }
  if (!res.ok) {
    if (res.status === 401) {
      setPlatformToken(null)
      const err = new Error(formatApiError(json.detail ?? json.message ?? '登录已过期，请重新登录'))
      err.code = 'AUTH_REQUIRED'
      throw err
    }
    throw new Error(formatApiError(json.detail ?? json.message ?? res.statusText))
  }
  if (json.code != null && json.code !== 0) {
    throw new Error(formatApiError(json.message) || '业务错误')
  }
  return json
}

export async function platformLogin(username, password) {
  const json = await platformFetch('/auth/login', {
    method: 'POST',
    body: { username, password },
  })
  const accessToken = json?.data?.access_token
  if (!accessToken) throw new Error('登录失败：未收到有效令牌')
  setPlatformToken(accessToken)
  return json.data
}

export async function sendEmailVerificationCode(email) {
  const json = await platformFetch('/auth/email/code', {
    method: 'POST',
    body: { email: String(email).trim() },
  })
  return { ...(json.data || {}), message: json.message }
}

export async function sendPasswordResetCode(email) {
  const json = await platformFetch('/auth/password/code', {
    method: 'POST',
    body: { email: String(email).trim() },
  })
  return { ...(json.data || {}), message: json.message }
}

export async function resetPassword({ email, code, password }) {
  const json = await platformFetch('/auth/password/reset', {
    method: 'POST',
    body: { email: String(email).trim(), code: String(code).trim(), password },
  })
  return { ...(json.data || {}), message: json.message }
}

export async function platformRegister({ username, email, password, code, nickname }) {
  await platformFetch('/auth/register', {
    method: 'POST',
    body: { username, email, password, code, nickname },
  })
  return platformLogin(username, password)
}

export async function fetchAiStatus() {
  return platformFetch('/ai/status')
}

export async function sendAiChat(query, conversationId) {
  return platformFetch('/ai/chat', {
    method: 'POST',
    auth: true,
    body: { query, conversation_id: conversationId || null },
  })
}

export async function fetchProfile() {
  return platformFetch('/users/me', { auth: true })
}

export async function updateProfile(payload) {
  return platformFetch('/users/me', {
    method: 'PATCH',
    auth: true,
    body: payload,
  })
}

export async function changePassword({ currentPassword, newPassword }) {
  return platformFetch('/users/me/password', {
    method: 'POST',
    auth: true,
    body: {
      current_password: currentPassword,
      new_password: newPassword,
    },
  })
}

export async function uploadAvatar(file) {
  const token = requirePlatformToken()
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/users/me/avatar`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  })
  let json
  try {
    json = await res.json()
  } catch {
    throw new Error(res.statusText || '上传失败')
  }
  if (!res.ok) {
    let msg = json.detail || json.message || res.statusText
    if (res.status === 404) {
      msg = '头像接口未就绪，请重启后端（uvicorn --reload）后再试'
    }
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg))
  }
  if (json.code != null && json.code !== 0) {
    throw new Error(json.message || '上传失败')
  }
  return json
}

export async function fetchMyPosts(page = 1, pageSize = 20) {
  return platformFetch(`/posts/mine?page=${page}&page_size=${pageSize}`, { auth: true })
}

export async function fetchPost(id, { auth = false } = {}) {
  return platformFetch(`/posts/${id}`, { auth })
}

export async function createPost(payload) {
  return platformFetch('/posts', {
    method: 'POST',
    auth: true,
    body: payload,
  })
}

export async function updatePost(id, payload) {
  return platformFetch(`/posts/${id}`, {
    method: 'PATCH',
    auth: true,
    body: payload,
  })
}

export async function deletePost(id) {
  return platformFetch(`/posts/${id}`, {
    method: 'DELETE',
    auth: true,
  })
}

export async function generatePostSummary(id) {
  return platformFetch(`/posts/${id}/summary`, {
    method: 'POST',
    auth: true,
  })
}

export async function fetchPosts(page = 1, pageSize = 10) {
  return platformFetch(`/posts?page=${page}&page_size=${pageSize}&status=published`)
}

export async function fetchPomodoroStats() {
  return platformFetch('/pomodoro/stats', { auth: true })
}

export async function fetchPomodoroSessions(page = 1, pageSize = 10) {
  return platformFetch(`/pomodoro/sessions?page=${page}&page_size=${pageSize}`, { auth: true })
}

export async function createPomodoroSession(payload) {
  return platformFetch('/pomodoro/sessions', {
    method: 'POST',
    auth: true,
    body: payload,
  })
}

export async function fetchPomodoroTimeline(days = 14) {
  return platformFetch(`/pomodoro/timeline?days=${days}`, { auth: true })
}

export async function fetchForumCategories() {
  return platformFetch('/forum/categories')
}

export async function fetchForumRecentThreads(limit = 5) {
  return platformFetch(`/forum/threads/recent?limit=${limit}`)
}

export async function fetchForumFeaturedThreads() {
  return platformFetch('/forum/threads/featured')
}

export async function fetchForumCategoryThreads(slug, page = 1, pageSize = 20) {
  return platformFetch(`/forum/categories/${slug}/threads?page=${page}&page_size=${pageSize}`)
}

export async function fetchForumThread(id) {
  return platformFetch(`/forum/threads/${id}`)
}

export async function fetchMyForumThreads(page = 1, pageSize = 20) {
  return platformFetch(`/forum/threads/mine?page=${page}&page_size=${pageSize}`, { auth: true })
}

export async function uploadForumImage(file) {
  return uploadEditorImage(file, '/forum/uploads/image')
}

export async function uploadPostImage(file) {
  return uploadEditorImage(file, '/posts/uploads/image')
}

async function uploadEditorImage(file, path) {
  const token = requirePlatformToken()
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(formatApiError(json, res.status))
  }
  if (json.code != null && json.code !== 0) {
    throw new Error(formatApiError(json.message) || '上传失败')
  }
  return json
}

export async function createForumThread(payload) {
  return platformFetch('/forum/threads', {
    method: 'POST',
    auth: true,
    body: payload,
  })
}

export async function updateForumThread(id, payload) {
  return platformFetch(`/forum/threads/${id}`, {
    method: 'PATCH',
    auth: true,
    body: payload,
  })
}

export async function deleteForumThread(id) {
  return platformFetch(`/forum/threads/${id}`, {
    method: 'DELETE',
    auth: true,
  })
}

export async function createForumReply(threadId, content) {
  return platformFetch(`/forum/threads/${threadId}/replies`, {
    method: 'POST',
    auth: true,
    body: { content },
  })
}

export async function likeForumThread(threadId) {
  return platformFetch(`/forum/threads/${threadId}/like`, { method: 'POST', auth: true })
}

export async function likeForumReply(replyId) {
  return platformFetch(`/forum/replies/${replyId}/like`, { method: 'POST', auth: true })
}

export async function shareForumThread(threadId) {
  return platformFetch(`/forum/threads/${threadId}/share`, { method: 'POST', auth: true })
}

export async function fetchUserProfile(userId) {
  return platformFetch(`/users/${userId}`)
}

export async function fetchUserThreads(userId) {
  return platformFetch(`/users/${userId}/threads`)
}

export async function fetchNotifications(page = 1, pageSize = 20) {
  return platformFetch(`/notifications?page=${page}&page_size=${pageSize}`, { auth: true })
}

export async function fetchNotificationUnread() {
  return platformFetch('/notifications/unread-count', { auth: true })
}

export async function markNotificationRead(id) {
  return platformFetch(`/notifications/${id}/read`, { method: 'POST', auth: true })
}

export async function markAllNotificationsRead() {
  return platformFetch('/notifications/read-all', { method: 'POST', auth: true })
}

export async function fetchCheckinStatus() {
  return platformFetch('/users/me/checkin/status', { auth: true })
}

export async function doCheckin() {
  return platformFetch('/users/me/checkin', { method: 'POST', auth: true })
}

export async function fetchCheckinCalendar(months = 3) {
  return platformFetch(`/users/me/checkin/calendar?months=${months}`, { auth: true })
}

export async function fetchAnimeSchedule() {
  const token = getPlatformToken()
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 30000)
  try {
    const headers = { 'Content-Type': 'application/json; charset=utf-8' }
    if (token) headers.Authorization = `Bearer ${token}`
    const res = await fetch(`${BASE}/anime/schedule`, { headers, signal: controller.signal })
    const json = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(formatApiError(json.detail ?? json.message ?? res.statusText))
    if (json.code != null && json.code !== 0) throw new Error(formatApiError(json.message) || '业务错误')
    return json
  } catch (e) {
    if (e.name === 'AbortError') throw new Error('请求超时，请稍后重试')
    throw e
  } finally {
    clearTimeout(timer)
  }
}

export async function fetchAnimeCalendar() {
  return platformFetch('/anime/calendar')
}

export async function fetchAnimeToday() {
  const token = getPlatformToken()
  if (!token) return platformFetch('/anime/today')
  const res = await fetch(`${BASE}/anime/today`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json; charset=utf-8',
    },
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(formatApiError(json.detail ?? json.message ?? res.statusText))
  if (json.code != null && json.code !== 0) throw new Error(formatApiError(json.message) || '业务错误')
  return json
}

export async function fetchAnimeWatchlist() {
  return platformFetch('/anime/watchlist', { auth: true })
}

export async function addAnimeWatchlist(payload) {
  return platformFetch('/anime/watchlist', { method: 'POST', auth: true, body: payload })
}

export async function removeAnimeWatchlist(bangumiId) {
  return platformFetch(`/anime/watchlist/${bangumiId}`, { method: 'DELETE', auth: true })
}

export async function fetchQaMessages(limit = 20) {
  return platformFetch(`/qa/messages?limit=${limit}`)
}

export async function createQaMessage(payload) {
  return platformFetch('/qa/messages', {
    method: 'POST',
    body: payload,
  })
}
export async function fetchStudyRoomMessages({ before, limit = 50 } = {}) {
  const qs = new URLSearchParams()
  if (before != null) qs.set('before', String(before))
  qs.set('limit', String(limit))
  return platformFetch(`/study-room/messages?${qs.toString()}`)
}

export async function fetchStudyRoomOnline() {
  return platformFetch('/study-room/online')
}

export function openStudyRoomSocket({ token, onMessage, onPresence, onOpen, onClose, onError } = {}) {
  // WS 协议必须跟当前页面一致(HTTPS 页用 wss,否则浏览器当 mixed content 拦)
  // 用 window.location 拼绝对 URL,不再用 apiOrigin()(它返回相对路径,无法判定协议)
  const proto = (typeof window !== 'undefined' && window.location && window.location.protocol === 'https:') ? 'wss:' : 'ws:'
  const host = (typeof window !== 'undefined' && window.location && window.location.host) || (apiOrigin().replace(/^https?:\/\//, ''))
  const url = `${proto}//${host}/api/v1/study-room/ws?token=${encodeURIComponent(token || '')}`
  let ws = null
  let backoff = 1000
  let closedByUser = false
  let reconnectTimer = null

  function connect() {
    try {
      ws = new WebSocket(url)
    } catch (e) {
      scheduleReconnect()
      return
    }
    ws.onopen = () => {
      backoff = 1000
      if (typeof onOpen === 'function') onOpen()
    }
    let lastPongAt = Date.now()
    ws.onmessage = (ev) => {
      let data
      try { data = JSON.parse(ev.data) } catch { return }
      if (!data || typeof data !== 'object') return
      if (data.type === 'pong') {
        lastPongAt = Date.now()
        return
      }
      if (data.type === 'ping') {
        try { ws.send(JSON.stringify({ type: 'pong' })) } catch {}
        return
      }
      if (data.type === 'msg' || data.type === 'history' || data.type === 'err') {
        if (typeof onMessage === 'function') onMessage(data)
      } else if (data.type === 'presence') {
        if (typeof onPresence === 'function') onPresence(data)
      }
    }
    // 瀹氭椂 ping: 姣? 5s 鍙?type:ping, server 鍥炵瓑 pong 鏇存柊 lastPongAt
    // 濡傛灉 8s 鍐呮湭鏀跺埌 pong -> 璇?ws 宸叉, 寮哄埗 close 瑙﹀彂 onclose
    const pingTimer = setInterval(() => {
      if (!ws || ws.readyState !== 1) return
      try { ws.send(JSON.stringify({ type: 'ping' })) } catch {}
      if (Date.now() - lastPongAt > 8000) {
        console.warn('[ws] no pong for 8s, force close')
        try { ws.close() } catch {}
        clearInterval(pingTimer)
      }
    }, 5000)
    ws.addEventListener('close', () => clearInterval(pingTimer))
    ws.onerror = (e) => {
      if (typeof onError === 'function') onError(e)
    }
    ws.onclose = () => {
      if (typeof onClose === 'function') onClose()
      if (!closedByUser) scheduleReconnect()
    }
  }

  function scheduleReconnect() {
    if (closedByUser) return
    const delay = Math.min(backoff, 10000)
    backoff = Math.min(backoff * 2, 10000)
    reconnectTimer = setTimeout(connect, delay)
  }

  connect()

  return {
    send(payload) {
      if (!ws || ws.readyState !== 1) return false
      try {
        // 兼容两种调用:
        //  send({ type: 'msg', content: text })  文本
        //  send({ type: 'msg', content: null, sticker_url: url })  表情
        //  send('纯文本')  旧 API(自动包成 {type,content})
        const body = (typeof payload === 'string')
          ? { type: 'msg', content: payload }
          : payload
        ws.send(JSON.stringify(body))
        if (ws.readyState !== 1) { console.warn('[ws] half-open detected, readyState=', ws.readyState, 'close+false'); try { ws.close() } catch {}; return false }
        return true
      } catch { return false }
    },
    pong() {
      if (!ws || ws.readyState !== 1) return false
      try { ws.send(JSON.stringify({ type: 'pong' })); return true } catch { return false }
    },
    close() {
      closedByUser = true
      if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
      if (ws) {
        try { ws.close() } catch {}
        ws = null
      }
    },
  }
}


// ============== Admin (study-room) ==============
export async function adminListStudyRoomMessages({ before, limit = 50, includeDeleted = 1 } = {}) {
  const qs = new URLSearchParams()
  if (before) qs.set('before', String(before))
  qs.set('limit', String(limit))
  qs.set('include_deleted', String(includeDeleted))
  return platformFetch(`/study-room/admin/messages?${qs.toString()}`, { auth: true })
}

export async function adminDeleteStudyRoomMessage(id) {
  return platformFetch(`/study-room/admin/messages/${id}`, { method: 'DELETE', auth: true })
}

export async function adminRestoreStudyRoomMessage(id) {
  return platformFetch(`/study-room/admin/messages/${id}/restore`, { method: 'POST', auth: true })
}

export async function adminListStudyRoomOnlineUsers() {
  return platformFetch('/study-room/admin/users', { auth: true })
}

export async function adminKickUser(userId, reason) {
  const q = reason ? '?reason=' + encodeURIComponent(reason) : ''
  return platformFetch(`/study-room/admin/kick/${userId}${q}`, { method: 'POST', auth: true })
}

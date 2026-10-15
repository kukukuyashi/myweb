// ── 导入区：本文件用到的 3 个外部工具 ─────────────────────────────

// formatApiError：把后端返回的错误（可能是英文/数组/对象）翻成一句中文提示给用户看
import { formatApiError } from '../utils/apiError.js' 
// 笔记管理台的 token 读写——注意：它和下面普通用户的 platform token 是两套独立登录体系
import { getNotesAdminToken, setNotesAdminToken } from './notesAdmin.js'
// imgUrl：把 img/ 开头的站内图片相对路径补全成完整 URL
import { imgUrl } from '../data/profile.js'

// BASE = 后端 API 的统一前缀，形如 'http://127.0.0.1:8000/api/v1'
// import.meta.env.VITE_API_BASE_URL：Vite 读 .env 配置的写法；读不到就用 || 后的本地默认值
// 末尾 .replace(/\/$/, '')：删掉结尾多余的 /，防止后面拼路径时出现双斜杠
const BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')

/**
 * 【导读】apiOrigin / resolveMediaUrl / resolvePublicUrl 三兄弟干同一件事：
 * 数据库里存的图片路径五花八门（/uploads/x.png、img/x.jpg、http 外链），
 * 它们负责统一补全成浏览器能直接打开的完整 URL。
 *
 * apiOrigin：返回服务器"裸地址"。BASE 尾部带着 /api/v1，砍掉它就是。
 */
export function apiOrigin() {
  // 正则 /\/api\/v1$/i：匹配末尾的 "/api/v1"（$=结尾，i=不区分大小写），替换成空 = 删掉
  return BASE.replace(/\/api\/v1$/i, '')
}

/**
 * 解析头像等相对路径 → 完整 URL。
 * 例：'/uploads/avatar/1.png' → 'http://127.0.0.1:8000/uploads/avatar/1.png'
 */
export function resolveMediaUrl(url) {
  // 没传路径（null/空串）直接返回空，防止拼出 'null' 这种怪 URL
  if (!url) return ''
  // 已经是完整地址的三种情况原样返回：http 外链、data:base64 内嵌图、blob:本地预览
  if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('blob:')) return url
  // 先拿到服务器裸地址（就是上面 apiOrigin）
  const origin = apiOrigin()
  // 三元表达式拼接：url 以 / 开头就直接拼；否则手动补一个 / 再拼（保证只有一条斜杠）
  return `${origin}${url.startsWith('/') ? url : `/${url}`}`
}

/**
 * 站点静态资源（img/…）+ API 上传（/uploads/…）+ 外链统一解析。
 * 论坛头像、封面等混用路径时用这个，不要用 imgUrl 硬拼外链。
 * 【导读】相当于"总入口"：先判断路径属于哪一类，再分派给对应的处理方式。
 */
export function resolvePublicUrl(url) {
  // 空值直接返回空
  if (!url) return ''
  // 统一转成字符串并 trim 掉首尾空格（防御脏数据，比如带空格的路径）
  const s = String(url).trim()
  // 去完空格变空了也返回空
  if (!s) return ''
  // 第一类：已经是完整地址（http/https 外链、data: 内嵌图、blob: 预览），原样返回
  if (s.startsWith('http://') || s.startsWith('https://') || s.startsWith('data:') || s.startsWith('blob:')) {
    return s
  }
  // 第二类：img/ 开头 = 前端自带的站内图片，交给 imgUrl（它会处理 /myweb/ 前缀）
  if (s.startsWith('img/') || s.startsWith('/img/')) {
    // 先把可能存在的开头 / 去掉，统一成 'img/xx' 形式再传
    return imgUrl(s.replace(/^\//, ''))
  }
  // 第三类：剩下的基本是 /uploads/…（后端上传的文件），交给 resolveMediaUrl 拼服务器地址
  return resolveMediaUrl(s)
}

// ── 登录 token 的存取 ───────────────────────────────────────────
// token 存在浏览器 localStorage（键名 cyinc_platform_token），
// 关浏览器也不丢——这就是"登录一次能保持很久"的原理。

/** 读 token：localStorage 里没有就返回 ''（|| '' 把 null 变空串，方便后面统一判空） */
export function getPlatformToken() {
  return localStorage.getItem('cyinc_platform_token') || ''
}

/**
 * 写/清 token：传字符串 = 登录；传 null/空 = 退出登录。
 * 末尾广播自定义事件 'platform-auth-changed'，让导航栏等组件实时刷新登录状态。
 */
export function setPlatformToken(token) {
  // 只接受"非空字符串"——防止把 null/undefined 存成字符串 'null'
  if (token && typeof token === 'string') {
    // 存 token
    localStorage.setItem('cyinc_platform_token', token)
  } else {
    // 否则一律视为清除登录态
    localStorage.removeItem('cyinc_platform_token')
  }
  // 派发事件：谁关心登录态就监听这个名字
  window.dispatchEvent(new CustomEvent('platform-auth-changed'))
}

/**
 * "必须有 token"版本：给需要登录才能调的接口用。
 * 没登录不是返回空糊弄过去，而是直接抛错——err.code='AUTH_REQUIRED' 是给页面识别的标记，
 * 页面 catch 到它就知道该跳登录页，而不是当普通网络错误弹个提示完事。
 */
export function requirePlatformToken() {
  // 先试着读 token
  const token = getPlatformToken()
  // 没有 → 造一个带 code 标记的错误抛出去
  if (!token) {
    const err = new Error('登录已过期，请重新登录')
    err.code = 'AUTH_REQUIRED'
    throw err
  }
  // 有 → 交给调用方用
  return token
}

/**
 * 【导读】platformFetch = 全站请求的"总闸门"：所有业务接口都经它发出去。
 * 它帮你包办 4 件重复劳动：
 *   1. 自动拼 BASE 前缀（调用处只写 '/auth/login' 这种短路径）
 *   2. 按三种认证模式自动塞 Authorization: Bearer <token> 请求头
 *   3. body 对象自动 JSON.stringify
 *   4. 统一处理错误：401 自动清登录态、错误翻成中文、业务 code≠0 也抛错
 *
 * 参数：path=接口短路径；method=HTTP 方法（默认 GET）；body=要发的对象；
 *   auth=true         必须登录（没 token 当场抛 AUTH_REQUIRED，请求不会发出）
 *   adminAuth=true    用笔记管理台那套 token
 *   optionalAuth=true 有 token 就带、没有也能调（游客可见的接口）
 *
 * 签名里 { … } = {} 是"解构+默认值"写法：允许 platformFetch('/xx') 只传一个参数。
 * async 表示返回 Promise，调用方用 await 拿结果。
 */
export async function platformFetch(path, { method = 'GET', body, auth = false, adminAuth = false, optionalAuth = false } = {}) {
  // 请求头先声明 Content-Type：告诉后端"body 是 UTF-8 编码的 JSON"
  const headers = { 'Content-Type': 'application/json; charset=utf-8' }
  // 模式一：强制登录。requirePlatformToken() 没 token 会当场抛错，fetch 根本不会执行
  if (auth) {
    // Bearer 方案：JWT 令牌固定写成 "Bearer <token>" 放进 Authorization 头
    headers.Authorization = `Bearer ${requirePlatformToken()}`
  // 模式二：管理台 token（不校验存在与否，token 为空会发出 "Bearer "）
  } else if (adminAuth) {
    headers.Authorization = `Bearer ${getNotesAdminToken()}`
  // 模式三：可选登录。有就带上（后端能认出你是谁），没有就匿名访问
  } else if (optionalAuth) {
    const token = getPlatformToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }
  // 真正发请求：fetch 是浏览器自带的 HTTP 客户端；await 暂停等响应回来
  const res = await fetch(`${BASE}${path}`, {
    method,   // HTTP 方法
    headers,  // 上面拼好的请求头
    // body != null（不为 null/undefined）才 JSON 化；GET 没有 body 传 undefined，fetch 会忽略
    body: body != null ? JSON.stringify(body) : undefined,
  })
  // 响应统一按 JSON 解析（这个后端所有接口都返回 JSON）
  let json
  try {
    json = await res.json()
  } catch {
    // 解析失败 = 返回的根本不是 JSON（比如服务器宕机回了 HTML 错误页），用 HTTP 状态文本顶包
    throw new Error(res.statusText || '请求失败')
  }
  // res.ok = 状态码 2xx；非 2xx 进入错误处理
  if (!res.ok) {
    // 401 = 未认证（token 过期/无效）：除了报错还要顺手清掉本地存的坏 token
    if (res.status === 401) {
      // 清哪套 token，看这次用的是哪套认证
      if (adminAuth) setNotesAdminToken(null)
      else setPlatformToken(null)
      // json.detail 是 FastAPI 错误字段，json.message 是业务统一格式；?? = 左边为 null/undefined 才取右边
      const err = new Error(formatApiError(json.detail ?? json.message ?? '登录已过期，请重新登录'))
      err.code = 'AUTH_REQUIRED'   // 打标记，页面靠它跳登录
      throw err
    }
    // 其他 HTTP 错误（400/403/404/500…）：同样翻成中文抛出
    throw new Error(formatApiError(json.detail ?? json.message ?? res.statusText))
  }
  // HTTP 层过了还要查业务层：后端约定统一返回 { code, message, data }，code===0 才算真成功
  if (json.code != null && json.code !== 0) {
    // code 存在且非 0 → 业务失败（比如"验证码错误"）
    throw new Error(formatApiError(json.message) || '业务错误')
  }
  // 所有关卡通过：整包 JSON 返回，调用方自己取 .data
  return json
}

/**
 * 【导读】platformLogin：调 /auth/login，把后端发的 access_token 存进 localStorage。
 * 存完 token，之后所有 auth=true 的请求就自动带上了——这就是"登录态"。
 */
export async function platformLogin(username, password) {
  // 走总闸门发 POST；不需要 token（还没登录呢）
  const json = await platformFetch('/auth/login', {
    method: 'POST',
    body: { username, password },
  })
  // 后端统一格式 { code, message, data }，token 在 data.access_token；?. 可选链防止某层为空时报错
  const accessToken = json?.data?.access_token
  // 防御：说成功了却没给 token，属于异常，当失败处理
  if (!accessToken) throw new Error('登录失败：未收到有效令牌')
  // 存 token（同时广播 platform-auth-changed，UI 自动切成已登录）
  setPlatformToken(accessToken)
  // data 里可能还有用户信息等，整块返回给调用方
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

export async function fetchPomodoroStats() {
  return platformFetch('/pomodoro/stats', { auth: true })
}

export async function fetchPomodoroTimeline(days = 90) {
  return platformFetch(`/pomodoro/timeline?days=${days}`, { auth: true })
}

export async function createPomodoroSession(payload) {
  return platformFetch('/pomodoro/sessions', {
    method: 'POST',
    auth: true,
    body: payload,
  })
}

export async function fetchQaMessages(limit = 20) {
  return platformFetch(`/qa/messages?limit=${limit}`)
}

export async function fetchQaBoardStatus() {
  return platformFetch('/qa/board-status')
}

export async function createQaMessage(payload) {
  return platformFetch('/qa/messages', {
    method: 'POST',
    body: payload,
    optionalAuth: true,
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
      if (['msg', 'history', 'err', 'delete', 'restore', 'kick'].includes(data.type)) {
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
  return platformFetch(`/study-room/admin/messages?${qs.toString()}`, { adminAuth: true })
}

export async function adminDeleteStudyRoomMessage(id) {
  return platformFetch(`/study-room/admin/messages/${id}`, { method: 'DELETE', adminAuth: true })
}

export async function adminRestoreStudyRoomMessage(id) {
  return platformFetch(`/study-room/admin/messages/${id}/restore`, { method: 'POST', adminAuth: true })
}

export async function adminListStudyRoomOnlineUsers() {
  return platformFetch('/study-room/admin/users', { adminAuth: true })
}

export async function adminKickUser(userId, reason) {
  const q = reason ? '?reason=' + encodeURIComponent(reason) : ''
  return platformFetch(`/study-room/admin/kick/${userId}${q}`, { method: 'POST', adminAuth: true })
}

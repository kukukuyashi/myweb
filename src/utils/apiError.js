const FIELD_LABELS = {
  email: '邮箱',
  username: '账号',
  password: '密码',
  current_password: '当前密码',
  new_password: '新密码',
  code: '验证码',
  nickname: '昵称',
}

function fieldLabel(loc) {
  if (!Array.isArray(loc) || !loc.length) return '请求参数'
  const key = String(loc[loc.length - 1])
  return FIELD_LABELS[key] || key
}

function validationItemToZh(item) {
  if (typeof item === 'string') return item
  if (!item || typeof item !== 'object') return '请求参数有误'

  const label = fieldLabel(item.loc)
  const msg = item.msg || ''
  const type = item.type || ''
  const lowered = msg.toLowerCase()

  if (msg.startsWith('Value error, ')) {
    return msg.slice('Value error, '.length)
  }

  if (type === 'missing') return `请填写${label}`

  if (label === '邮箱' || lowered.includes('email address') || lowered.includes('at-sign')) {
    return '邮箱格式不正确，须为有效邮箱地址（含 @ 符号）'
  }

  if (label === '验证码') return '验证码须为 6 位数字'

  if (label === '账号') {
    if (type.includes('pattern')) return '账号仅允许字母、数字与下划线（3–50 位）'
    if (type.includes('too_short')) return '账号至少 3 个字符'
  }

  if (label === '密码') {
    if (type.includes('too_short')) return '密码至少 9 位，且须含大小写字母与数字'
    return '密码格式不符合要求'
  }

  if (type.includes('too_short')) {
    const min = item.ctx?.min_length
    return min ? `${label}长度不能少于 ${min} 个字符` : `${label}内容过短`
  }

  if (type.includes('pattern')) return `${label}格式不正确`

  return msg ? `${label}：${msg}` : `${label}格式不正确`
}

/** 解析 FastAPI / 业务 API 错误体为中文可读字符串 */
export function formatApiError(detail) {
  if (!detail) return '请求失败'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const parts = detail.map(validationItemToZh).filter(Boolean)
    return parts.length ? parts.join('；') : '请求参数有误'
  }
  if (typeof detail === 'object') {
    if (detail.message) return String(detail.message)
    if (detail.msg) return validationItemToZh(detail)
  }
  try {
    return JSON.stringify(detail)
  } catch {
    return '请求失败'
  }
}

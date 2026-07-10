<template>
  <AuthShell
    title="创建 CYINC 账户"
    subtitle="填写以下信息完成注册，验证码将发送到邮箱"
    brand-title="加入 CYINC 社区"
    brand-copy="注册后可逛论坛、收藏歌单、记录专注 — 与同好一起分享 ACG 与技术日常。"
    :panel-image="authRegisterPanel"
    :backdrop-image="authPageBackdrop"
    :stats="[
      { value: '邮箱', label: '验证码注册' },
      { value: '9+', label: '位安全密码' },
      { value: 'JWT', label: '会话登录' },
    ]"
    footer-note="© CYINC · 用爱发电，为爱而生"
  >
    <form class="auth-form" @submit.prevent="handleRegister">
      <label class="auth-field">
        <span class="auth-field__label">账号 *</span>
        <div class="auth-field__wrap">
          <input
            v-model="form.username"
            required
            autocomplete="username"
            placeholder="3–50 位字母数字下划线"
            pattern="[A-Za-z0-9_]{3,50}"
          />
          <span class="auth-field__icon" aria-hidden="true">@</span>
        </div>
      </label>
      <p class="auth-form-text">账号用于登录，注册后不可更改</p>

      <label class="auth-field">
        <span class="auth-field__label">邮箱 *</span>
        <div class="auth-field__wrap">
          <input
            v-model="form.email"
            type="email"
            required
            autocomplete="email"
            placeholder="you@example.com"
          />
          <span class="auth-field__icon" aria-hidden="true">✉</span>
        </div>
      </label>
      <p class="auth-form-text">{{ emailTip }}</p>

      <div class="auth-row">
        <label class="auth-field auth-field--grow">
          <span class="auth-field__label">邮箱验证码 *</span>
          <div class="auth-field__wrap">
            <input
              v-model="form.code"
              required
              inputmode="numeric"
              maxlength="6"
              placeholder="6 位数字"
              pattern="\d{6}"
            />
            <span class="auth-field__icon" aria-hidden="true">#</span>
          </div>
        </label>
        <button
          type="button"
          class="auth-code-btn"
          :disabled="codeSending || codeCooldown > 0 || !form.email.trim()"
          @click="sendCode"
        >
          {{ codeCooldown > 0 ? `${codeCooldown}s` : codeSending ? '发送中…' : '发送验证码' }}
        </button>
      </div>
      <p v-if="codeHint" class="auth-form-text auth-form-text--hint">{{ codeHint }}</p>

      <label class="auth-field">
        <span class="auth-field__label">密码 *</span>
        <div class="auth-field__wrap">
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            required
            autocomplete="new-password"
            placeholder="至少 9 位，含大小写与数字"
          />
          <button
            type="button"
            class="auth-field__icon auth-field__icon-btn"
            :aria-label="showPassword ? '隐藏密码' : '显示密码'"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? '🙈' : '👁' }}
          </button>
        </div>
      </label>

      <label class="auth-field">
        <span class="auth-field__label">昵称（可选）</span>
        <div class="auth-field__wrap">
          <input
            v-model="form.nickname"
            maxlength="100"
            placeholder="显示名称，默认同用户名"
          />
          <span class="auth-field__icon" aria-hidden="true">★</span>
        </div>
      </label>

      <p v-if="success" class="auth-success">{{ success }}</p>
      <p v-if="error" class="auth-error">{{ error }}</p>

      <button type="submit" class="auth-submit" :disabled="loading">
        <span class="auth-submit__icon" aria-hidden="true">→</span>
        {{ loading ? '注册中…' : '立即注册' }}
      </button>
    </form>

    <template #switch>
      已有账户？<router-link to="/app/login">立即登录</router-link>
    </template>
  </AuthShell>
</template>

<script setup>
import { computed, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from './AuthShell.vue'
import { platformRegister, sendEmailVerificationCode } from '../../api/platform.js'
import { authPageBackdrop, authRegisterPanel } from '../../data/authGallery.js'

const router = useRouter()
const loading = ref(false)
const codeSending = ref(false)
const codeCooldown = ref(0)
const error = ref('')
const success = ref('')
const codeHint = ref('')
const showPassword = ref(false)
const form = ref({
  username: '',
  email: '',
  code: '',
  password: '',
  nickname: '',
})
let cooldownTimer = null

const emailTip = computed(() => {
  const email = form.value.email.trim()
  return email ? `验证码将发送到 ${email}` : '请输入邮箱并获取验证码'
})

function startCooldown(seconds = 60) {
  codeCooldown.value = seconds
  cooldownTimer = setInterval(() => {
    codeCooldown.value -= 1
    if (codeCooldown.value <= 0) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

async function sendCode() {
  const email = form.value.email.trim()
  if (!email) {
    error.value = '请先填写邮箱'
    return
  }
  codeSending.value = true
  error.value = ''
  success.value = ''
  codeHint.value = ''
  try {
    const data = await sendEmailVerificationCode(email)
    if (data?.dev_code) {
      success.value = `开发模式验证码：${data.dev_code}`
      codeHint.value = data.message || '未配置 SMTP 时验证码显示在上方；生产环境将发送至邮箱。'
    } else {
      success.value = data.message || '验证码已发送，请查收邮箱（含垃圾箱）。'
    }
    startCooldown(60)
  } catch (e) {
    error.value = e.message || '发送失败，请检查邮箱格式或稍后重试'
  } finally {
    codeSending.value = false
  }
}

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await platformRegister({
      username: form.value.username.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
      code: form.value.code.trim(),
      nickname: form.value.nickname.trim() || undefined,
    })
    router.replace('/app/me')
  } catch (e) {
    error.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
</script>

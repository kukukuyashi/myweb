<template>
  <AuthShell
    title="重置密码"
    subtitle="通过邮箱验证码重置你的账号密码"
    brand-title="找回账号"
    brand-copy="我们会向注册邮箱发送一个 6 位验证码，验证通过后即可设置新密码。"
    :panel-image="authVisual.panel"
    :backdrop-image="authVisual.backdrop"
    :stats="[
      { value: '邮箱', label: '验证码验证' },
      { value: '9+', label: '位安全密码' },
      { value: '一次', label: '即发即用' },
    ]"
    footer-note="© CYINC · 用爱发电，与博客账号通用"
  >
    <form class="auth-form" @submit.prevent="handleReset">
      <label class="auth-field">
        <span class="auth-field__label">注册邮箱 *</span>
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
        <span class="auth-field__label">新密码 *</span>
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

      <p v-if="success" class="auth-success">{{ success }}</p>
      <p v-if="error" class="auth-error">{{ error }}</p>

      <button type="submit" class="auth-submit" :disabled="loading">
        <span class="auth-submit__icon" aria-hidden="true">→</span>
        {{ loading ? '重置中…' : '重置密码' }}
      </button>
    </form>

    <template #switch>
      <router-link to="/app/login">← 返回登录</router-link>
    </template>
  </AuthShell>
</template>

<script setup>
import { onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from './AuthShell.vue'
import { sendPasswordResetCode, resetPassword } from '../../api/platform.js'
import { getAuthVisuals } from '../../data/authGallery.js'

const authVisual = getAuthVisuals()
const router = useRouter()
const loading = ref(false)
const codeSending = ref(false)
const codeCooldown = ref(0)
const error = ref('')
const success = ref('')
const codeHint = ref('')
const showPassword = ref(false)
const form = ref({ email: '', code: '', password: '' })
let cooldownTimer = null

function startCooldown() {
  codeCooldown.value = 60
  cooldownTimer = setInterval(() => {
    codeCooldown.value--
    if (codeCooldown.value <= 0) clearInterval(cooldownTimer)
  }, 1000)
}

async function sendCode() {
  codeHint.value = ''
  codeSending.value = true
  try {
    const result = await sendPasswordResetCode(form.value.email.trim())
    codeHint.value = result.message || '验证码已发送'
    startCooldown()
  } catch (e) {
    error.value = e.message || '发送失败'
  } finally {
    codeSending.value = false
  }
}

async function handleReset() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await resetPassword({
      email: form.value.email.trim(),
      code: form.value.code.trim(),
      password: form.value.password,
    })
    success.value = '密码已重置，正在跳转登录页面…'
    setTimeout(() => router.replace('/app/login'), 1500)
  } catch (e) {
    error.value = e.message || '重置失败'
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
</script>
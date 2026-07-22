<template>
  <AuthShell
    title="开启 CYINC 之旅"
    subtitle="登录您的账号，探索主站功能"
    brand-title="欢迎回来"
    brand-copy="登录后可管理资料、发布 Markdown 文章、参与论坛讨论，并同步番茄钟专注记录。"
    :panel-image="authVisual.panel"
    :backdrop-image="authVisual.backdrop"
    :stats="authDefaultStats"
    footer-note="© CYINC · 用爱发电，与博客账号通用"
  >
    <form class="auth-form" @submit.prevent="handleLogin">
      <label class="auth-field">
        <span class="auth-field__label">账号或邮箱</span>
        <div class="auth-field__wrap">
          <input
            v-model="form.username"
            required
            autocomplete="username"
            placeholder="请输入账号或注册邮箱"
          />
          <span class="auth-field__icon" aria-hidden="true">👤</span>
        </div>
      </label>

      <label class="auth-field">
        <span class="auth-field__label">密码</span>
        <div class="auth-field__wrap">
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            required
            autocomplete="current-password"
            placeholder="请输入您的密码"
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

      <div class="auth-field-meta">
        <label class="auth-remember">
          <input v-model="rememberMe" type="checkbox" />
          <span>在此设备上记住账号</span>
        </label>
      </div>

      <p v-if="error" class="auth-error">{{ error }}</p>

      <button type="submit" class="auth-submit" :disabled="loading">
        <span class="auth-submit__icon" aria-hidden="true">→</span>
        {{ loading ? '登录中…' : '立即登录' }}
      </button>
    </form>

    <template #switch>
      还没有账号？<router-link to="/app/register">立即注册</router-link>
      <span class="auth-switch-sep">·</span>
      <router-link to="/app/forgot-password">忘记密码</router-link>
    </template>
  </AuthShell>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthShell from './AuthShell.vue'
import { platformLogin } from '../../api/platform.js'
import { authDefaultStats, getAuthVisuals } from '../../data/authGallery.js'

const REMEMBER_KEY = 'cyinc_remember_username'
const authVisual = getAuthVisuals()

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const form = ref({ username: '', password: '' })

onMounted(() => {
  const saved = localStorage.getItem(REMEMBER_KEY)
  if (saved) {
    form.value.username = saved
    rememberMe.value = true
  }
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await platformLogin(form.value.username, form.value.password)
    if (rememberMe.value) {
      localStorage.setItem(REMEMBER_KEY, form.value.username.trim())
    } else {
      localStorage.removeItem(REMEMBER_KEY)
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/app/me'
    router.replace(redirect)
  } catch (e) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-switch-sep {
  margin: 0 0.4rem;
  color: var(--text-muted);
}
</style>
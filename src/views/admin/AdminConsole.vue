<template>
  <div class="admin-console">
    <!-- 未登录：统一登录门 -->
    <div v-if="!authed" class="console-login-wrap">
      <div class="platform-panel console-login-card">
        <span class="console-badge">CYINC ADMIN</span>
        <h2>登录管理控制台</h2>
        <p class="login-hint">使用运维账号（ADMIN_USERNAME / 密码），一次登录管理笔记、机器人与数据。</p>
        <form class="login-form" @submit.prevent="handleLogin">
          <label>
            用户名
            <input v-model="loginForm.username" type="text" autocomplete="username" required />
          </label>
          <label>
            密码
            <input v-model="loginForm.password" type="password" autocomplete="current-password" required />
          </label>
          <p v-if="loginError" class="toast" data-type="error">{{ loginError }}</p>
          <button type="submit" class="platform-btn-primary" :disabled="loggingIn">
            {{ loggingIn ? '登录中…' : '登录' }}
          </button>
        </form>
      </div>
    </div>

    <!-- 已登录：外壳布局 -->
    <div v-else class="console-shell">
      <aside class="console-sidebar" :class="{ open: mobileNavOpen }">
        <div class="console-brand">
          <span class="brand-mark">◈</span>
          <div class="brand-text">
            <strong>管理控制台</strong>
            <small>CYINC Console</small>
          </div>
        </div>

        <nav class="console-nav">
          <template v-for="group in navGroups" :key="group.title">
            <p class="nav-group-title">{{ group.title }}</p>
            <router-link
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              class="nav-item"
              :class="{ active: isActive(item) }"
              @click="mobileNavOpen = false"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </template>
        </nav>

        <div class="console-user">
          <div class="user-meta">
            <span class="user-avatar">{{ (username || 'A').slice(0, 1).toUpperCase() }}</span>
            <div>
              <strong>{{ username || '管理员' }}</strong>
              <small>Administrator</small>
            </div>
          </div>
          <button type="button" class="platform-btn-ghost logout-btn" @click="logout">退出登录</button>
        </div>
      </aside>

      <div v-if="mobileNavOpen" class="console-scrim" @click="mobileNavOpen = false"></div>

      <div class="console-main">
        <header class="console-topbar">
          <button type="button" class="console-burger" @click="mobileNavOpen = !mobileNavOpen" aria-label="菜单">☰</button>
          <h1 class="console-title">{{ activeTitle }}</h1>
          <div class="topbar-actions">
            <a class="platform-btn-ghost" href="/myweb/app" target="_blank" rel="noopener">打开站点 ↗</a>
          </div>
        </header>

        <main class="console-content">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  clearNotesAdminToken,
  fetchNotesAdminMe,
  getNotesAdminToken,
  loginNotesAdmin,
} from '../../api/notesAdmin.js'

const route = useRoute()
const authed = ref(Boolean(getNotesAdminToken()))
const username = ref('')
const loggingIn = ref(false)
const loginError = ref('')
const mobileNavOpen = ref(false)
const loginForm = reactive({ username: '', password: '' })

const navGroups = [
  {
    title: '概览',
    items: [{ label: '仪表盘', icon: '▦', to: '/admin', exact: true }],
  },
  {
    title: '内容管理',
    items: [{ label: '笔记管理', icon: '✎', to: '/admin/notes' }],
  },
  {
    title: '论坛',
    items: [{ label: '发帖机器人', icon: '✦', to: '/admin/acg-bot' }],
  },
  {
    title: '系统',
    items: [{ label: '数据管理', icon: '▤', to: '/admin/data' }],
  },
]

const flatItems = navGroups.flatMap((g) => g.items)

function isActive(item) {
  if (item.exact) return route.path === '/admin' || route.path === '/admin/'
  return route.path === item.to || route.path.startsWith(item.to + '/')
}

const activeTitle = computed(() => {
  const found = flatItems.find((it) => isActive(it))
  return found ? found.label : '管理控制台'
})

async function refreshMe() {
  try {
    const me = await fetchNotesAdminMe()
    username.value = me?.username || ''
  } catch {
    username.value = ''
  }
}

async function handleLogin() {
  loggingIn.value = true
  loginError.value = ''
  try {
    await loginNotesAdmin(loginForm.username.trim(), loginForm.password)
    loginForm.password = ''
    authed.value = true
    await refreshMe()
  } catch (err) {
    loginError.value = err.message || '登录失败'
  } finally {
    loggingIn.value = false
  }
}

function logout() {
  clearNotesAdminToken()
  authed.value = false
  username.value = ''
}

if (authed.value) refreshMe()
</script>

<style scoped>
.admin-console {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

/* 登录门 */
.console-login-wrap {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
}
.console-login-card {
  width: min(420px, 100%);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.console-badge {
  align-self: flex-start;
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--primary-color) 16%, transparent);
  color: var(--primary-color);
}
.console-login-card h2 { margin: 0; font-size: 1.35rem; }
.login-hint { color: var(--text-muted); font-size: 0.9rem; margin: 0; }
.login-form { display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.4rem; }
.login-form label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.9rem; color: var(--text-muted); }
.login-form input {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  color: var(--text);
  font-size: 1rem;
}
.toast[data-type='error'] { color: #d64545; font-size: 0.85rem; margin: 0; }

/* 外壳 */
.console-shell { display: flex; min-height: 100vh; }
.console-sidebar {
  width: 248px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.1rem 0.9rem;
  border-right: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
  background: color-mix(in srgb, var(--bg-paper) 88%, transparent);
  backdrop-filter: blur(10px) saturate(1.1);
  -webkit-backdrop-filter: blur(10px) saturate(1.1);
  position: sticky;
  top: 0;
  height: 100vh;
}
.console-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.5rem 0.9rem;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 45%, transparent);
}
.brand-mark {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: var(--primary-color);
  color: #fff;
  font-size: 1rem;
}
.brand-text { display: flex; flex-direction: column; line-height: 1.2; }
.brand-text strong { font-size: 0.98rem; }
.brand-text small { color: var(--text-muted); font-size: 0.72rem; }

.console-nav { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.15rem; }
.nav-group-title {
  margin: 0.9rem 0.5rem 0.3rem;
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  text-transform: uppercase;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.65rem;
  border-radius: 10px;
  color: var(--text);
  text-decoration: none;
  font-size: 0.92rem;
  transition: background 0.15s ease, color 0.15s ease;
}
.nav-item:hover { background: color-mix(in srgb, var(--text) 6%, transparent); }
.nav-item.active {
  background: color-mix(in srgb, var(--primary-color) 14%, transparent);
  color: var(--primary-color);
  font-weight: 600;
}
.nav-icon { width: 1.2rem; text-align: center; opacity: 0.85; }

.console-user {
  border-top: 1px solid color-mix(in srgb, var(--border) 45%, transparent);
  padding-top: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.user-meta { display: flex; align-items: center; gap: 0.6rem; }
.user-avatar {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--primary-color) 20%, transparent);
  color: var(--primary-color);
  font-weight: 700;
}
.user-meta strong { font-size: 0.9rem; display: block; }
.user-meta small { color: var(--text-muted); font-size: 0.72rem; }
.logout-btn { width: 100%; justify-content: center; }

.console-main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.console-topbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 55%, transparent);
  background: color-mix(in srgb, var(--bg-paper) 80%, transparent);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 20;
}
.console-title { margin: 0; font-size: 1.15rem; flex: 1; }
.topbar-actions { display: flex; gap: 0.5rem; align-items: center; }
.console-burger {
  display: none;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  border-radius: 8px;
  width: 38px;
  height: 34px;
  cursor: pointer;
  font-size: 1.05rem;
}
.console-content { padding: clamp(1rem, 2.5vw, 1.75rem); flex: 1; }
.console-scrim { display: none; }

@media (max-width: 960px) {
  .console-sidebar {
    position: fixed;
    z-index: 40;
    left: 0;
    top: 0;
    transform: translateX(-105%);
    transition: transform 0.22s ease;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.28);
  }
  .console-sidebar.open { transform: translateX(0); }
  .console-burger { display: inline-flex; align-items: center; justify-content: center; }
  .console-scrim {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 30;
  }
}
</style>
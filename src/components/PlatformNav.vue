<template>
  <aside class="platform-sidebar" :class="{ open: menuOpen, 'is-collapsed': collapsed }">
    <div class="sidebar-inner">
      <div class="sidebar-top">
        <router-link to="/app" class="sidebar-logo" @click="menuOpen = false">
          <svg class="logo-mark" width="22" height="22" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <rect x="3" y="3" width="14" height="14" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <path d="M6 10h8M10 6v8" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          <div class="logo-text">
            <strong>CYINC</strong>
            <span>主站</span>
          </div>
        </router-link>
        <button
          type="button"
          class="sidebar-collapse"
          aria-label="收起侧栏"
          title="收起侧栏"
          @click="togglePlatformSidebar"
        >
          ◀
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/app" @click="menuOpen = false">
          <span class="nav-icon">⌂</span> 首页
        </router-link>
        <router-link to="/app/forum" @click="menuOpen = false">
          <span class="nav-icon">☷</span> 论坛
        </router-link>
        <router-link to="/app/music" @click="menuOpen = false">
          <span class="nav-icon">♫</span> 音乐室
        </router-link>
        <router-link to="/app/pomo" @click="menuOpen = false">
          <span class="nav-icon">◷</span> 番茄钟
        </router-link>
        <router-link v-if="hasToken" to="/app/me" @click="menuOpen = false">
          <span class="nav-icon">◉</span> 个人中心
        </router-link>
        <router-link v-else to="/app/login" @click="menuOpen = false">
          <span class="nav-icon">→</span> 登录
        </router-link>
        <router-link v-if="!hasToken" to="/app/register" @click="menuOpen = false">
          <span class="nav-icon">+</span> 注册
        </router-link>
      </nav>

      <div class="sidebar-divider" />

      <nav class="sidebar-nav sidebar-nav--sub">
        <router-link to="/" @click="menuOpen = false">
          <span class="nav-icon">↩</span> 返回博客
        </router-link>
      </nav>

      <div class="sidebar-spacer" />

      <SidebarMusicPanel variant="sidebar" @navigate="menuOpen = false" />

      <div class="sidebar-footer">
        <button type="button" class="sidebar-theme" @click="toggleDarkMode">
          {{ isDarkMode ? '☀ 浅色模式' : '☾ 深色模式' }}
        </button>
        <p v-if="hasToken" class="sidebar-user">● 已登录</p>
      </div>
    </div>
  </aside>
  <div v-if="menuOpen" class="sidebar-overlay" @click="menuOpen = false" />
  <button
    v-if="collapsed"
    type="button"
    class="sidebar-reopen"
    aria-label="展开侧栏"
    title="展开侧栏"
    @click="togglePlatformSidebar"
  >
    ☰
  </button>
  <button
    type="button"
    class="sidebar-toggle"
    :aria-expanded="menuOpen"
    @click="menuOpen = !menuOpen"
  >
    {{ menuOpen ? '✕' : '☰' }}
  </button>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPlatformToken } from '../api/platform.js'
import { usePlatformSidebar } from '../composables/usePlatformSidebar.js'
import { applyTheme, getInitialDarkState, toggleTheme } from '../utils/theme.js'
import SidebarMusicPanel from './SidebarMusicPanel.vue'

const route = useRoute()
const menuOpen = ref(false)
const { collapsed, togglePlatformSidebar } = usePlatformSidebar()
const hasToken = ref(!!getPlatformToken())
const isDarkMode = ref(getInitialDarkState())

function syncToken() {
  hasToken.value = !!getPlatformToken()
}

function toggleDarkMode() {
  isDarkMode.value = toggleTheme()
}

applyTheme(isDarkMode.value)

onMounted(() => {
  window.addEventListener('platform-auth-changed', syncToken)
})

onUnmounted(() => {
  window.removeEventListener('platform-auth-changed', syncToken)
})

watch(() => route.path, () => {
  menuOpen.value = false
  syncToken()
})

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})
</script>

<style scoped>
.platform-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1005;
  width: var(--platform-sidebar-width, 240px);
  height: 100vh;
  height: 100dvh;
  border-right: 1px solid var(--border);
  background: var(--bg-paper);
  display: flex;
  flex-direction: column;
  transition: transform 0.22s ease;
}

.sidebar-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.35rem;
  margin-bottom: 1.35rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.sidebar-collapse {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.72rem;
  line-height: 1;
  transition: color 0.15s, border-color 0.15s;
}

.sidebar-collapse:hover {
  color: var(--orange);
  border-color: color-mix(in srgb, var(--orange) 35%, var(--border));
}

.sidebar-reopen {
  display: none;
  position: fixed;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 1004;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text);
  cursor: pointer;
  font-size: 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1.25rem 1rem 1rem;
  overflow-y: auto;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: var(--text);
  min-width: 0;
  flex: 1;
}

.logo-mark {
  color: var(--orange);
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-text strong {
  font-family: var(--mono);
  font-size: 0.88rem;
  letter-spacing: 0.06em;
}

.logo-text span {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.sidebar-nav {
  display: grid;
  gap: 0.2rem;
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 0.65rem;
  border: 1px solid transparent;
  text-decoration: none;
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 0.78rem;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.sidebar-nav a:hover {
  color: var(--text);
  background: color-mix(in srgb, var(--orange) 6%, var(--bg-paper));
  border-color: var(--border);
}

.sidebar-nav a.router-link-active {
  color: var(--orange);
  background: var(--orange-light);
  border-color: color-mix(in srgb, var(--orange) 35%, var(--border));
  box-shadow: inset 3px 0 0 var(--orange);
}

.nav-icon {
  width: 1.1rem;
  text-align: center;
  opacity: 0.85;
}

.sidebar-divider {
  height: 1px;
  background: var(--border);
  margin: 0.85rem 0;
}

.sidebar-nav--sub a {
  font-size: 0.72rem;
}

.sidebar-spacer {
  flex: 1;
  min-height: 1rem;
}

.sidebar-footer {
  display: grid;
  gap: 0.5rem;
  padding-top: 0.85rem;
  border-top: 1px dashed var(--border);
  margin-top: 0.75rem;
}

.sidebar-theme {
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.45rem 0.65rem;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
  text-align: left;
}

.sidebar-theme:hover {
  border-color: var(--orange);
  color: var(--orange);
}

.sidebar-user {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.sidebar-toggle {
  display: none;
  position: fixed;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 1003;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text);
  cursor: pointer;
  font-size: 1rem;
}

.sidebar-overlay {
  display: none;
}

@media (min-width: 961px) {
  .platform-sidebar.is-collapsed {
    transform: translateX(-105%);
  }

  .sidebar-reopen {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar-collapse {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

@media (max-width: 960px) {
  .sidebar-collapse {
    display: none;
  }

  .platform-sidebar.is-collapsed {
    transform: translateX(-105%);
  }

  .platform-sidebar {
    box-shadow: 8px 0 24px rgba(0, 0, 0, 0.12);
  }

  .platform-sidebar.open {
    transform: translateX(0);
  }

  .sidebar-reopen {
    display: none !important;
  }

  .sidebar-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 1001;
    background: rgba(0, 0, 0, 0.35);
  }
}
</style>

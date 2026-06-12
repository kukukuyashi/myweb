<template>
  <header class="topbar">
    <router-link to="/" class="topbar-logo">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <rect x="3" y="3" width="14" height="14" stroke="#e85d04" stroke-width="1.5" fill="none"/>
        <path d="M6 10h8M10 6v8" stroke="#e85d04" stroke-width="1.5"/>
      </svg>
      CYINC.LOG
    </router-link>

    <nav class="topbar-nav" :class="{ open: menuOpen }">
      <router-link to="/" @click="menuOpen = false">首页</router-link>
      <router-link to="/about" @click="menuOpen = false">关于</router-link>
      <router-link to="/archive" @click="menuOpen = false">归档</router-link>
      <router-link to="/music" @click="menuOpen = false">音乐室</router-link>
      <router-link to="/guestbook" @click="menuOpen = false">留言板</router-link>
    </nav>

    <div class="topbar-actions">
      <button @click="toggleDarkMode" class="theme-btn" :title="isDarkMode ? '浅色模式' : '深色模式'">
        {{ isDarkMode ? '☀' : '☾' }}
      </button>
      <button
        class="menu-btn"
        :aria-expanded="menuOpen"
        aria-label="菜单"
        @click="menuOpen = !menuOpen"
      >
        {{ menuOpen ? '✕' : '☰' }}
      </button>
    </div>
  </header>
  <div v-if="menuOpen" class="nav-overlay" @click="menuOpen = false"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isDarkMode = ref(false)
const menuOpen = ref(false)

watch(() => route.path, () => { menuOpen.value = false })

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.setAttribute('data-theme', 'dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  padding: 0 2rem;
  height: var(--topbar-height);
  background: var(--topbar-bg);
  color: #fff;
  font-family: var(--mono);
  font-size: 0.75rem;
  position: sticky;
  top: 0;
  z-index: 1001;
}

.topbar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  font-size: 0.85rem;
  color: #fff;
  text-decoration: none;
  flex-shrink: 0;
}

.topbar-nav {
  display: flex;
  margin-left: auto;
}

.topbar-nav a {
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  padding: 0 1rem;
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.15s;
}

.topbar-nav a:hover,
.topbar-nav a.router-link-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.topbar-nav a.router-link-active {
  box-shadow: inset 0 -2px 0 var(--orange);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 0.5rem;
}

.theme-btn,
.menu-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.menu-btn { display: none; font-size: 0.9rem; }

.theme-btn:hover,
.menu-btn:hover {
  background: var(--orange);
  border-color: var(--orange);
}

.nav-overlay {
  display: none;
}

@media (max-width: 768px) {
  .topbar { padding: 0 1rem; }
  .topbar-nav a { padding: 0 0.6rem; font-size: 0.7rem; }
}

@media (max-width: 640px) {
  .menu-btn { display: flex; }

  .topbar-nav {
    position: fixed;
    top: var(--topbar-height);
    right: 0;
    left: 0;
    flex-direction: column;
    background: var(--topbar-bg);
    border-bottom: 2px solid var(--orange);
    transform: translateY(-110%);
    opacity: 0;
    pointer-events: none;
    transition: transform 0.2s, opacity 0.2s;
    z-index: 1000;
  }

  .topbar-nav.open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
  }

  .topbar-nav a {
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    height: auto;
    padding: 0.85rem 1.25rem;
  }

  .nav-overlay {
    display: block;
    position: fixed;
    inset: var(--topbar-height) 0 0 0;
    background: rgba(0, 0, 0, 0.35);
    z-index: 999;
  }
}
</style>

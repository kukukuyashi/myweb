<template>
  <header class="topbar">
    <router-link to="/" class="topbar-logo">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <rect x="3" y="3" width="14" height="14" stroke="#e85d04" stroke-width="1.5" fill="none"/>
        <path d="M6 10h8M10 6v8" stroke="#e85d04" stroke-width="1.5"/>
      </svg>
      CYINC.LOG
    </router-link>
    <nav class="topbar-nav">
      <router-link to="/">首页</router-link>
      <router-link to="/about">关于</router-link>
      <router-link to="/archive">归档</router-link>
      <router-link to="/music">音乐室</router-link>
      <router-link to="/guestbook">留言板</router-link>
    </nav>
    <button @click="toggleDarkMode" class="theme-btn" :title="isDarkMode ? '浅色模式' : '深色模式'">
      {{ isDarkMode ? '☀' : '☾' }}
    </button>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isDarkMode = ref(false)

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
  z-index: 100;
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

.theme-btn {
  margin-left: 0.5rem;
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

.theme-btn:hover {
  background: var(--orange);
  border-color: var(--orange);
}

@media (max-width: 768px) {
  .topbar { padding: 0 1rem; }
  .topbar-nav a { padding: 0 0.6rem; font-size: 0.7rem; }
  .topbar-logo span { display: none; }
}

@media (max-width: 520px) {
  .topbar-nav a:nth-child(n+4) { display: none; }
}
</style>

<template>
  <header class="platform-topbar">
    <div class="platform-inner">
      <router-link to="/app" class="platform-logo">
        <span class="logo-dot" aria-hidden="true" />
        CYINC 主站
      </router-link>

      <nav class="platform-nav" :class="{ open: menuOpen }">
        <router-link to="/app" @click="menuOpen = false">首页</router-link>
        <router-link to="/app/forum" @click="menuOpen = false">论坛</router-link>
        <router-link to="/app/pomo" @click="menuOpen = false">番茄钟</router-link>
        <router-link to="/app/me" @click="menuOpen = false">个人中心</router-link>
        <router-link to="/ai" @click="menuOpen = false">AI 助手</router-link>
        <router-link to="/" class="back-blog" @click="menuOpen = false">返回博客</router-link>
      </nav>

      <div class="platform-actions">
        <span v-if="hasToken" class="user-hint">已登录</span>
        <button class="menu-btn" :aria-expanded="menuOpen" @click="menuOpen = !menuOpen">
          {{ menuOpen ? '✕' : '☰' }}
        </button>
      </div>
    </div>
    <div v-if="menuOpen" class="nav-overlay" @click="menuOpen = false" />
  </header>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPlatformToken } from '../api/platform.js'

const route = useRoute()
const menuOpen = ref(false)
const hasToken = ref(!!getPlatformToken())

watch(() => route.path, () => {
  menuOpen.value = false
  hasToken.value = !!getPlatformToken()
})
</script>

<style scoped>
.platform-topbar {
  position: sticky;
  top: 0;
  z-index: 1001;
  background: #1a1a2e;
  color: #fff;
  font-family: var(--mono);
  font-size: 0.75rem;
  border-bottom: 2px solid var(--orange);
}

.platform-inner {
  display: flex;
  align-items: center;
  max-width: var(--content-width);
  margin: 0 auto;
  padding: 0 clamp(1rem, 2.5vw, 2.5rem);
  height: calc(var(--topbar-height) + var(--safe-top, 0px));
  padding-top: var(--safe-top, 0);
}

.platform-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #fff;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.logo-dot {
  width: 8px;
  height: 8px;
  background: var(--orange);
  border-radius: 50%;
}

.platform-nav {
  display: flex;
  margin-left: auto;
  align-items: center;
}

.platform-nav a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  padding: 0 0.85rem;
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  transition: color 0.15s, background 0.15s;
}

.platform-nav a:hover,
.platform-nav a.router-link-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}

.platform-nav a.router-link-active {
  box-shadow: inset 0 -2px 0 var(--orange);
}

.back-blog {
  color: var(--orange) !important;
}

.platform-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 0.5rem;
}

.user-hint {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.45);
}

.menu-btn {
  display: none;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  width: 36px;
  height: 36px;
  cursor: pointer;
}

.nav-overlay { display: none; }

@media (max-width: 768px) {
  .menu-btn { display: flex; align-items: center; justify-content: center; }
  .user-hint { display: none; }

  .platform-nav {
    position: fixed;
    top: calc(var(--topbar-height) + var(--safe-top, 0px));
    left: 0;
    right: 0;
    flex-direction: column;
    background: #1a1a2e;
    transform: translateY(-110%);
    opacity: 0;
    pointer-events: none;
    transition: transform 0.2s, opacity 0.2s;
    margin-left: 0;
  }

  .platform-nav.open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
  }

  .platform-nav a {
    width: 100%;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    height: auto;
    padding: 0.9rem 1.25rem;
  }

  .nav-overlay {
    display: block;
    position: fixed;
    inset: calc(var(--topbar-height) + var(--safe-top, 0px)) 0 0 0;
    background: rgba(0, 0, 0, 0.35);
    z-index: 999;
  }
}
</style>

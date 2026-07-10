<template>
  <div
    class="platform-layout"
    :class="{
      'platform-layout--auth': isAuthRoute,
      'platform-layout--sidebar-collapsed': sidebarCollapsed && !isAuthRoute,
    }"
  >
    <PlatformNav v-if="!isAuthRoute" />
    <div class="platform-body">
      <main class="platform-main">
        <router-view />
      </main>
      <footer v-if="!isAuthRoute" class="platform-footer">
        <div class="platform-footer-inner">
          <span class="footer-coord">CYINC · PLATFORM · {{ footerYear }}</span>
          <p class="footer-line">
            与 <router-link to="/">个人博客</router-link> 账号通用 · FastAPI + Vue 3
          </p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PlatformNav from '../components/PlatformNav.vue'
import { usePlatformSidebar } from '../composables/usePlatformSidebar.js'

const route = useRoute()
const { collapsed: sidebarCollapsed } = usePlatformSidebar()
const footerYear = computed(() => new Date().getFullYear())
const isAuthRoute = computed(() => route.name === 'Login' || route.name === 'Register')
</script>

<style scoped>
.platform-layout {
  --platform-sidebar-width: 240px;
  min-height: 100vh;
  background: var(--bg);
}

.platform-layout:not(.platform-layout--auth) .platform-body {
  margin-left: var(--platform-sidebar-width);
  transition: margin-left 0.22s ease;
}

.platform-layout--sidebar-collapsed:not(.platform-layout--auth) .platform-body {
  margin-left: 0;
}

.platform-body {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.platform-main {
  position: relative;
  isolation: isolate;
  flex: 1;
  padding: clamp(1.25rem, 3vw, 2rem) 0 2.5rem;
}

.platform-main::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: min(var(--content-width), calc(100% - 2rem));
  background: var(--bg-paper);
  border-left: 1px solid var(--border);
  border-right: 1px solid var(--border);
  box-shadow:
    0 1px 0 rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.35);
  pointer-events: none;
  z-index: 0;
}

[data-theme="dark"] .platform-main::before {
  box-shadow:
    0 1px 0 rgba(0, 0, 0, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

.platform-layout--auth .platform-main::before {
  display: none;
}

.platform-layout--auth .platform-main {
  padding: 0;
}

.platform-footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 1.25rem 1rem;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg-paper) 85%, var(--bg));
}

.platform-footer-inner {
  max-width: var(--content-width);
  margin: 0 auto;
}

.footer-coord {
  display: block;
  letter-spacing: 0.12em;
  color: var(--orange);
  margin-bottom: 0.35rem;
}

.footer-line {
  margin: 0;
}

.platform-footer a {
  color: var(--orange);
}

@media (max-width: 960px) {
  .platform-layout:not(.platform-layout--auth) .platform-body {
    margin-left: 0;
  }

  .platform-layout:not(.platform-layout--auth) .platform-main {
    padding-top: 3.5rem;
  }
}
</style>

<template>
  <div class="platform-layout">
    <PlatformNav />
    <main class="platform-main">
      <router-view />
    </main>
    <footer class="platform-footer">
      <div class="platform-footer-inner">
        <span class="footer-coord">CYINC · PLATFORM · {{ footerYear }}</span>
        <p class="footer-line">
          与 <router-link to="/">个人博客</router-link> 账号通用 · FastAPI + Vue 3
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PlatformNav from '../components/PlatformNav.vue'

const footerYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.platform-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.platform-main {
  position: relative;
  isolation: isolate;
  flex: 1;
  padding: 2rem 0 3rem;
}

.platform-main::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: var(--content-width);
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

.platform-main::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: var(--content-width);
  pointer-events: none;
  z-index: 0;
  background:
    linear-gradient(var(--orange) 0 0) 0 0 / 12px 2px no-repeat,
    linear-gradient(var(--orange) 0 0) 100% 0 / 12px 2px no-repeat,
    linear-gradient(var(--orange) 0 0) 0 100% / 12px 2px no-repeat,
    linear-gradient(var(--orange) 0 0) 100% 100% / 12px 2px no-repeat;
  opacity: 0.45;
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
  background: color-mix(in srgb, var(--bg-paper) 80%, var(--bg));
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
</style>

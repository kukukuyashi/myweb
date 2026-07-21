<template>
  <div
    class="platform-layout"
    :class="{
      'platform-layout--auth': isAuthRoute,
      'platform-layout--sidebar-collapsed': sidebarCollapsed && !isAuthRoute,
    }"
  >
    <div
      v-if="!isAuthRoute && backdropUrl"
      class="platform-backdrop"
      :style="backdropStyle"
      aria-hidden="true"
    ></div>
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
          <p class="footer-beian">
            <a
              href="https://beian.miit.gov.cn/"
              target="_blank"
              rel="noopener noreferrer"
            >桂ICP备2026014828号-1</a>
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
import { useForumBackdrop } from '../composables/useForumBackdrop.js'
import { PLATFORM_POST_INK_IMAGE } from '../data/inkTheme.js'
import { imgUrl } from '../data/profile.js'

const route = useRoute()
const { collapsed: sidebarCollapsed } = usePlatformSidebar()
const footerYear = computed(() => new Date().getFullYear())
const isAuthRoute = computed(() => route.name === 'Login' || route.name === 'Register')

const backdropUrl = imgUrl(PLATFORM_POST_INK_IMAGE)
const { blur: backdropBlur, dark: backdropDark } = useForumBackdrop()
const backdropStyle = computed(() => {
  if (!backdropUrl) return {}
  const brightness = Math.max(0, 1 - backdropDark.value / 100)
  const mask = Math.min(0.92, 0.25 + backdropDark.value / 130)
  return {
    backgroundImage: `url("${backdropUrl}")`,
    filter: `blur(${backdropBlur.value}px) saturate(1.08) brightness(${brightness})`,
    '--backdrop-mask': String(mask),
  }
})
</script>

<style scoped>
.platform-layout {
  --platform-sidebar-width: 240px;
  min-height: 100vh;
  background: var(--bg);
}

/* 统一模糊背景（爱莉固定图）+ 毛玻璃卡片 */
.platform-backdrop {
  position: fixed;
  inset: 0;
  z-index: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: blur(22px) saturate(1.08) brightness(0.55);
  transform: scale(1.12);
  opacity: 0.85;
  pointer-events: none;
  transition: filter 0.2s ease;
}

.platform-backdrop::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--bg) calc(var(--backdrop-mask, 0.45) * 70%), transparent) 0%,
    color-mix(in srgb, var(--bg) calc(var(--backdrop-mask, 0.45) * 100%), transparent) 100%
  );
}

/* 背景存在时让主内容区透出背景 */
.platform-layout:not(.platform-layout--auth) .platform-main::before {
  background: color-mix(in srgb, var(--bg-paper) 30%, transparent);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.platform-layout:not(.platform-layout--auth) :deep(.platform-panel) {
  background: color-mix(in srgb, var(--bg-paper) 62%, transparent);
  backdrop-filter: blur(14px) saturate(1.15);
  -webkit-backdrop-filter: blur(14px) saturate(1.15);
  border-color: color-mix(in srgb, var(--border) 60%, transparent);
  border-radius: 14px;
}

.platform-layout:not(.platform-layout--auth) .platform-body {
  margin-left: var(--platform-sidebar-width);
  transition: margin-left 0.22s ease;
}

.platform-layout--sidebar-collapsed:not(.platform-layout--auth) .platform-body {
  margin-left: 0;
}

.platform-body {
  position: relative;
  z-index: 1;
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

.footer-beian {
  margin: 0.65rem 0 0;
}

.footer-beian a {
  color: var(--text-muted);
  text-decoration: none;
  border-bottom: 1px solid transparent;
}

.footer-beian a:hover {
  color: var(--orange);
  border-bottom-color: color-mix(in srgb, var(--orange) 45%, transparent);
}

.platform-footer a {
  color: var(--orange);
}

.platform-footer .footer-beian a {
  color: var(--text-muted);
}

.platform-footer .footer-beian a:hover {
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

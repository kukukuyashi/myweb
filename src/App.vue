<template>
  <div v-if="showBlogBackdrop" class="blog-backdrop" :style="blogBackdropStyle" aria-hidden="true"></div>
  <PageRails v-if="!isAdminRoute && !isPlatformRoute" />
  <PlatformRails v-if="!isAdminRoute && isPlatformRoute" />
  <div class="route-stage" :class="{ 'route-stage--admin': isAdminRoute }">
    <router-view v-slot="{ Component, route }">
      <transition :name="transitionName">
        <component :is="Component" :key="route.fullPath" />
      </transition>
    </router-view>
  </div>
  <audio
    ref="globalAudioRef"
    id="cyinc-global-audio"
    preload="auto"
    tabindex="-1"
    aria-hidden="true"
    style="position:fixed;width:0;height:0;opacity:0;pointer-events:none"
  />
  <MusicPlayer v-if="showMusicPlayer" />
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import router from './router'
import { useGridSpotlight } from './composables/useRevealOnScroll'
import { useRouteTransition } from './composables/useRouteTransition'
import { useKonamiCheat } from './composables/useKonamiCheat'
import { useClickRipple } from './composables/useClickRipple'
import { useAnimatedCursor } from './composables/useAnimatedCursor'
import { initMusicEngine, useMusicPlayback } from './composables/useMusicPlayback'
import { bindGlobalAudio } from './utils/musicAudio.js'
import { PLATFORM_POST_INK_IMAGE } from './data/inkTheme.js'
import { imgUrl } from './data/profile.js'

const PageRails = defineAsyncComponent(() => import('./components/PageRails.vue'))
const PlatformRails = defineAsyncComponent(() => import('./components/PlatformRails.vue'))
const MusicPlayer = defineAsyncComponent(() => import('./components/MusicPlayer.vue'))

const route = useRoute()
const isAdminRoute = computed(() => route.name === 'NotesAdmin')
const isPlatformRoute = computed(() => route.path.startsWith('/app'))
const isAuthRoute = computed(() => route.name === 'Login' || route.name === 'Register')

/* 博客区移动端毛玻璃背景（与主站同款爱莉图，仅 CSS 在 ≤768px 显示） */
const blogBackdropUrl = imgUrl(PLATFORM_POST_INK_IMAGE)
const showBlogBackdrop = computed(() => !isAdminRoute.value && !isPlatformRoute.value)
const blogBackdropStyle = computed(() => (blogBackdropUrl ? { backgroundImage: `url("${blogBackdropUrl}")` } : {}))

/** 主站除音乐室外不挂底栏播放器，避免挡住侧边栏主题切换 */
const showMusicPlayer = computed(() => {
  if (isAdminRoute.value || isAuthRoute.value) return false
  if (isPlatformRoute.value && route.name !== 'PlatformMusic') return false
  return true
})

useGridSpotlight()
useKonamiCheat()
useClickRipple()
useAnimatedCursor()
useMusicPlayback()

const globalAudioRef = ref(null)
onMounted(() => {
  bindGlobalAudio(globalAudioRef.value)
  initMusicEngine()
})

const { transitionName } = useRouteTransition(router)
</script>

<style>
/* 博客区移动端：与主站同款毛玻璃背景 + 卡片，桌面端保持纸感风不变 */
.blog-backdrop {
  display: none;
}

@media (max-width: 768px) {
  .blog-backdrop {
    display: block;
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
  }

  .blog-backdrop::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--bg) 55%, transparent) 0%,
      color-mix(in srgb, var(--bg) 82%, transparent) 100%
    );
  }

  /* 内容层透出背景 */
  .home,
  .content-page,
  .archive,
  .about,
  .projects,
  .changelog-page,
  .guestbook,
  .tag-view {
    position: relative;
    z-index: 1;
    background: transparent !important;
  }

  body::before {
    opacity: 0.4;
  }

  /* 博客卡片毛玻璃化，对齐主站质感 */
  .featured,
  .post-card,
  .article-content,
  .hero.ink-panel,
  .about-hero--ink,
  .archive-timeline--ink {
    background: color-mix(in srgb, var(--bg-paper) 68%, transparent) !important;
    backdrop-filter: blur(14px) saturate(1.15);
    -webkit-backdrop-filter: blur(14px) saturate(1.15);
    border-color: color-mix(in srgb, var(--border) 60%, transparent) !important;
    border-radius: 14px;
  }
}

.route-stage {
  position: relative;
  min-height: calc(100vh - var(--topbar-height));
}

.route-stage--admin {
  min-height: 100vh;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

.slide-forward-enter-active,
.slide-forward-leave-active,
.slide-back-enter-active,
.slide-back-leave-active,
.slide-forward-soft-enter-active,
.slide-forward-soft-leave-active {
  transition:
    opacity 0.24s ease,
    transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
}

.slide-forward-enter-from {
  opacity: 0;
  transform: translateX(32px);
}

.slide-forward-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}

.slide-back-enter-from {
  opacity: 0;
  transform: translateX(-32px);
}

.slide-back-leave-to {
  opacity: 0;
  transform: translateX(32px);
}

.slide-forward-soft-enter-from {
  opacity: 0;
  transform: translateX(14px);
}

.slide-forward-soft-leave-to {
  opacity: 0;
  transform: translateX(-14px);
}

.slide-forward-leave-active,
.slide-back-leave-active,
.slide-forward-soft-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  z-index: 0;
  pointer-events: none;
}

.slide-forward-enter-active,
.slide-back-enter-active,
.slide-forward-soft-enter-active {
  position: relative;
  z-index: 1;
}

@media (prefers-reduced-motion: reduce) {
  .page-fade-enter-active,
  .page-fade-leave-active,
  .slide-forward-enter-active,
  .slide-forward-leave-active,
  .slide-back-enter-active,
  .slide-back-leave-active,
  .slide-forward-soft-enter-active,
  .slide-forward-soft-leave-active {
    transition: none;
  }

  .page-fade-enter-from,
  .page-fade-leave-to,
  .slide-forward-enter-from,
  .slide-forward-leave-to,
  .slide-back-enter-from,
  .slide-back-leave-to,
  .slide-forward-soft-enter-from,
  .slide-forward-soft-leave-to {
    opacity: 1;
    transform: none;
  }

  .slide-forward-leave-active,
  .slide-back-leave-active,
  .slide-forward-soft-leave-active {
    position: static;
  }
}
</style>

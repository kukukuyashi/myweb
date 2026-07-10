<template>
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

const PageRails = defineAsyncComponent(() => import('./components/PageRails.vue'))
const PlatformRails = defineAsyncComponent(() => import('./components/PlatformRails.vue'))
const MusicPlayer = defineAsyncComponent(() => import('./components/MusicPlayer.vue'))

const route = useRoute()
const isAdminRoute = computed(() => route.name === 'NotesAdmin')
const isPlatformRoute = computed(() => route.path.startsWith('/app'))
const isAuthRoute = computed(() => route.name === 'Login' || route.name === 'Register')

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

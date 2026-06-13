<template>
  <PageRails />
  <div class="route-stage">
    <router-view v-slot="{ Component, route }">
      <transition :name="transitionName">
        <component :is="Component" :key="route.fullPath" />
      </transition>
    </router-view>
  </div>
  <MusicPlayer />
</template>

<script setup>
import PageRails from './components/PageRails.vue'
import MusicPlayer from './components/MusicPlayer.vue'
import router from './router'
import { useGridSpotlight } from './composables/useRevealOnScroll'
import { useRouteTransition } from './composables/useRouteTransition'
import { useKonamiCheat } from './composables/useKonamiCheat'

useGridSpotlight()
useKonamiCheat()
const { transitionName } = useRouteTransition(router)
</script>

<style>
.route-stage {
  position: relative;
  min-height: calc(100vh - var(--topbar-height));
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

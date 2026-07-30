<template>
  <div
    class="player-spectrum"
    :class="{ 'player-spectrum--live': playing, 'player-spectrum--mini': collapsed }"
    aria-hidden="true"
  >
    <span
      v-for="i in barCount"
      :key="i"
      class="spectrum-bar"
      :style="{ '--i': i }"
    />
  </div>
</template>

<script setup>
const props = defineProps({
  playing: { type: Boolean, default: false },
  collapsed: { type: Boolean, default: false },
})

const barCount = props.collapsed ? 8 : 14
</script>

<style scoped>
.player-spectrum {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 22px;
  flex-shrink: 0;
  opacity: 0.45;
  transition: opacity 0.2s;
}

.player-spectrum--live {
  opacity: 1;
}

.player-spectrum--mini {
  height: 14px;
  gap: 1px;
}

.spectrum-bar {
  display: block;
  width: 3px;
  min-height: 3px;
  height: 5px;
  transform-origin: bottom;
  background: linear-gradient(to top, rgba(232, 93, 4, 0.55), var(--orange));
}

.player-spectrum--mini .spectrum-bar {
  width: 2px;
}

/* 仅播放时用纯 CSS 动画驱动，零每帧 JS、零重排 */
.player-spectrum--live .spectrum-bar {
  height: 21px;
  animation: spectrum-bounce 1.1s ease-in-out infinite;
  animation-delay: calc(var(--i) * -0.13s);
}

.player-spectrum--mini.player-spectrum--live .spectrum-bar {
  height: 13px;
}

@keyframes spectrum-bounce {
  0%, 100% { transform: scaleY(0.18); }
  20% { transform: scaleY(0.9); }
  40% { transform: scaleY(0.35); }
  60% { transform: scaleY(0.75); }
  80% { transform: scaleY(0.45); }
}

@media (prefers-reduced-motion: reduce) {
  .player-spectrum--live .spectrum-bar {
    animation: none;
    transform: scaleY(0.5);
  }
}
</style>
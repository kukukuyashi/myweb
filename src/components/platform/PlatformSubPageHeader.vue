<template>
  <InkRevealPanel
    tag="header"
    root-class="platform-sub-header ink-panel"
    :image="image"
    :position="position"
    :r-end="rEnd"
    :fade-direction="fadeDirection"
  >
    <p v-if="coord" class="platform-coord page-ink-coord">
      {{ coord }} · <span class="ink-hint">hover 晕染</span>
    </p>
    <slot />
  </InkRevealPanel>
</template>

<script setup>
import InkRevealPanel from '../InkRevealPanel.vue'
import { PLATFORM_FORUM_INK_IMAGE, PLATFORM_FORUM_INK_POSITION } from '../../data/inkTheme.js'

defineProps({
  coord: { type: String, default: '' },
  image: { type: String, default: PLATFORM_FORUM_INK_IMAGE },
  position: { type: String, default: PLATFORM_FORUM_INK_POSITION },
  rEnd: { type: Number, default: 112 },
  fadeDirection: { type: String, default: 'left' },
})
</script>

<style scoped>
.platform-sub-header :deep(.ink-panel__content) {
  padding: clamp(1rem, 3vw, 1.65rem);
  min-height: 120px;
}
</style>

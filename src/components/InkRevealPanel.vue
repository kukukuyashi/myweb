<template>
  <component :is="tag" :class="['ink-panel', rootClass, { 'ink-panel--bleed': bleed }]">
    <HeroInkReveal
      :key="image"
      :image="image"
      :position="position"
      :r-end="rEnd"
      :max-stamps="maxStamps"
      :fade-direction="fadeDirection"
    />
    <div class="ink-panel__content">
      <slot />
    </div>
  </component>
</template>

<script setup>
import HeroInkReveal from './HeroInkReveal.vue'

defineProps({
  tag: { type: String, default: 'section' },
  rootClass: { type: String, default: '' },
  image: { type: String, required: true },
  position: { type: String, default: '85% center' },
  rEnd: { type: Number, default: 118 },
  maxStamps: { type: Number, default: 130 },
  fadeDirection: { type: String, default: 'left' },
  bleed: { type: Boolean, default: false },
})
</script>

<template>
  <div class="platform-page container layout-single">
    <InkRevealPanel
      v-if="inkImage"
      tag="header"
      root-class="platform-page__header platform-page__header--ink ink-panel"
      :image="inkImage"
      :position="inkPosition"
      :r-end="inkREnd"
      :fade-direction="inkFadeDirection"
    >
      <div class="platform-page__header-main">
        <p v-if="coord" class="platform-coord page-ink-coord">
          {{ coord }} · <span class="ink-hint">hover 晕染</span>
        </p>
        <h1 class="platform-title">{{ title }}</h1>
        <p v-if="lead" class="platform-lead">{{ lead }}</p>
      </div>
      <div v-if="$slots.actions" class="platform-page__actions">
        <slot name="actions" />
      </div>
    </InkRevealPanel>

    <header v-else class="platform-page__header">
      <div class="platform-page__header-main">
        <p v-if="coord" class="platform-coord">{{ coord }}</p>
        <h1 class="platform-title">{{ title }}</h1>
        <p v-if="lead" class="platform-lead">{{ lead }}</p>
      </div>
      <div v-if="$slots.actions" class="platform-page__actions">
        <slot name="actions" />
      </div>
    </header>

    <slot />
  </div>
</template>

<script setup>
import InkRevealPanel from '../InkRevealPanel.vue'

defineProps({
  coord: { type: String, default: '' },
  title: { type: String, required: true },
  lead: { type: String, default: '' },
  inkImage: { type: String, default: '' },
  inkPosition: { type: String, default: '80% center' },
  inkREnd: { type: Number, default: 118 },
  inkFadeDirection: { type: String, default: 'left' },
})
</script>

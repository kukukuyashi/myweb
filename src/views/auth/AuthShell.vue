<template>
  <div class="auth-page auth-page--isolated">
    <div class="auth-page__ink" aria-hidden="true">
      <HeroInkReveal
        :image="backdropImage || panelImage"
        position="center"
        :r-end="132"
        :max-stamps="150"
        fade-direction="left"
      />
      <div class="auth-page__ink-veil" />
    </div>
    <p class="auth-page__ink-hint">hover 墨染</p>

    <div class="auth-card">
      <aside
        class="auth-card__visual"
        :style="{ backgroundImage: `url(${imgUrl(panelImage)})` }"
      >
        <div class="auth-card__visual-overlay" aria-hidden="true" />
        <div class="auth-card__visual-inner">
          <p class="auth-card__eyebrow">CYINC · PLATFORM</p>
          <h1 class="auth-card__brand-title">{{ brandTitle }}</h1>
          <p class="auth-card__brand-copy">{{ brandCopy }}</p>
          <div class="auth-card__divider" />
          <div class="auth-card__stats">
            <div v-for="stat in stats" :key="stat.label" class="auth-card__stat">
              <strong>{{ stat.value }}</strong>
              <span>{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </aside>

      <div class="auth-card__form-panel">
        <div class="auth-card__form-inner">
          <header class="auth-card__header">
            <h2 class="auth-card__title">{{ title }}</h2>
            <p v-if="subtitle" class="auth-card__subtitle">{{ subtitle }}</p>
          </header>

          <slot />

          <p v-if="$slots.switch" class="auth-card__switch">
            <slot name="switch" />
          </p>

          <p v-if="footerNote || $slots.footer" class="auth-card__footer">
            <slot name="footer">{{ footerNote }}</slot>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { imgUrl } from '../../data/profile.js'
import HeroInkReveal from '../../components/HeroInkReveal.vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  brandTitle: { type: String, default: '加入 CYINC 社区' },
  brandCopy: {
    type: String,
    default: '探索 ACG 与技术日常，逛论坛、听音乐室、记录专注 — 与同好一起创造属于我们的社区。',
  },
  panelImage: { type: String, required: true },
  backdropImage: { type: String, default: '' },
  stats: {
    type: Array,
    default: () => [
      { value: '论坛', label: '板块讨论' },
      { value: 'FLAC', label: '音乐室' },
      { value: '24/7', label: '全天在线' },
    ],
  },
  footerNote: { type: String, default: '' },
})
</script>

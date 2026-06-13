<template>
  <div class="hero-ticker" aria-hidden="true">
    <div class="hero-ticker-track">
      <span v-for="copy in 2" :key="copy" class="hero-ticker-row">
        <span v-for="(item, i) in items" :key="`${copy}-${i}`" class="hero-ticker-item">
          <span v-if="item.highlight" class="hero-ticker-highlight">{{ item.text }}</span>
          <template v-else>{{ item.text }}</template>
          <span class="hero-ticker-sep">·</span>
        </span>
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [
      { text: 'ACG' },
      { text: 'LEARNING' },
      { text: 'AGENT' },
      { text: 'NOTES' },
      { text: 'hover 晕染', highlight: true },
    ],
  },
})
</script>

<style scoped>
.hero-ticker {
  overflow: hidden;
  margin-bottom: 1rem;
  border-bottom: 1px dashed var(--border);
  padding-bottom: 0.5rem;
  mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
}

.hero-ticker-track {
  display: flex;
  width: max-content;
  animation: ticker-scroll 28s linear infinite;
}

.hero-ticker-row {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  padding-right: 2rem;
}

.hero-ticker-item {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  white-space: nowrap;
}

.hero-ticker-sep {
  margin: 0 0.65rem;
  opacity: 0.35;
}

.hero-ticker-highlight {
  color: var(--orange);
  opacity: 0.85;
}

@keyframes ticker-scroll {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

@media (prefers-reduced-motion: reduce) {
  .hero-ticker-track {
    animation: none;
    flex-wrap: wrap;
    width: auto;
  }

  .hero-ticker-row:last-child {
    display: none;
  }
}
</style>

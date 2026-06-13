<template>
  <div class="system-halt" :class="{ 'system-halt--compact': compact }" role="alert">
    <div class="system-halt-screen">
      <div class="system-halt-scanline" aria-hidden="true" />
      <div class="system-halt-top">
        <span class="system-halt-code">{{ code }}</span>
        <span v-if="status" class="system-halt-status">{{ status }}</span>
      </div>
      <h2 class="system-halt-head">{{ headline }}</h2>
      <p class="system-halt-msg">{{ message }}</p>
      <ul v-if="lines.length" class="system-halt-log">
        <li v-for="(line, i) in lines" :key="i">{{ line }}</li>
      </ul>
      <slot />
      <router-link v-if="homeLink" to="/" class="system-halt-link">{{ homeLabel }}</router-link>
    </div>
  </div>
</template>

<script setup>
defineProps({
  code: { type: String, default: '404' },
  headline: { type: String, default: 'SYSTEM HALTED' },
  message: { type: String, default: '请求的资源无法定位。' },
  status: { type: String, default: 'FAULT' },
  lines: { type: Array, default: () => [] },
  compact: { type: Boolean, default: false },
  homeLink: { type: Boolean, default: true },
  homeLabel: { type: String, default: '← RETURN TO INDEX' },
})
</script>

<style scoped>
.system-halt {
  margin: 1.5rem 0;
}

.system-halt--compact {
  margin: 0;
}

.system-halt-screen {
  position: relative;
  overflow: hidden;
  padding: 1.75rem 1.5rem;
  background: var(--topbar-bg);
  color: rgba(255, 255, 255, 0.88);
  border: 1px solid var(--border);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%);
}

[data-theme="dark"] .system-halt-screen {
  background: #0d0d0d;
}

.system-halt-scanline {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    transparent 0,
    transparent 3px,
    rgba(255, 255, 255, 0.03) 3px,
    rgba(255, 255, 255, 0.03) 4px
  );
  animation: halt-scan 9s linear infinite;
}

@keyframes halt-scan {
  from { background-position: 0 0; }
  to { background-position: 0 100px; }
}

.system-halt-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
}

.system-halt-code {
  color: var(--orange);
  font-size: 1.35rem;
  font-weight: 500;
  line-height: 1;
}

.system-halt--compact .system-halt-code {
  font-size: 1rem;
}

.system-halt-status {
  color: rgba(255, 255, 255, 0.45);
  animation: halt-blink 1.15s step-end infinite;
}

.system-halt-head {
  font-family: var(--mono);
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.18em;
  color: #fff;
  margin: 0 0 0.65rem;
  animation: halt-blink 1.15s step-end infinite;
}

.system-halt--compact .system-halt-head {
  font-size: 0.82rem;
  letter-spacing: 0.14em;
}

.system-halt-msg {
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.72);
  margin: 0 0 1rem;
  line-height: 1.5;
}

.system-halt--compact .system-halt-msg {
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
}

.system-halt-log {
  list-style: none;
  margin: 0 0 1.15rem;
  padding: 0.75rem 0.85rem;
  background: rgba(0, 0, 0, 0.35);
  border: 1px dashed rgba(255, 255, 255, 0.12);
  font-family: var(--mono);
  font-size: 0.68rem;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.55);
}

.system-halt-log li::before {
  content: '› ';
  color: var(--orange);
}

.system-halt-link {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  color: var(--orange);
  text-decoration: none;
  border: 1px solid rgba(232, 93, 4, 0.35);
  padding: 0.35rem 0.65rem;
  transition: background 0.15s, color 0.15s;
}

.system-halt-link:hover {
  background: var(--orange);
  color: #fff;
}

@keyframes halt-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.38; }
}

@media (prefers-reduced-motion: reduce) {
  .system-halt-head,
  .system-halt-status {
    animation: none;
  }

  .system-halt-scanline {
    animation: none;
  }
}
</style>

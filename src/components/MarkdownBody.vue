<template>
  <div class="md-body prose" v-html="html" />
</template>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '../utils/markdown.js'

const props = defineProps({
  content: { type: String, default: '' },
})

const html = computed(() => renderMarkdown(props.content))
</script>

<style scoped>
.md-body :deep(h1),
.md-body :deep(h2),
.md-body :deep(h3) {
  margin: 1.25em 0 0.5em;
  line-height: 1.3;
}

.md-body :deep(h1) { font-size: 1.35rem; }
.md-body :deep(h2) { font-size: 1.15rem; }
.md-body :deep(h3) { font-size: 1rem; }

.md-body :deep(p) {
  margin: 0.65em 0;
  line-height: 1.7;
}

.md-body :deep(ul),
.md-body :deep(ol) {
  margin: 0.65em 0;
  padding-left: 1.4em;
}

.md-body :deep(blockquote) {
  margin: 0.75em 0;
  padding-left: 0.85em;
  border-left: 3px solid var(--orange, #e85d04);
  color: var(--text-muted, #666);
}

.md-body :deep(code) {
  font-family: var(--mono, monospace);
  font-size: 0.88em;
  background: rgba(0, 0, 0, 0.05);
  padding: 0.12em 0.35em;
  border-radius: 3px;
}

.md-body :deep(pre) {
  overflow-x: auto;
  padding: 0.85em 1em;
  background: #1e1e1e;
  color: #f5f5f5;
  border-radius: 4px;
  font-size: 0.85rem;
}

.md-body :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}

.md-body :deep(a) {
  color: var(--orange, #e85d04);
}

.md-body :deep(img) {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1em auto;
  border-radius: 8px;
  border: 1px solid var(--border, #ddd);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.md-body :deep(figure) {
  margin: 1.1em 0;
  text-align: center;
}

.md-body :deep(figcaption) {
  margin-top: 0.4em;
  font-size: 0.8rem;
  color: var(--text-muted, #666);
}

.md-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border, #ddd);
  margin: 1.25em 0;
}
</style>

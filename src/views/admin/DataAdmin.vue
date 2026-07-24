<template>
  <div class="data-admin">
    <div class="data-hint platform-panel">
      <span>数据管理由 SQLAdmin 提供（用户 / 文章 / 论坛 / 留言）。已通过统一登录，无需再次登录。</span>
      <a class="platform-btn-ghost" href="/admin" target="_blank" rel="noopener">新标签打开 ↗</a>
    </div>
    <div class="frame-wrap platform-panel">
      <iframe ref="frame" class="data-frame" src="/admin" title="数据管理" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const frame = ref(null)
</script>

<style scoped>
.data-admin { display: flex; flex-direction: column; gap: 0.85rem; height: 100%; }
.data-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  color: var(--text-muted);
  font-size: 0.88rem;
  padding: 0.75rem 1rem;
}
.frame-wrap { padding: 0; overflow: hidden; flex: 1; }
.data-frame {
  width: 100%;
  height: calc(100vh - 220px);
  min-height: 520px;
  border: 0;
  display: block;
  background: #fff;
  border-radius: 12px;
}
</style>
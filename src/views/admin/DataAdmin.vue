<template>
  <div class="data-admin">
    <div class="data-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.slug"
        type="button"
        class="data-tab"
        :class="{ active: activeSlug === tab.slug }"
        @click="activeSlug = tab.slug"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
      <div class="data-tabs-tail">
        <a class="platform-btn-ghost" :href="currentUrl" target="_blank" rel="noopener">新标签打开 ↗</a>
      </div>
    </div>

    <div class="frame-wrap platform-panel" @mouseenter="onEnterFrame" @mouseleave="onLeaveFrame">
      <iframe :key="activeSlug" :src="currentUrl" class="data-frame" title="数据管理" />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'

const tabs = [
  { slug: 'user', label: '用户', icon: '👤' },
  { slug: 'post', label: '博客文章', icon: '📝' },
  { slug: 'forum-category', label: '论坛板块', icon: '📁' },
  { slug: 'forum-thread', label: '论坛帖子', icon: '💬' },
  { slug: 'forum-reply', label: '论坛回复', icon: '↩' },
  { slug: 'qa-message', label: '留言板', icon: '✉' },
]

const activeSlug = ref(tabs[0].slug)
const currentUrl = computed(() => `/admin/${activeSlug.value}/list`)

/** 鼠标进入 iframe 时，主站的 canvas 动画光标会因无法监听 iframe 内 mousemove 而“卡在原地”。
 *  这里给 html 加一个类：父页 CSS 会临时隐藏 canvas；iframe 内部通过自身 CSS 显示 GIF 光标。 */
function onEnterFrame() {
  document.documentElement.classList.add('cursor-hide-in-frame')
}
function onLeaveFrame() {
  document.documentElement.classList.remove('cursor-hide-in-frame')
}
onBeforeUnmount(() => onLeaveFrame())
</script>

<style scoped>
.data-admin {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  height: 100%;
}

.data-tabs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.65rem;
  border: 1px solid color-mix(in srgb, var(--border) 55%, transparent);
  border-radius: 12px;
  background: color-mix(in srgb, var(--bg-paper) 78%, transparent);
  backdrop-filter: blur(10px) saturate(1.1);
  -webkit-backdrop-filter: blur(10px) saturate(1.1);
}

.data-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid transparent;
  border-radius: 999px;
  background: transparent;
  color: var(--text);
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.data-tab:hover { background: color-mix(in srgb, var(--text) 6%, transparent); }
.data-tab.active {
  background: color-mix(in srgb, var(--primary-color) 14%, transparent);
  color: var(--primary-color);
  border-color: color-mix(in srgb, var(--primary-color) 40%, transparent);
  font-weight: 600;
}

.tab-icon { font-size: 1rem; }
.data-tabs-tail { margin-left: auto; display: flex; align-items: center; }

.frame-wrap {
  padding: 0;
  overflow: hidden;
  flex: 1;
  border-radius: 14px;
  min-height: 640px;
}

.data-frame {
  width: 100%;
  height: calc(100vh - 200px);
  min-height: 620px;
  border: 0;
  display: block;
  background: #fff;
  border-radius: 14px;
}
</style>

<style>
/* 全局：鼠标位于 iframe 内时隐藏父页的 canvas 动画光标，避免残影卡住 */
html.cursor-hide-in-frame .animated-cursor { visibility: hidden !important; }
</style>
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
        <a class="platform-btn-ghost" href="/admin" target="_blank" rel="noopener">高级 / SQLAdmin ↗</a>
      </div>
    </div>

    <AdminTable
      v-if="active"
      :key="active.slug"
      :resource="active.resource"
      :columns="active.columns"
      :field-types="active.fieldTypes"
      :default-sort="active.defaultSort || '-id'"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'

const tabs = [
  {
    slug: 'users',
    resource: 'users',
    label: '用户',
    icon: '👤',
    defaultSort: '-id',
    columns: [
      { field: 'id', label: 'ID' },
      { field: 'username', label: '用户名', searchable: true },
      { field: 'email', label: '邮箱', searchable: true },
      { field: 'nickname', label: '昵称', searchable: true },
      { field: 'level', label: '等级' },
      { field: 'xp', label: '经验' },
      { field: 'checkin_streak', label: '连续签到' },
      { field: 'created_at', label: '注册时间' },
    ],
    fieldTypes: {
      level: 'number',
      xp: 'number',
      checkin_streak: 'number',
      last_checkin_date: 'date',
    },
  },
  {
    slug: 'threads',
    resource: 'threads',
    label: '论坛帖子',
    icon: '💬',
    defaultSort: '-id',
    columns: [
      { field: 'id', label: 'ID' },
      { field: 'category_id', label: '板块 ID' },
      { field: 'user_id', label: '作者 ID' },
      { field: 'title', label: '标题', searchable: true },
      { field: 'reply_count', label: '回复' },
      { field: 'view_count', label: '浏览' },
      { field: 'like_count', label: '点赞' },
      { field: 'is_pinned', label: '置顶' },
      { field: 'is_featured', label: '精选' },
      { field: 'created_at', label: '创建时间' },
    ],
    fieldTypes: {
      content: 'textarea',
      category_id: 'number',
      is_pinned: 'boolean',
      is_locked: 'boolean',
      is_featured: 'boolean',
      featured_order: 'number',
      view_count: 'number',
      like_count: 'number',
      share_count: 'number',
    },
  },
  {
    slug: 'replies',
    resource: 'replies',
    label: '论坛回复',
    icon: '↩',
    defaultSort: '-id',
    columns: [
      { field: 'id', label: 'ID' },
      { field: 'thread_id', label: '帖子 ID' },
      { field: 'user_id', label: '作者 ID' },
      { field: 'content', label: '内容', searchable: true },
      { field: 'like_count', label: '点赞' },
      { field: 'created_at', label: '创建时间' },
    ],
    fieldTypes: {
      content: 'textarea',
    },
  },
  {
    slug: 'qa',
    resource: 'qa',
    label: '留言板',
    icon: '✉',
    defaultSort: '-id',
    columns: [
      { field: 'id', label: 'ID' },
      { field: 'name', label: '昵称', searchable: true },
      { field: 'content', label: '内容', searchable: true },
      { field: 'created_at', label: '时间' },
    ],
    fieldTypes: {
      content: 'textarea',
    },
  },
]

const activeSlug = ref(tabs[0].slug)
const active = computed(() => tabs.find((t) => t.slug === activeSlug.value))
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

.data-tab:hover {
  background: color-mix(in srgb, var(--text) 6%, transparent);
}

.data-tab.active {
  background: color-mix(in srgb, var(--primary-color) 14%, transparent);
  color: var(--primary-color);
  border-color: color-mix(in srgb, var(--primary-color) 40%, transparent);
  font-weight: 600;
}

.tab-icon {
  font-size: 1rem;
}

.data-tabs-tail {
  margin-left: auto;
  display: flex;
  align-items: center;
}
</style>
<template>
  <aside class="blog-aside">
    <div class="panel">
      <div class="panel-header">About</div>
      <div class="panel-body">
        <p>前端开发者，正在学 Agent 与 LLM 应用。</p>
        <div class="skill-tags">
          <span>Vue</span>
          <span>Agent</span>
          <span>LLM</span>
          <span>Python</span>
          <span>Node.js</span>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">Now Learning</div>
      <div class="panel-body">
        <ul class="learning-list">
          <li v-for="item in learningItems" :key="item">
            <span class="learning-dot"></span>{{ item }}
          </li>
        </ul>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">Stats</div>
      <div class="panel-body">
        <div class="stats-row">
          <span class="stats-key">Articles</span>
          <span class="stats-val">{{ totalPosts }}</span>
        </div>
        <div class="stats-row">
          <span class="stats-key">Categories</span>
          <span class="stats-val">{{ totalCategories }}</span>
        </div>
        <div class="stats-row">
          <span class="stats-key">Online</span>
          <span class="stats-val">{{ siteAge }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  totalPosts: { type: [Number, String], default: 0 },
  totalCategories: { type: [Number, String], default: 0 },
  totalTags: { type: [Number, String], default: 0 },
  siteAge: { type: String, default: '—' }
})

const learningItems = [
  'AI Agent 架构',
  'Prompt / Tool Use',
  'RAG 与知识库',
  'Cursor / SDK 实践'
]
</script>

<style scoped>
.learning-list {
  list-style: none;
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--text-muted);
}

.learning-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--border);
}

.learning-list li:last-child { border-bottom: none; }

.learning-dot {
  width: 5px;
  height: 5px;
  background: var(--orange);
  flex-shrink: 0;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--border);
  font-family: var(--mono);
  font-size: 0.7rem;
}

.stats-row:last-child { border-bottom: none; }

.stats-key {
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stats-val {
  color: var(--steel);
  font-weight: 500;
}
</style>

<template>
  <aside class="blog-aside">
    <div class="panel">
      <div class="panel-header">Profile</div>
      <div class="panel-body">
        <ProfileCard />
      </div>
    </div>

    <MomentPanel :total-posts="totalPosts" :site-age="siteAge" />

    <div class="panel">
      <div class="panel-header">最近更新</div>
      <div class="panel-body">
        <ul class="recent-list">
          <li v-for="post in recentPosts" :key="post.id">
            <router-link :to="post.url">{{ post.title }}</router-link>
            <span class="recent-date">{{ post.date }}</span>
          </li>
        </ul>
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

    <VisitorLcd />

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
          <span class="stats-key">Tags</span>
          <span class="stats-val">{{ totalTags }}</span>
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
import ProfileCard from './ProfileCard.vue'
import MomentPanel from './MomentPanel.vue'
import VisitorLcd from './VisitorLcd.vue'
import { getRecentPosts } from '../data/posts'

const recentPosts = getRecentPosts(3)

defineProps({
  totalPosts: { type: [Number, String], default: 0 },
  totalCategories: { type: [Number, String], default: 0 },
  totalTags: { type: [Number, String], default: 0 },
  siteAge: { type: String, default: '—' }
})

const learningItems = [
  'AI Agent 架构',
  'MyGO!!!!! / 碧蓝档案',
  'Prompt / Tool Use',
  'Cursor / SDK 实践'
]
</script>

<style scoped>
.recent-list {
  list-style: none;
}

.recent-list li {
  padding: 0.45rem 0;
  border-bottom: 1px solid var(--border);
}

.recent-list li:last-child {
  border-bottom: none;
}

.recent-list a {
  display: block;
  font-size: 0.78rem;
  line-height: 1.4;
  color: var(--text);
  text-decoration: none;
  margin-bottom: 0.2rem;
}

.recent-list a:hover {
  color: var(--orange);
}

.recent-date {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}

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

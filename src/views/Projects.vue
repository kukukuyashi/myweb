<template>
  <div class="projects">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <header class="projects-header">
            <p class="page-ink-coord">PROJECTS · WORKS · <span class="ink-hint">实战复盘</span></p>
            <h1 class="page-title">项目</h1>
            <p class="projects-lead">
              不只有笔记 — 这些是真正跑过、写过、踩过坑的东西。详细过程见对应文章。
            </p>
          </header>

          <div class="projects-grid">
            <article
              v-for="project in projectList"
              :key="project.slug"
              class="project-card"
              :class="{ 'project-card--active': project.status === 'active' }"
            >
              <div class="project-card-top">
                <span class="project-status">{{ statusLabel(project.status) }}</span>
                <span class="project-slug">{{ project.slug }}</span>
              </div>
              <h2 class="project-title">{{ project.title }}</h2>
              <p class="project-sub">{{ project.subtitle }}</p>
              <p class="project-desc">{{ project.description }}</p>
              <div class="project-stack">
                <span v-for="tech in project.stack" :key="tech" class="project-tech">{{ tech }}</span>
              </div>
              <div class="project-links">
                <router-link v-if="project.postId" :to="postLink(project.postId)" class="project-link">
                  读笔记 →
                </router-link>
                <a v-if="project.demo" :href="project.demo" target="_blank" rel="noopener" class="project-link">
                  在线预览 ↗
                </a>
                <a v-if="project.repo" :href="project.repo" target="_blank" rel="noopener" class="project-link">
                  GitHub ↗
                </a>
              </div>
            </article>
          </div>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import { usePageMeta } from '../composables/usePageMeta'
import { getProjects } from '../data/projects'
import { postUrl } from '../data/posts'

usePageMeta({
  title: '项目',
  description: 'Cyinc 的项目与实战复盘：个人博客、AI 鉴陈等。',
})

const projectList = getProjects()

function postLink(id) {
  return postUrl(id)
}

function statusLabel(status) {
  if (status === 'active') return 'ACTIVE'
  if (status === 'archive') return 'ARCHIVE'
  return status.toUpperCase()
}
</script>

<style scoped>
.projects-header {
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px dashed var(--border);
}

.projects-lead {
  margin-top: 0.75rem;
  max-width: 42rem;
  color: var(--text-muted);
  line-height: 1.55;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.project-card {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  padding: 1.25rem 1.35rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: border-color 0.15s, transform 0.15s;
}

.project-card:hover {
  border-color: var(--orange);
  transform: translateY(-2px);
}

.project-card--active {
  border-top: 3px solid var(--orange);
}

.project-card-top {
  display: flex;
  justify-content: space-between;
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.project-status {
  color: var(--orange);
}

.project-title {
  font-size: 1.15rem;
  margin: 0;
  line-height: 1.3;
}

.project-sub {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--steel);
  margin: 0;
}

.project-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0.25rem 0 0.5rem;
  flex: 1;
}

.project-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
}

.project-tech {
  font-family: var(--mono);
  font-size: 0.58rem;
  padding: 0.15rem 0.4rem;
  border: 1px solid var(--border);
  color: var(--text-muted);
  letter-spacing: 0.03em;
}

.project-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
  padding-top: 0.65rem;
  border-top: 1px dashed var(--border);
}

.project-link {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--steel);
  text-decoration: none;
  letter-spacing: 0.04em;
}

.project-link:hover {
  color: var(--orange);
  text-decoration: underline;
  text-underline-offset: 2px;
}
</style>

<template>
  <div class="about">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single about-layout">
        <div class="page-content">
          <section class="about-hero">
            <div class="about-hero-main">
              <div class="acg-frame acg-frame--profile">
                <img :src="avatarUrl" :alt="profile.name" width="140" height="140">
                <span class="frame-label">ID · CYINC</span>
              </div>
              <div class="about-intro">
                <h1 class="page-title about-name">{{ profile.name }}</h1>
                <p class="about-tagline">{{ profile.tagline }}</p>
                <div class="acg-chips about-chips">
                  <span v-for="t in profile.acgTags" :key="t" class="acg-chip">{{ t }}</span>
                </div>
              </div>
            </div>
            <p class="about-lead">
              这个站既是<strong>技术笔记本</strong>，也是<strong>ACG 爱好者的自留地</strong>。
              笔记可以查，音乐室可以听，留言板可以聊 — 不必把爱好和技术分开。
            </p>
          </section>

          <section class="about-block">
            <h2>我是谁</h2>
            <p>
              叫我 Cyinc 就好。平时写 Vue / Java / Agent 相关的东西，私下是重度 ACG 用户：
              追番、囤 OST、看 MAD，音乐室里那几首就是真实歌单。
            </p>
            <p>
              博客最初是前端学习草稿本，后来加了 Agent 笔记、Twikoo 留言板、音乐播放器。
              风格刻意做成「工业蓝图」的样子 — 但人格不用跟着变冷，ACG 图会放在<strong>档案框</strong>里，像贴纸墙一样，不破坏整体版式。
            </p>
          </section>

          <section class="about-block">
            <h2>现在在做什么</h2>
            <ul class="about-list">
              <li v-for="item in profile.favorites" :key="item.label">
                <span class="list-key">{{ item.label }}</span>
                {{ item.text }}
              </li>
            </ul>
            <blockquote>写下来，才算真正学过一遍 — 番剧观后感也算。</blockquote>
          </section>

          <section class="about-block">
            <h2>技术栈</h2>
            <div class="skill-tags">
              <span>Vue / JS</span>
              <span>Agent / LLM</span>
              <span>Python</span>
              <span>Node.js</span>
              <span>Java</span>
              <span>PHP</span>
              <span>Twikoo</span>
            </div>
          </section>

          <section class="about-block">
            <h2>贴纸墙 / 收藏</h2>
            <p class="gallery-note">
              图片统一加「档案框」处理：硬边框 + 切角 + 悬停才恢复饱和，和站点工业风共存，不会突然变成粉色博客。
            </p>
            <div class="gallery-grid">
              <figure
                v-for="item in profile.gallery"
                :key="item.path"
                class="gallery-item"
              >
                <div class="acg-frame acg-frame--gallery">
                  <img
                    :src="imgUrl(item.path)"
                    :alt="item.caption"
                    loading="lazy"
                  >
                </div>
                <figcaption>{{ item.caption }}</figcaption>
              </figure>
            </div>
          </section>

          <section class="about-block">
            <h2>联系方式</h2>
            <p>📧 邮箱：<a :href="`mailto:${profile.email}`">{{ profile.email }}</a></p>
            <p>🌐 博客：<a :href="profile.blog">{{ profile.blog }}</a></p>
            <p>💻 GitHub：<a :href="profile.github" target="_blank" rel="noopener">{{ profile.github }}</a></p>
            <p>🎵 音乐室：<router-link to="/music">/music</router-link></p>
          </section>
        </div>
      </div>
    </main>
    <SiteFooter />
    <MusicPlayer />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { usePageMeta } from '../composables/usePageMeta'
import { profile, imgUrl } from '../data/profile'

usePageMeta({
  title: '关于我',
  description: 'Cyinc — 前端与 Agent 学习者，ACG 爱好者。技术笔记 + 音乐室 + 贴纸墙。',
  image: imgUrl(profile.avatar),
})

const avatarUrl = computed(() => imgUrl(profile.avatar))
</script>

<style scoped>
.about-layout {
  max-width: 900px;
}

.about-hero {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px dashed var(--border);
}

.about-hero-main {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.about-name {
  margin-bottom: 0.35rem;
}

.about-tagline {
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.55;
  margin-bottom: 0.75rem;
}

.about-chips {
  gap: 0.35rem;
}

.about-lead {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.65;
  padding: 1rem 1.25rem;
  background: var(--orange-light);
  border-left: 3px solid var(--orange);
}

.about-block {
  margin-bottom: 2.25rem;
}

.about-block h2 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--border);
}

.about-block p {
  margin-bottom: 0.75rem;
  line-height: 1.65;
}

.about-list {
  list-style: none;
  margin-bottom: 1rem;
}

.about-list li {
  padding: 0.5rem 0;
  border-bottom: 1px dashed var(--border);
  font-size: 0.9rem;
}

.list-key {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
  text-transform: uppercase;
  display: inline-block;
  min-width: 5rem;
  margin-right: 0.5rem;
}

.gallery-note {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}

.gallery-item figcaption {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
  text-align: center;
}

@media (max-width: 560px) {
  .about-hero-main {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .about-chips {
    justify-content: center;
  }
}
</style>

<template>
  <div class="about">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single about-layout">
        <div class="page-content">
          <InkRevealPanel
            tag="section"
            root-class="about-hero about-hero--ink"
            image="img/关于/Fp6MHMdaEAA806l.jfif"
            position="78% center"
            :r-end="122"
            fade-direction="left"
          >
            <div class="about-hero-main">
              <div class="acg-frame acg-frame--profile">
                <img :src="avatarUrl" :alt="profile.name" width="140" height="140" loading="lazy">
                <span class="frame-label">ID · CYINC</span>
              </div>
              <div class="about-intro">
                <p class="page-ink-coord">PROFILE · ACG · <span class="ink-hint">hover 晕染</span></p>
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
          </InkRevealPanel>

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
            <h2>贴纸墙</h2>
            <StickerWall :items="aboutGallery" />
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
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import StickerWall from '../components/StickerWall.vue'
import InkRevealPanel from '../components/InkRevealPanel.vue'
import { usePageMeta } from '../composables/usePageMeta'
import { profile, imgUrl } from '../data/profile'
import { aboutGallery } from '../data/aboutGallery'

usePageMeta({
  title: '关于我',
  description: 'Cyinc — 前端与 Agent 学习者，ACG 爱好者。技术笔记 + 音乐室 + 贴纸墙。',
  image: imgUrl(profile.avatar),
})

const avatarUrl = computed(() => imgUrl(profile.avatar))
</script>

<style scoped>
.about-hero--ink {
  /* ink panel 样式见 main.css */
}

.about-hero:not(.about-hero--ink) {
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

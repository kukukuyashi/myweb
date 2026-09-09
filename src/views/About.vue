<template>
  <div class="about">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single about-layout">
        <div class="page-content">
          <InkRevealPanel
            tag="section"
            root-class="about-hero about-hero--ink"
            :image="heroImageUrl"
            position="78% center"
            :r-end="122"
            fade-direction="left"
          >
            <div class="about-hero-main">
              <div class="acg-frame acg-frame--profile">
                <img :src="avatarUrl" :alt="aboutContent.name" width="140" height="140" loading="lazy">
                <span class="frame-label">ID · CYINC</span>
              </div>
              <div class="about-intro">
                <p class="page-ink-coord">PROFILE · ACG · <span class="ink-hint">hover 晕染</span></p>
                <h1 class="page-title about-name">{{ aboutContent.name }}</h1>
                <p class="about-tagline">{{ aboutContent.tagline }}</p>
                <div class="acg-chips about-chips">
                  <span v-for="t in aboutContent.acgTags" :key="t" class="acg-chip">{{ t }}</span>
                </div>
              </div>
            </div>
            <p class="about-lead">{{ aboutContent.lead }}</p>
          </InkRevealPanel>

          <section class="about-block">
            <h2>我是谁</h2>
            <p v-for="paragraph in aboutContent.whoIAm" :key="paragraph">{{ paragraph }}</p>
          </section>

          <section class="about-block">
            <h2>现在在做什么</h2>
            <ul class="about-list">
              <li v-for="item in aboutContent.favorites" :key="item.label">
                <span class="list-key">{{ item.label }}</span>
                {{ item.text }}
              </li>
            </ul>
            <blockquote>{{ aboutContent.quote }}</blockquote>
          </section>

          <section class="about-block">
            <h2>技术栈</h2>
            <div class="skill-tags">
              <span v-for="skill in aboutContent.skills" :key="skill">{{ skill }}</span>
            </div>
          </section>

          <section class="about-block">
            <h2>贴纸墙</h2>
            <StickerWall :items="aboutContent.stickers" />
          </section>

          <section class="about-block">
            <h2>联系方式</h2>
            <p>📧 邮箱：<a :href="`mailto:${aboutContent.contacts.email}`">{{ aboutContent.contacts.email }}</a></p>
            <p>🌐 博客：<a :href="aboutContent.contacts.blog">{{ aboutContent.contacts.blog }}</a></p>
            <p>💻 GitHub：<a :href="aboutContent.contacts.github" target="_blank" rel="noopener">{{ aboutContent.contacts.github }}</a></p>
            <p>🎵 音乐室：<router-link :to="aboutContent.contacts.musicPath">{{ aboutContent.contacts.musicPath }}</router-link></p>
          </section>

          <section class="about-block">
            <h2>友链</h2>
            <div class="friend-grid">
              <a
                v-for="link in friendLinks"
                :key="link.url"
                :href="link.url"
                target="_blank"
                rel="noopener"
                class="friend-card"
              >
                <span class="friend-name">{{ link.name }}</span>
                <span class="friend-desc">{{ link.desc }}</span>
              </a>
            </div>
            <button type="button" class="about-friend-teleport" @click="teleportRandom">
              随机传送 →
            </button>
          </section>
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import InkRevealPanel from '../components/InkRevealPanel.vue'
import { usePageMeta } from '../composables/usePageMeta'
import { imgUrl } from '../data/profile'
import { friendLinks as defaultFriendLinks } from '../data/social'
import { defaultAboutContent, cloneSitePageContent } from '../data/sitePageDefaults'
import { fetchSitePage } from '../api/sitePages'
import { fetchFriendLinksPublic } from '../api/friendLinks'

const StickerWall = defineAsyncComponent(() => import('../components/StickerWall.vue'))

const aboutContent = ref(cloneSitePageContent(defaultAboutContent))
const friendLinks = ref([...defaultFriendLinks])

function teleportRandom() {
  const pool = friendLinks.value.filter((link) => !link.url.includes('kukukuyashi.github.io'))
  const source = pool.length ? pool : friendLinks.value
  const link = source[Math.floor(Math.random() * source.length)]
  if (link) window.open(link.url, '_blank', 'noopener')
}

usePageMeta({
  title: '关于我',
  description: 'Cyinc — 前端与 Agent 学习者，ACG 爱好者。技术笔记 + 音乐室 + 贴纸墙。',
  image: imgUrl(aboutContent.value.avatar),
})

const heroImageUrl = computed(() => imgUrl(aboutContent.value.heroImage))
const avatarUrl = computed(() => imgUrl(aboutContent.value.avatar))

onMounted(async () => {
  try {
    const data = await fetchSitePage('about')
    if (data?.content) {
      aboutContent.value = {
        ...cloneSitePageContent(defaultAboutContent),
        ...data.content,
      }
    }
  } catch {
  }

  try {
    const data = await fetchFriendLinksPublic()
    if (data?.links?.length) {
      friendLinks.value = data.links.map((link) => ({
        name: link.name,
        url: link.url,
        desc: link.description || link.desc || '',
      }))
    }
  } catch {
  }
})
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

.friend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.friend-card {
  display: grid;
  gap: 0.2rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.friend-card:hover {
  border-color: var(--orange);
  box-shadow: 0 3px 0 var(--orange);
}

.friend-name {
  font-weight: 600;
  font-size: 0.92rem;
}

.friend-desc {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.about-friend-teleport {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: inherit;
  cursor: pointer;
}

.about-friend-teleport:hover {
  border-color: var(--orange);
  color: var(--orange);
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


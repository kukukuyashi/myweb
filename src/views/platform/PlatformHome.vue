<template>
  <div ref="homeRef" class="platform-home container">
    <PlatformOnboarding />
    <InkRevealPanel
      tag="section"
      root-class="platform-hero platform-hero--ink"
      :image="platformHeroInk"
      position="72% center"
      :r-end="120"
      fade-direction="left"
    >
      <div class="hero-coord-overlay" aria-hidden="true" />
      <HeroTicker :items="platformHeroTicker" />
      <p class="welcome-eyebrow">欢迎来到</p>
      <h1 class="hero-title">
        CYINC 主站
        <span class="hero-title-sub">&gt; PLATFORM &lt;</span>
      </h1>
      <p class="welcome-guest">
        我不知道你从哪找到这里的，<br>但你确实找到主站了。
      </p>

      <div class="hero-cta-row">
        <router-link to="/app/pomo" class="btn-primary">番茄钟</router-link>
        <a href="#guestboard" class="btn-ghost" @click.prevent="scrollToSection('guestboard')">留言板</a>
        <router-link to="/" class="btn-ghost">博客</router-link>
        <router-link to="/app/me" class="btn-ghost">{{ token ? '个人中心' : '登录' }}</router-link>
        <button type="button" class="btn-ghost" @click="openOnboarding">新手指引</button>
      </div>

      <div class="hero-split">
        <div class="hero-copy">
          <div class="hero-main compact">
            <div class="acg-frame acg-frame--profile">
              <img
                :src="heroAvatarSrc"
                :alt="siteProfile.name"
                width="100"
                height="100"
                loading="eager"
              >
              <span class="frame-label">CYINC</span>
            </div>
            <div class="hero-intro">
              <p class="hero-tagline">{{ welcomeSubtitle }}</p>
              <div class="acg-chips hero-chips">
                <span v-for="t in heroTags" :key="t" class="acg-chip">{{ t }}</span>
              </div>
            </div>
          </div>
        </div>

        <figure class="hero-portrait">
          <div class="acg-frame acg-frame--portrait">
            <img
              :src="thumbUrl(platformPortrait)"
              alt="立绘"
              loading="lazy"
              decoding="async"
              @error="onThumbError($event, platformPortrait)"
            >
          </div>
          <figcaption>ARCHIVE · img/BA</figcaption>
        </figure>
      </div>
    </InkRevealPanel>

    <div class="platform-home-grid">
      <div class="platform-home-main">
        <nav class="section-nav section-nav--mobile reveal-item" data-reveal aria-label="页内分区">
          <a
            v-for="item in platformSectionNav"
            :key="item.id"
            :href="`#${item.id}`"
            class="section-nav-link"
            @click.prevent="scrollToSection(item.id)"
          >
            {{ item.label }}
          </a>
        </nav>

    <!-- 简介 -->
    <section id="intro" class="section-block ink-panel reveal-item" data-reveal>
      <header class="section-header">
        <h2 class="section-title">简介</h2>
        <p class="section-sub">PROFILE · CYINC PLATFORM</p>
      </header>

      <div class="intro-body">
        <div class="intro-text">
          <p>
            幸识～这里是 <strong>Cyinc</strong> 的主站入口 (｢･ω･)｢
            博客写技术日志，番茄钟记录专注，留言板可以随便聊聊。
          </p>
        </div>
        <ul class="attr-grid">
          <li v-for="row in platformSiteAttrs" :key="row.key">
            <span class="attr-key">{{ row.key }}</span>
            <span class="attr-val">{{ row.value }}</span>
          </li>
        </ul>
      </div>

      <div class="timeline">
        <h3 class="timeline-head">平台时间线</h3>
        <ol class="timeline-list">
          <li v-for="(ev, idx) in platformTimeline" :key="idx">
            <time>{{ ev.date }}</time>
            <span>{{ ev.text }}</span>
          </li>
        </ol>
      </div>
    </section>

    <!-- 档案 / 资源站 -->
    <section id="archive" class="section-block ink-panel reveal-item" data-reveal>
      <header class="section-header">
        <h2 class="section-title">档案 / 图床</h2>
        <p class="section-sub">img/BA · 点击预览大图</p>
      </header>
      <p class="section-lead">
        碧蓝档案与其它 ACG 收藏，点击可预览大图。
      </p>
      <BaStripCarousel :items="platformBaStrip" @select="openLightbox" />
      <p class="archive-note">※ 以上图片仅供个人收藏展示，路径位于 <code>img/BA/</code></p>
    </section>

    <!-- 留言板 -->
    <section id="guestboard" class="section-block ink-panel reveal-item" data-reveal>
      <header class="section-header">
        <h2 class="section-title">留言板</h2>
        <p class="section-sub">GUESTBOOK</p>
      </header>
      <p class="section-lead">
        友人A：这里可以留言吗？<br>可以，随便写点什么～
      </p>

      <form class="guestboard-form" @submit.prevent="submitQa">
        <div class="guestboard-form-row">
          <input v-model="qaName" type="text" maxlength="50" placeholder="昵称（可选）" class="guestboard-input">
          <button type="submit" class="btn-primary" :disabled="qaLoading">
            {{ qaLoading ? '发送中…' : '发送留言' }}
          </button>
        </div>
        <textarea
          v-model="qaContent"
          maxlength="500"
          rows="2"
          required
          placeholder="写点什么吧～打个招呼、提问、吐槽都行"
          class="guestboard-input"
        />
        <p v-if="qaError" class="error">{{ qaError }}</p>
      </form>

      <p v-if="qaLoading && !qaList.length" class="muted">加载中…</p>
      <ul v-else-if="qaList.length" class="guestboard-list">
        <li v-for="m in qaList" :key="m.id">
          <span class="guestboard-name">{{ m.name || '访客' }}</span>
          <span class="guestboard-text">{{ m.content }}</span>
          <span class="guestboard-time">{{ formatDate(m.created_at) }}</span>
        </li>
      </ul>
      <ul v-else class="guestboard-list guestboard-list--demo">
        <li v-for="(m, i) in guestboardExamples" :key="i">
          <span class="guestboard-name">{{ m.name }}</span>
          <span class="guestboard-text">{{ m.content }}</span>
          <span class="guestboard-time">示例</span>
        </li>
      </ul>
      <p v-if="!qaList.length && !qaLoading" class="muted guestboard-empty-hint">
        还没有留言，来做第一个吧～
      </p>
    </section>

    <!-- 工作台 -->
    <section id="workbench" class="section-block reveal-item" data-reveal>
      <header class="section-header">
        <h2 class="section-title">工作台</h2>
        <p class="section-sub">NAV · QUICK ACCESS</p>
      </header>
      <p class="section-lead">专注、论坛、个人资料 — 从这里进。</p>

      <div class="work-grid">
        <router-link
          v-for="item in platformQuickEntries"
          :key="item.to"
          :to="item.to"
          class="work-card"
          :class="{ accent: item.accent }"
        >
          <div class="work-thumb">
            <img
              :src="thumbUrl(item.thumb)"
              alt=""
              loading="lazy"
              @error="onThumbError($event, item.thumb)"
            >
          </div>
          <div class="work-body">
            <span class="work-tag">{{ item.tag }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <span class="work-arrow">进入 →</span>
          </div>
        </router-link>
      </div>

      <div v-if="stats" class="focus-strip ink-panel platform-stat-strip">
        <span>今日专注 <strong>{{ stats.today_minutes }}</strong> 分</span>
        <span>本周 <strong>{{ stats.week_minutes }}</strong> 分</span>
        <span>今日 <strong>{{ stats.today_sessions }}</strong> 次</span>
        <router-link to="/app/pomo">打开番茄钟 →</router-link>
      </div>
    </section>

    <!-- 最新文章 -->
    <section id="posts" class="section-block ink-panel reveal-item" data-reveal>
      <header class="section-header">
        <h2 class="section-title">最新文章</h2>
        <router-link to="/app/me" class="section-more">全部文章 →</router-link>
      </header>
      <p v-if="postsLoading" class="muted">加载中…</p>
      <div v-else-if="recentPosts.length" class="post-card-grid">
        <router-link
          v-for="p in recentPosts"
          :key="p.id"
          :to="`/app/posts/${p.id}`"
          class="post-card"
        >
          <span class="post-card-cat">{{ p.category || '日志' }}</span>
          <h3 class="post-card-title">{{ p.title }}</h3>
          <p v-if="p.ai_summary" class="post-card-summary">{{ p.ai_summary }}</p>
          <time class="post-card-date">{{ formatDate(p.published_at || p.created_at) }}</time>
        </router-link>
      </div>
      <p v-else class="muted">
        暂无文章 — <router-link to="/app/me">去个人中心写一篇</router-link>
      </p>
    </section>

    <!-- 链接 / 关于 -->
    <section id="links" class="section-block footer-block reveal-item section-block--alt" data-reveal>
      <header class="section-header">
        <h2 class="section-title">关于</h2>
        <p class="section-sub">LINK · NAV</p>
      </header>
      <div class="footer-grid footer-grid--two">
        <div class="footer-col">
          <h4>站内导航</h4>
          <ul>
            <li><router-link to="/app/forum">论坛</router-link></li>
            <li><router-link to="/app/me">个人中心</router-link></li>
            <li><router-link to="/app/pomo">番茄钟</router-link></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>博客区</h4>
          <ul>
            <li><router-link to="/">技术博客</router-link></li>
            <li><router-link to="/app/music">音乐室</router-link></li>
            <li><router-link to="/about">关于 & 贴纸墙</router-link></li>
            <li><router-link to="/guestbook">留言板</router-link></li>
          </ul>
        </div>
      </div>
      <p class="copyright">CYINC Platform · 与 <router-link to="/">个人博客</router-link> 账号通用</p>
    </section>
      </div>

      <PlatformHomeAside
        :section-nav="platformSectionNav"
        :site-days="siteDays"
        :profile="profile"
        :stats="stats"
        :recent-posts="recentPosts"
        :posts-loading="postsLoading"
        @section="scrollToSection"
      />
    </div>

    <Teleport to="body">
      <div v-if="lightboxIndex >= 0" class="ba-lightbox" @click.self="closeLightbox">
        <button type="button" class="lb-close" aria-label="关闭" @click="closeLightbox">✕</button>
        <button type="button" class="lb-nav lb-prev" aria-label="上一张" @click.stop="shiftLightbox(-1)">‹</button>
        <figure class="lb-figure">
          <img
            :src="imgUrl(platformBaStrip[lightboxIndex].path)"
            :alt="platformBaStrip[lightboxIndex].label"
          >
          <figcaption>[ {{ platformBaStrip[lightboxIndex].label }} ]</figcaption>
        </figure>
        <button type="button" class="lb-nav lb-next" aria-label="下一张" @click.stop="shiftLightbox(1)">›</button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import BaStripCarousel from '../../components/BaStripCarousel.vue'
import HeroTicker from '../../components/HeroTicker.vue'
import InkRevealPanel from '../../components/InkRevealPanel.vue'
import PlatformHomeAside from '../../components/PlatformHomeAside.vue'
import PlatformOnboarding from '../../components/PlatformOnboarding.vue'
import { usePageMeta } from '../../composables/usePageMeta'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'
import {
  platformBaStrip,
  platformHeroInk,
  platformHeroTicker,
  platformLaunchDate,
  platformPortrait,
  platformQuickEntries,
  platformSectionNav,
  platformSiteAttrs,
  platformTimeline,
} from '../../data/platformBaGallery.js'
import { guestboardExamples } from '../../data/social.js'
import { imgUrl, profile as siteProfile } from '../../data/profile.js'
import { thumbUrl, onThumbError } from '../../utils/thumbs.js'
import {
  createQaMessage,
  fetchPomodoroStats,
  fetchPosts,
  fetchProfile,
  fetchQaMessages,
  getPlatformToken,
} from '../../api/platform.js'

usePageMeta({
  title: '主站',
  description: 'CYINC 主站：个人中心、番茄钟、留言板与 ACG 档案。',
  image: imgUrl(platformHeroInk),
})

const homeRef = ref(null)
useRevealOnScroll(homeRef)

function openOnboarding() {
  window.dispatchEvent(new Event('platform-open-onboarding'))
}

const token = ref(getPlatformToken())
const profile = ref(null)
const stats = ref(null)
const lightboxIndex = ref(-1)

const qaList = ref([])
const qaName = ref('')
const qaContent = ref('')
const qaLoading = ref(false)
const qaError = ref('')

const recentPosts = ref([])
const postsLoading = ref(true)

const heroTags = siteProfile.acgTags.slice(0, 5)

const welcomeSubtitle = computed(() => {
  if (profile.value?.nickname) return '欢迎回到 CYINC 主站。'
  return '随便逛逛，有事去留言板说～'
})

/** 站点形象头像（与下方兴趣标签同属品牌区，不用登录用户上传头像） */
const heroAvatarSrc = computed(() => imgUrl(siteProfile.avatar || 'img/xiaoqing.png'))

const siteDays = computed(() => {
  const start = new Date(platformLaunchDate)
  const now = new Date()
  const diff = Math.floor((now - start) / 86400000)
  return diff > 0 ? diff : 0
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN')
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function openLightbox(index) {
  lightboxIndex.value = index
  document.body.style.overflow = 'hidden'
}

function closeLightbox() {
  lightboxIndex.value = -1
  document.body.style.overflow = ''
}

function shiftLightbox(delta) {
  const n = platformBaStrip.length
  lightboxIndex.value = (lightboxIndex.value + delta + n) % n
}

async function loadQa() {
  qaLoading.value = true
  try {
    const json = await fetchQaMessages(20)
    qaList.value = json.data || []
  } catch {
    qaList.value = []
  } finally {
    qaLoading.value = false
  }
}

async function loadRecentPosts() {
  postsLoading.value = true
  try {
    const json = await fetchPosts(1, 3)
    recentPosts.value = json.data?.items || []
  } catch {
    recentPosts.value = []
  } finally {
    postsLoading.value = false
  }
}

async function submitQa() {
  qaError.value = ''
  if (!qaContent.value.trim()) {
    qaError.value = '写点什么再发送吧～'
    return
  }
  qaLoading.value = true
  try {
    await createQaMessage({
      name: qaName.value.trim() || null,
      content: qaContent.value.trim(),
    })
    qaContent.value = ''
    await loadQa()
  } catch (e) {
    qaError.value = e.message
  } finally {
    qaLoading.value = false
  }
}

function onKeydown(e) {
  if (lightboxIndex.value < 0) return
  if (e.key === 'Escape') closeLightbox()
  if (e.key === 'ArrowLeft') shiftLightbox(-1)
  if (e.key === 'ArrowRight') shiftLightbox(1)
}

async function loadProfileAndStats() {
  if (!token.value) return
  try {
    const [profileJson, statsJson] = await Promise.all([
      fetchProfile(),
      fetchPomodoroStats(),
    ])
    profile.value = profileJson.data
    stats.value = statsJson.data
  } catch {
    profile.value = null
    stats.value = null
  }
}

onMounted(async () => {
  window.addEventListener('keydown', onKeydown)
  await Promise.all([loadProfileAndStats(), loadQa(), loadRecentPosts()])
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.platform-home {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-bottom: 2rem;
  position: relative;
  z-index: 1;
}

.platform-home-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 300px);
  gap: clamp(1.25rem, 2vw, 2rem);
  align-items: start;
}

.platform-home-main {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-width: 0;
}

.platform-home-main > section.section-block:nth-of-type(even) {
  background: color-mix(in srgb, var(--bg-paper) 55%, transparent);
}

.section-nav--mobile {
  display: none;
  position: static;
  background: transparent;
  backdrop-filter: none;
  z-index: auto;
}

.section-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.5rem 0;
  border-bottom: 1px dashed var(--border);
}

.section-nav-link {
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  color: inherit;
  text-decoration: none;
  transition: border-color 0.15s, color 0.15s;
}

.section-nav-link:hover {
  border-color: var(--orange);
  color: var(--orange);
}

.platform-hero {
  position: relative;
}

.platform-hero--ink :deep(.ink-panel__content) {
  padding: clamp(1.25rem, 4vw, 2.5rem);
  min-height: 200px;
  position: relative;
}

.hero-coord-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.07;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 24px 24px;
  mask-image: linear-gradient(135deg, transparent 20%, #000 45%, #000 70%, transparent 95%);
}

.platform-hero--ink :deep(.ink-panel__content) > :not(.hero-coord-overlay) {
  position: relative;
  z-index: 1;
}

.hero-copy {
  max-width: 36rem;
}

.welcome-eyebrow {
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 0.35rem;
}

.hero-title {
  font-size: clamp(1.75rem, 5vw, 2.35rem);
  margin: 0 0 0.5rem;
  line-height: 1.2;
}

.hero-title-sub {
  display: block;
  font-family: var(--mono);
  font-size: 0.55em;
  color: var(--orange);
  letter-spacing: 0.08em;
  margin-top: 0.25rem;
}

.welcome-guest {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.65;
  margin-bottom: 1rem;
}

.hero-cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.hero-split {
  display: grid;
  grid-template-columns: 1fr minmax(140px, 220px);
  gap: 1.25rem;
  align-items: end;
}

.hero-main.compact {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 0.85rem;
}

.hero-tagline {
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.55;
  margin-bottom: 0.5rem;
}

.hero-chips { gap: 0.3rem; }

.hero-portrait {
  margin: 0;
  text-align: center;
}

.acg-frame--portrait {
  width: 100%;
  aspect-ratio: 3 / 4;
  max-height: 280px;
}

.acg-frame--portrait img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-portrait figcaption {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
}

.btn-primary,
.btn-ghost {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.45rem 0.95rem;
  text-decoration: none;
  border: 1px solid var(--border);
}

.btn-primary {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.btn-ghost {
  color: inherit;
  background: var(--bg-paper);
}

.section-block {
  padding: 1.5rem 1.35rem;
  scroll-margin-top: calc(var(--topbar-height) + 3rem);
}

.section-header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.35rem 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid var(--border);
}

.section-title {
  font-size: 1.15rem;
  margin: 0;
}

.section-sub {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
  letter-spacing: 0.1em;
  margin: 0;
}

.section-more {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  text-decoration: none;
}

.section-lead {
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0 0 1rem;
}

.intro-body {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.intro-text p {
  font-size: 0.88rem;
  line-height: 1.65;
  color: var(--text-muted);
  margin: 0 0 0.65rem;
}

.intro-text a {
  color: var(--orange);
}

.attr-grid {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0;
  border: 1px solid var(--border);
}

.attr-grid li {
  display: grid;
  grid-template-columns: 4.5rem 1fr;
  gap: 0.5rem;
  padding: 0.45rem 0.65rem;
  font-size: 0.78rem;
  border-bottom: 1px dashed var(--border);
}

.attr-grid li:last-child { border-bottom: none; }

.attr-key {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--orange);
}

.attr-val { color: var(--text-muted); }

.timeline-head {
  font-size: 0.88rem;
  margin: 0 0 0.65rem;
  font-family: var(--mono);
}

.timeline-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
}

.timeline-list li {
  display: grid;
  grid-template-columns: 5rem 1fr;
  gap: 0.75rem;
  font-size: 0.82rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed var(--border);
}

.timeline-list time {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--orange);
}

.post-card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.85rem;
}

.post-card {
  display: grid;
  gap: 0.35rem;
  padding: 1rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.post-card:hover {
  border-color: var(--orange);
  box-shadow: 0 3px 0 var(--orange);
}

.post-card-cat {
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--orange);
  letter-spacing: 0.08em;
}

.post-card-title {
  font-size: 0.92rem;
  margin: 0;
  line-height: 1.4;
}

.post-card-summary {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-card-date {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.archive-note {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  margin: 1rem 0 0;
}

.archive-note code {
  color: var(--orange);
}

.work-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.work-card {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 0.75rem;
  padding: 0.85rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.work-card:hover {
  border-color: var(--orange);
  box-shadow: 0 3px 0 var(--orange);
}

.work-card.accent {
  border-color: color-mix(in srgb, var(--orange) 50%, var(--border));
}

.work-thumb {
  border: 1px solid var(--border);
  overflow: hidden;
  aspect-ratio: 1;
}

.work-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.85);
}

.work-tag {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--orange);
}

.work-body h3 {
  font-size: 0.95rem;
  margin: 0.15rem 0;
}

.work-body p {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.45;
}

.work-arrow {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--orange);
  display: inline-block;
  margin-top: 0.35rem;
}

.focus-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem 1.5rem;
  padding: 0.75rem 1rem;
  font-family: var(--mono);
  font-size: 0.78rem;
}

.focus-strip strong { color: var(--orange); }

.focus-strip a {
  margin-left: auto;
  color: var(--orange);
  text-decoration: none;
  font-size: 0.72rem;
}

.cat-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.cat-chip {
  display: grid;
  gap: 0.12rem;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--border);
  background: var(--bg);
  text-decoration: none;
  color: inherit;
  min-width: 110px;
}

.cat-chip:hover { border-color: var(--orange); }

.cat-slug {
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--orange);
  text-transform: uppercase;
}

.cat-name { font-size: 0.85rem; font-weight: 500; }

.cat-count {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}

.work-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.6rem;
}

.work-list li {
  padding-bottom: 0.55rem;
  border-bottom: 1px dashed var(--border);
}

.work-list-title {
  color: inherit;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.88rem;
}

.work-list-title:hover { color: var(--orange); }

.meta {
  display: block;
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
}

.footer-block {
  border: 1px solid var(--border);
  background: var(--bg-paper);
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.footer-col h4 {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
  margin: 0 0 0.5rem;
}

.footer-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.35rem;
}

.footer-col a {
  font-size: 0.8rem;
  color: inherit;
  text-decoration: none;
}

.footer-col a:hover { color: var(--orange); }

.stat-line {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin: 0 0 0.35rem;
}

.stat-line strong { color: var(--orange); }

.footer-grid--two {
  grid-template-columns: repeat(2, 1fr);
}

.copyright {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  margin: 0;
  padding-top: 0.75rem;
  border-top: 1px dashed var(--border);
}

.copyright a { color: var(--orange); }

.muted { color: var(--text-muted); font-size: 0.88rem; }
.empty-hint a { color: var(--orange); }

/* 留言板 */
.guestboard-form {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.guestboard-form-row {
  display: flex;
  gap: 0.5rem;
}

.guestboard-input {
  width: 100%;
  border: 1px solid var(--border);
  padding: 0.5rem 0.6rem;
  font: inherit;
  background: var(--bg);
  color: inherit;
  resize: vertical;
}

.guestboard-form-row .guestboard-input {
  flex: 1;
}

.guestboard-form .btn-primary {
  width: fit-content;
  font-family: var(--mono);
  font-size: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--orange);
  border: 1px solid var(--orange);
  color: #fff;
  cursor: pointer;
}

.guestboard-form .btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.guestboard-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.6rem;
}

.guestboard-list li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.35rem 0.75rem;
  align-items: baseline;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed var(--border);
  font-size: 0.86rem;
}

.guestboard-name {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--orange);
}

.guestboard-text {
  color: var(--text-muted);
}

.guestboard-time {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
}

.guestboard-list--demo .guestboard-time {
  opacity: 0.65;
}

.guestboard-empty-hint {
  margin-top: 0.5rem;
}

.guestboard-form .error {
  color: #c0392b;
  font-size: 0.8rem;
  margin: 0;
}

/* Lightbox */
.ba-lightbox {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(0, 0, 0, 0.82);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.lb-figure {
  margin: 0;
  max-width: min(90vw, 720px);
  max-height: 85vh;
}

.lb-figure img {
  max-width: 100%;
  max-height: 78vh;
  object-fit: contain;
  border: 2px solid var(--border);
}

.lb-figure figcaption {
  text-align: center;
  font-family: var(--mono);
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.75);
  margin-top: 0.5rem;
}

.lb-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #fff;
  width: 36px;
  height: 36px;
  cursor: pointer;
}

.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #fff;
  width: 40px;
  height: 48px;
  cursor: pointer;
  font-size: 1.5rem;
}

.lb-prev { left: 1rem; }
.lb-next { right: 1rem; }

@media (max-width: 960px) {
  .platform-home-grid {
    grid-template-columns: 1fr;
  }

  .section-nav--mobile {
    display: flex;
  }
}

@media (max-width: 900px) {
  .hero-split { grid-template-columns: 1fr; }
  .hero-portrait { max-width: 200px; margin: 0 auto; }
  .intro-body { grid-template-columns: 1fr; }
  .post-card-grid { grid-template-columns: 1fr; }
  .work-grid { grid-template-columns: 1fr; }
  .footer-grid,
  .footer-grid--two { grid-template-columns: 1fr 1fr; }
}

@media (min-width: 961px) {
  .post-card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 560px) {
  .hero-main.compact {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .hero-chips { justify-content: center; }
  .hero-cta-row { justify-content: center; }
  .footer-grid { grid-template-columns: 1fr; }
  .timeline-list li { grid-template-columns: 1fr; gap: 0.2rem; }
}
</style>

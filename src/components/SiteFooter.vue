<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="footer-logo">CYINC.LOG</span>
        <p class="footer-desc">写给自己的技术学习日志</p>
      </div>
      <div class="footer-links">
        <router-link to="/archive">归档</router-link>
        <router-link to="/projects">项目</router-link>
        <router-link to="/changelog">更新</router-link>
        <router-link to="/guestbook">留言板</router-link>
        <router-link to="/music">音乐室</router-link>
        <a :href="rssUrl" target="_blank" rel="noopener">RSS</a>
        <a href="https://github.com/kukukuyashi/myweb" target="_blank" rel="noopener">GitHub</a>
        <a :href="reportMailto" class="footer-report">举报</a>
      </div>

      <div class="footer-bottom">
        <p class="footer-meta">
          <span>© {{ year }} Cyinc</span>
          <span class="footer-dot" aria-hidden="true">·</span>
          <span>{{ totalPosts }} articles</span>
          <span class="footer-dot" aria-hidden="true">·</span>
          <a
            class="beian-link"
            href="https://beian.miit.gov.cn/"
            target="_blank"
            rel="noopener noreferrer"
          >{{ BEIAN_ICP }}</a>
          <template v-if="BEIAN_POLICE">
            <span class="footer-dot" aria-hidden="true">·</span>
            <a
              class="beian-link beian-link--police"
              :href="policeBeianUrl"
              target="_blank"
              rel="noopener noreferrer"
            >
              <span class="beian-police-icon" aria-hidden="true" />
              {{ BEIAN_POLICE }}
            </a>
          </template>
        </p>
        <p class="footer-rss">
          订阅：
          <a :href="rssUrl" target="_blank" rel="noopener">{{ rssUrl }}</a>
        </p>
        <p class="footer-rss">
          举报 / 联系：
          <a :href="reportMailto">{{ REPORT_EMAIL }}</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { posts } from '../data/posts'

/** ICP 备案号（管局已通过） */
const BEIAN_ICP = '桂ICP备2026014828号-1'
/**
 * 公安联网备案号。办完后改成例如：桂公网安备45xxxxxxxx号
 * 留空则不显示。
 */
const BEIAN_POLICE = ''

const year = new Date().getFullYear()
const totalPosts = computed(() => posts.length)
const rssUrl = `${import.meta.env.BASE_URL}feed.xml`
const policeBeianUrl = 'https://beian.mps.gov.cn/#/query/webSearch'

/** 内容举报邮箱（备案自评估：投诉举报机制入口） */
const REPORT_EMAIL = '1344908013@qq.com'
const reportMailto = `mailto:${REPORT_EMAIL}?subject=${encodeURIComponent('[CYINC.LOG] 内容举报')}&body=${encodeURIComponent('举报内容链接：\n违规类型：\n补充说明：\n')}`
</script>

<style scoped>
.site-footer {
  border-top: 1px solid var(--border);
  background: var(--bg-paper);
  margin-top: 3rem;
  /* 给底部 MusicPlayer 留空 */
  padding: 1.75rem 1.5rem calc(5.5rem + var(--safe-bottom, 0px));
}

.footer-inner {
  width: var(--content-width);
  max-width: none;
  margin: 0 auto;
  padding: 0 clamp(1.25rem, 2.5vw, 2.5rem);
  display: flex;
  flex-wrap: wrap;
  gap: 1rem 1.5rem;
  align-items: flex-start;
  justify-content: space-between;
  font-family: var(--mono);
  font-size: 0.72rem;
}

.footer-logo {
  font-weight: 500;
  letter-spacing: 0.05em;
  color: var(--text);
}

.footer-desc {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
  font-family: var(--sans);
  font-size: 0.85rem;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem 1.1rem;
}

.footer-links a {
  color: var(--steel);
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.footer-links a:hover {
  color: var(--orange);
}

.footer-report {
  color: var(--orange);
}

.footer-report:hover {
  text-decoration: underline;
}

.footer-bottom {
  width: 100%;
  padding-top: 0.85rem;
  border-top: 1px dashed var(--border);
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.45rem 1.25rem;
}

.footer-meta {
  margin: 0;
  color: var(--text-muted);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.15rem 0;
  line-height: 1.55;
}

.footer-rss {
  margin: 0;
  font-size: 0.62rem;
  color: var(--text-muted);
  word-break: break-all;
}

.footer-rss a {
  color: var(--steel);
  text-decoration: none;
}

.footer-rss a:hover {
  color: var(--orange);
}

.beian-link {
  color: var(--text-muted);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: color 0.15s ease, border-color 0.15s ease;
}

.beian-link:hover {
  color: var(--orange);
  border-bottom-color: color-mix(in srgb, var(--orange) 45%, transparent);
}

.beian-link--police {
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
}

.beian-police-icon {
  width: 0.85rem;
  height: 0.85rem;
  flex-shrink: 0;
  background: currentColor;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23000' d='M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z'/%3E%3C/svg%3E") center / contain no-repeat;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23000' d='M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z'/%3E%3C/svg%3E") center / contain no-repeat;
  opacity: 0.75;
}

.footer-dot {
  margin: 0 0.35rem;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .site-footer {
    padding: 1.35rem 0 calc(6rem + var(--safe-bottom, 0px));
  }

  .footer-inner {
    flex-direction: column;
    gap: 0.85rem;
    padding: 0 1rem;
  }

  .footer-links {
    gap: 0.45rem 0.9rem;
  }

  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.4rem;
  }
}
</style>

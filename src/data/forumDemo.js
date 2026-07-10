import { platformBaStrip } from './platformBaGallery.js'

/** 论坛侧边公告（静态） */
export const forumAnnouncements = [
  { icon: '★', text: '欢迎来到 CYINC 论坛 — 分享 ACG 与技术日常' },
  { icon: '📢', text: '发帖请先登录，支持 Markdown 正文' },
  { icon: '🍅', text: '番茄钟专注记录可在个人中心查看' },
]

/**
 * 示例帖（API 不足 7 条时填充贴纸墙）
 * id 为 null 表示仅展示，不可点击
 */
export const forumDemoThreads = [
  {
    id: null,
    title: '碧蓝档案新活动立绘分享',
    category_name: '日常交流',
    author: { nickname: 'Cyinc' },
    reply_count: 24,
    view_count: 892,
    cover: platformBaStrip[0]?.path,
    excerpt: '妃咲这张太绝了，大家来看看…',
  },
  {
    id: null,
    title: 'Vue 3 + FastAPI 论坛 MVP 复盘',
    category_name: '技术讨论',
    author: { nickname: 'Cyinc' },
    reply_count: 18,
    view_count: 654,
    cover: platformBaStrip[1]?.path,
    excerpt: 'JWT、板块 CRUD、Markdown 编辑器踩坑记录。',
  },
  {
    id: null,
    title: '星野同人图整理（img/BA）',
    category_name: '项目展示',
    author: { nickname: '访客A' },
    reply_count: 12,
    view_count: 1203,
    cover: platformBaStrip[2]?.path,
    excerpt: '把收藏夹里的图床路径统一了一下。',
  },
  {
    id: null,
    title: '番茄钟 v2 圆环计时体验',
    category_name: '技术讨论',
    author: { nickname: 'Cyinc' },
    reply_count: 9,
    view_count: 431,
    cover: platformBaStrip[3]?.path,
    excerpt: '专注结束可以写反思，会进时间线。',
  },
  {
    id: null,
    title: 'ECS 单机上 Docker 全栈部署笔记',
    category_name: '技术讨论',
    author: { nickname: 'Cyinc' },
    reply_count: 31,
    view_count: 2104,
    cover: platformBaStrip[4]?.path,
    excerpt: 'MySQL 在宿主机、API 在容器里踩的 ufw 坑。',
  },
  {
    id: null,
    title: '周末 Cosplay 返图（吹雪）',
    category_name: '日常交流',
    author: { nickname: '友人B' },
    reply_count: 45,
    view_count: 3421,
    cover: platformBaStrip[5]?.path,
    excerpt: '场照修图修到半夜，先发几张。',
  },
  {
    id: null,
    title: '主站侧边栏改版 & 论坛 UI 升级',
    category_name: '项目展示',
    author: { nickname: 'Cyinc' },
    reply_count: 7,
    view_count: 388,
    cover: platformBaStrip[6]?.path,
    excerpt: '参考 ACG 社区排版，贴纸墙展示精选帖。',
  },
]

export function pickCover(index) {
  return platformBaStrip[index % platformBaStrip.length]?.path || 'img/xiaoqing.png'
}

export function mergeFeaturedThreads(apiThreads) {
  const out = []
  for (let i = 0; i < 7; i++) {
    if (apiThreads[i]) {
      const t = apiThreads[i]
      out.push({
        ...t,
        cover: pickCover(i),
        excerpt: t.title,
      })
    } else {
      out.push({ ...forumDemoThreads[i], cover: pickCover(i) })
    }
  }
  return out
}

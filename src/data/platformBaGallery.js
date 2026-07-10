/**
 * 主站首页数据 — img/BA 档案、分区文案、时间线
 */
export const platformHeroInk = 'img/BA/F/妃咲/2023_06_13_17_45_IMG_3259.JPG'

/** Hero 右侧「立绘」 */
export const platformPortrait = 'img/BA/X/星野/d6db50f9097db958e26f0fc42c67eb16.jpeg'

export const platformHeroTicker = [
  { text: 'CYINC PLATFORM' },
  { text: 'POMODORO' },
  { text: 'GUESTBOOK' },
  { text: 'ACG ARCHIVE' },
  { text: 'VUE · FASTAPI' },
]

export const platformBaStrip = [
  { path: 'img/BA/X/星野/d6db50f9097db958e26f0fc42c67eb16.jpeg', label: '星野' },
  { path: 'img/BA/R/日奈/458780fd5ec25ccaefe0fd36ccfbabaa_720.jpg', label: '日奈' },
  { path: 'img/BA/mika/acdcfb54cb622b0e8bdf29af195398f6_720.jpg', label: 'Mika' },
  { path: 'img/BA/A/爱莉/2fd0a12728327701054df80f0686eb0f.jpeg', label: '爱莉' },
  { path: 'img/BA/魔法伊蕾娜/c9d5e22d00c44a9139f12f3139620173_720.jpg', label: '伊蕾娜' },
  { path: 'img/BA/C/吹雪/5c10b5b884dbde1fa99b04795a689f57_720.jpg', label: '吹雪' },
  { path: 'img/BA/G/宫子/07d8a069f0ffec88d536ccf3a067d4d0.png', label: '宫子' },
  { path: 'img/BA/L/莉音/e8781d4d0a4086a1647fb749fffe6909.jpeg', label: '莉音' },
  { path: 'img/BA/3590b9b84647d1babd85a22676172c62.jpeg', label: '收藏' },
  { path: 'img/BA/9425b4cdef410b4758b699d6b1d806d7.jpg', label: '档案' },
]

export const platformSiteAttrs = [
  { key: '坐标', value: 'CYINC · /app' },
  { key: '栈', value: 'Vue 3 · FastAPI · MySQL' },
  { key: '论坛', value: '板块 · 贴纸墙 · Markdown' },
  { key: 'ACG', value: '碧蓝档案 · 葬送のフリーレン' },
  { key: '主色', value: '#e85d04 工业橙' },
  { key: '字体', value: 'IBM Plex Mono' },
]

export const platformTimeline = [
  { date: '2026.06', text: 'FastAPI 鉴权 + JWT 脚手架（M1）' },
  { date: '2026.06', text: '文章 CRUD + Dify 摘要 + Chatflow /ai（M2–M3）' },
  { date: '2026.07', text: 'n8n 发文 Webhook 联调通过（M4）' },
  { date: '2026.07', text: '主站 /app 分离 + 论坛 MVP + 番茄钟 v2（M5.5）' },
  { date: 'NEXT', text: '阿里云 ECS + Docker 上线（M6）' },
]

export const platformSectionNav = [
  { id: 'intro', label: '简介' },
  { id: 'archive', label: '档案' },
  { id: 'guestboard', label: '留言板' },
  { id: 'workbench', label: '工作台' },
  { id: 'posts', label: '博客' },
  { id: 'links', label: '链接' },
]

export const platformQuickEntries = [
  {
    to: '/app/me',
    tag: 'ME',
    title: '个人中心',
    desc: '资料、文章与专注时间线。',
    thumb: 'img/BA/X/星野/d6db50f9097db958e26f0fc42c67eb16.jpeg',
    accent: true,
  },
  {
    to: '/app/pomo',
    tag: 'POMO',
    title: '番茄钟',
    desc: '圆环计时、反思总结与本周统计。',
    thumb: 'img/BA/R/日奈/5d0a8942b8224ab477751bdcffa8abc3.jpeg',
  },
  {
    to: '/app/forum',
    tag: 'FORUM',
    title: 'ACG 社区',
    desc: '论坛讨论、贴纸墙精选与板块。',
    thumb: 'img/BA/mika/acdcfb54cb622b0e8bdf29af195398f6_720.jpg',
  },
  {
    to: '/app/music',
    tag: 'MUSIC',
    title: '音乐室',
    desc: 'FLAC 歌单、专辑列表与换页续播。',
    thumb: 'img/BA/魔法伊蕾娜/c9d5e22d00c44a9139f12f3139620173_720.jpg',
  },
]

/** 站点上线日 — 用于「已运行」统计 */
export const platformLaunchDate = '2026-06-01'

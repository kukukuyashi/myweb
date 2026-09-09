import { aboutGallery } from './aboutGallery'
import { profile } from './profile'

export const defaultAboutContent = {
  heroImage: 'img/关于/Fp6MHMdaEAA806l.jfif',
  avatar: profile.avatar,
  name: profile.name,
  tagline: profile.tagline,
  acgTags: [...profile.acgTags],
  lead: '这个站既是技术笔记本，也是 ACG 爱好者的自留地。笔记可以查，音乐室可以听，留言板可以聊 — 不必把爱好和技术分开。',
  whoIAm: [
    '叫我 Cyinc 就好。平时写 Vue / Java / Agent 相关的东西，私下是重度 ACG 用户：追番、囤 OST、看 MAD，音乐室里那几首就是真实歌单。',
    '博客最初是前端学习草稿本，后来加了 Agent 笔记、Twikoo 留言板、音乐播放器。风格刻意做成「工业蓝图」的样子 — 但人格不用跟着变冷，ACG 图会放在档案框里，像贴纸墙一样，不破坏整体版式。',
  ],
  favorites: profile.favorites.map((item) => ({ ...item })),
  quote: '写下来，才算真正学过一遍 — 番剧观后感也算。',
  skills: ['Vue / JS', 'Agent / LLM', 'Python', 'Node.js', 'Java', 'PHP', 'Twikoo'],
  stickers: aboutGallery.slice(0, 10).map((item) => ({ ...item })),
  contacts: {
    email: profile.email,
    blog: profile.blog,
    github: profile.github,
    musicPath: '/app/music',
  },
}

export const defaultArchiveContent = {
  title: '文章归档',
  description: '',
  postLimit: 0,
  showStats: true,
  showCategoryPanel: true,
}

export function cloneSitePageContent(content) {
  return JSON.parse(JSON.stringify(content))
}

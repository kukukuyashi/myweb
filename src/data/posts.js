/**
 * 文章目录 — 发新文章只需在这里加一条，并放入 Content/ 对应 html 文件
 */
import { encodePathSegments } from '../utils/music.js'

export const SITE_NAME = 'Cyinc 的学习日志'
export const SITE_URL = 'https://kukukuyashi.github.io/myweb'
export const SITE_DESCRIPTION = '前端、Agent 与 Java 学习笔记，踩坑记录与 Twikoo 留言板。'

export const posts = [
  {
    id: 29,
    title: 'Git 与 GitHub入门笔记',
    date: '2026-07-01',
    category: '部署',
    tags: ['学习', 'git', 'github', '多人项目协助', '项目版本处理'],
    excerpt: 'Git 与 GitHub入门笔记 — 学习笔记。',
    file: 'Git 与 GitHub入门笔记.html',
    cover: 'img/关于/F0xVRaEakAAKgCw.jfif',
  },
  {
    id: 28,
    title: 'Agent Harness 体系',
    date: '2026-07-01',
    category: '学习',
    tags: ['学习'],
    excerpt: '学习如何对 AI Agent（如 Claude Code）进行质量保障，掌握从单元测试、集成模拟（Mock）到模型评估（Eval）和自动化部署的全链路 Harness 方法。',
    file: 'Agent Harness 体系.html'
  },
  {
    id: 27,
    title: '鼠标动画光标：从 PNG 序列到 Chrome 兼容',
    date: '2026-06-29',
    category: '前端',
    tags: ['CSS', 'Vue', '前端', '鼠标', '动画', 'Python', 'Canvas'],
    excerpt: 'PNG 序列生成透明 GIF，Canvas 叠加层逐帧清屏绘制，解决 Chrome 不动与移动拖影两个问题。',
    file: '鼠标动画光标从素材到上线.html',
    cover: 'img/bkm/5.jfif',
  },
  {
    id: 26,
    title: '自定义鼠标样式与点击涟漪效果',
    date: '2026-06-26',
    category: '前端',
    tags: ['CSS', 'Vue', '前端', '鼠标', '动画'],
    excerpt: '用 CSS cursor 属性替换默认鼠标为动态 GIF 光标，加上纯 CSS 实现的点击涟漪波纹效果。',
    file: '自定义鼠标样式与点击涟漪效果.html',
    cover: 'img/bkm/5.jfif',
  },
  {
    id: 20,
    title: '帕朵root开发笔记',
    date: '2026-06-14',
    category: '项目',
    tags: ['项目'],
    excerpt: '帕朵root开发笔记 — 学习笔记。',
    file: '帕朵root开发笔记.html',
    cover: 'img/bkm/2.jfif',
  },

  {
    id: 24,
    title: '首页墨染晕染：鼠标 hover 显现线稿',
    date: '2026-06-16',
    category: '前端',
    tags: ['Canvas', 'Vue', '前端'],
    excerpt: '首页 Hero、音乐室、关于页顶栏都有「鼠标划过去，线稿从纸面晕开」的效果。这篇拆开 DOM 结构、Canvas 遮罩原理和 Vue 组件怎么接，方便以后换图或复用到别的面板。',
    file: '首页墨染晕染 Canvas 鼠标显现线稿.html',
    cover: 'img/bkm/3.jfif',
  },

  {
    id: 25,
    title: '陈皮有多陈：Flask + AI 鉴陈项目笔记',
    date: '2026-06-15',
    category: '项目',
    tags: ['Flask', 'Python', 'AI', '项目', 'Qwen'],
    excerpt: '第八届传智杯比赛项目「陈皮有多陈」复盘：Flask 单体应用 + 通义千问视觉模型 + 传统页面，用通俗语言讲清楚怎么搭起来的。',
    file: '陈皮有多陈 Flask AI 鉴陈项目笔记.html',
  },

  {
    id: 22,
    title: '博客音乐室：GitHub Pages 上播 FLAC',
    date: '2026-06-14',
    category: '部署',
    tags: ['Vue', 'FLAC', 'GitHub Pages', '部署', '音乐'],
    excerpt: '静态博客也能当播放器用 — 这篇讲音乐室怎么实现、FLAC 怎么部署到 GitHub Pages、以及路由切换时音乐为什么会重播（以及怎么修）。',
    file: '博客音乐室 GitHub Pages 播 FLAC.html',
    cover: 'img/bkm/5.jfif',
  },

  {
    id: 23,
    title: 'GitHub Actions 自动部署 Vue 博客',
    date: '2026-06-13',
    category: '部署',
    tags: ['GitHub Actions', 'CI/CD', 'Vue', '部署'],
    excerpt: 'push 代码就自动更新网站 — 这篇记录本博客 GitHub Actions 部署流程，适合第一次配 CI 的同学对照操作。',
    file: 'GitHub Actions 自动部署 Vue 博客.html',
  },

  {
    id: 21,
    title: '个人博客重构记：Vue3 静态站上线',
    date: '2026-06-12',
    category: '部署',
    tags: ['Vue3', 'Vue', 'GitHub Pages', '重构', '部署'],
    excerpt: '记录这个博客从「老静态页」到 Vue3 + Vite + GitHub Pages 的重构过程，尽量用大白话讲清楚为什么要改、改了什么、踩了哪些坑。',
    file: '个人博客重构记 Vue3 静态站上线.html',
    cover: 'img/bkm/4.jfif',
  },

  {
    id: 19,
    title: '留言板 Twikoo 部署笔记',
    date: '2026-06-11',
    category: '学习',
    tags: [],
    excerpt: 'Twikoo 留言板完整部署：MongoDB Atlas、Netlify 云函数、博客接入与踩坑记录。',
    file: '留言板 Twikoo 部署笔记.html',
    cover: 'img/bkm/1.jfif',
  },

  {
    id: 18,
    title: '从 LLM 到 Agent Skill 笔记',
    date: '2026-06-09',
    category: 'Agent',
    tags: ['Agent', 'LLM', 'Skill', 'MCP', 'AI'],
    excerpt: 'LLM、Token、Context、Prompt、Tool、MCP、Agent、Skill 基础概念梳理，带通俗解释。',
    file: '从 LLM 到 Agent Skill 笔记.html',
    cover: 'img/bkm/3.jfif',
  },
  {
    id: 12,
    title: 'JAVA笔记一(基本语法)',
    date: '2026-04-03',
    category: 'Java',
    tags: ['Java', '语法', '基础'],
    excerpt: 'Java 基本语法学习笔记。',
    file: 'JAVA笔记一(基本语法).html'
  },
  {
    id: 13,
    title: 'JAVA笔记二(流程控制语句)',
    date: '2026-04-03',
    category: 'Java',
    tags: ['Java', '流程控制', '基础'],
    excerpt: 'Java 流程控制语句学习笔记。',
    file: 'JAVA笔记二(流程控制语句).html'
  },
  {
    id: 14,
    title: 'JAVA笔记三(数组)',
    date: '2026-04-03',
    category: 'Java',
    tags: ['Java', '数组', '基础'],
    excerpt: 'Java 数组学习笔记。',
    file: 'JAVA笔记三(数组).html'
  },
  {
    id: 15,
    title: 'JAVA笔记四（方法）',
    date: '2026-04-03',
    category: 'Java',
    tags: ['Java', '方法', '基础'],
    excerpt: 'Java 方法学习笔记。',
    file: 'JAVA笔记四（方法）.html'
  },
  {
    id: 17,
    title: 'Java的运行原理',
    date: '2026-04-03',
    category: 'Java',
    tags: ['Java', 'JVM', '原理'],
    excerpt: 'Java 运行原理，JVM、内存结构、垃圾回收等。',
    file: 'Java的运行原理.html'
  },
  {
    id: 1,
    title: '前端核心学习表',
    date: '2026-01-30',
    category: '学习',
    tags: ['前端', 'HTML', 'CSS', 'JavaScript', '速查'],
    excerpt: 'HTML、CSS、JavaScript 核心知识点梳理，适合随时查阅的速查表。',
    file: '前端核心学习表.html'
  },
  {
    id: 2,
    title: 'Vue.js,Three.js和Node.js的区别',
    date: '2025-12-21',
    category: '技术',
    tags: ['Vue', 'Three.js', 'Node.js', '前端'],
    excerpt: '详细介绍 Vue.js、Three.js 和 Node.js 的区别和应用场景。',
    file: 'Vue.js,Three.js和Node.js的区别.html'
  },
  {
    id: 3,
    title: 'RhinoWeb的常见问题',
    date: '2025-12-21',
    category: '小知识',
    tags: ['RhinoWeb', 'FAQ', '工具'],
    excerpt: 'RhinoWeb 使用过程中常见问题的解决方案。',
    file: 'RhinoWeb的常见问题.html'
  },
  {
    id: 10,
    title: 'Web API笔记（四）',
    date: '2025-12-18',
    category: '技术',
    tags: ['JavaScript', 'Web API', 'DOM', '实战'],
    excerpt: 'Web API 综合案例与实战练习。',
    file: 'Web API4.html'
  },
  {
    id: 5,
    title: 'JS进阶笔记（一）',
    date: '2025-12-17',
    category: '技术',
    tags: ['JavaScript', '闭包', '原型链', '进阶'],
    excerpt: 'JavaScript 进阶知识点，包含闭包、原型链等内容。',
    file: 'JS进阶1.html'
  },
  {
    id: 6,
    title: 'JS进阶笔记（二）',
    date: '2025-12-17',
    category: '技术',
    tags: ['JavaScript', 'Promise', '异步', '进阶'],
    excerpt: 'JavaScript 进阶知识点，包含异步编程、Promise 等内容。',
    file: 'JS进阶2.html'
  },
  {
    id: 9,
    title: 'Web API笔记（三）',
    date: '2025-12-17',
    category: '技术',
    tags: ['JavaScript', 'Web API', 'BOM', '存储'],
    excerpt: 'Web API 进阶，包含 BOM 操作、本地存储等内容。',
    file: 'Web API3.html'
  },
  {
    id: 8,
    title: 'Web API笔记（二）',
    date: '2025-12-16',
    category: '技术',
    tags: ['JavaScript', 'Web API', '事件'],
    excerpt: 'Web API 进阶，包含事件流、事件委托等内容。',
    file: 'Web API2.html'
  },
  {
    id: 7,
    title: 'Web API学习笔记',
    date: '2025-12-15',
    category: '技术',
    tags: ['JavaScript', 'Web API', 'DOM'],
    excerpt: 'Web API 核心知识点，包含 DOM 操作、事件监听等内容。',
    file: 'Web API.html'
  },
  {
    id: 11,
    title: 'JS基础笔记',
    date: '2025-12-10',
    category: '技术',
    tags: ['JavaScript', '基础'],
    excerpt: 'JavaScript 基础知识点，变量、数据类型、流程控制等。',
    file: 'JS基础.html'
  },
  {
    id: 4,
    title: 'Vue3学习笔记',
    date: '2025-02-27',
    category: '技术',
    tags: ['Vue', 'Vue3', 'Composition API', '前端'],
    excerpt: 'Vue3 核心知识点学习笔记，包含 Composition API 等新特性。',
    file: 'Vue3学习笔记.html'
  }
]

let _postsCatalogLoaded = false
let _postsCatalogPromise = null

/**
 * 优先拉取 /myweb/data/posts.json（线上发布热更新），失败则保留打包进包的目录。
 * 用 splice 原地更新，已 import posts 的模块会看到新数据。
 */
export async function reloadPostsCatalog() {
  _postsCatalogLoaded = false
  _postsCatalogPromise = null
  return ensurePostsCatalogLoaded()
}

export function ensurePostsCatalogLoaded() {
  if (_postsCatalogLoaded) return Promise.resolve(posts)
  if (_postsCatalogPromise) return _postsCatalogPromise

  _postsCatalogPromise = (async () => {
    try {
      const base = import.meta.env.BASE_URL || '/myweb/'
      const res = await fetch(`${base}data/posts.json`, { cache: 'no-store' })
      if (res.ok) {
        const data = await res.json()
        const list = Array.isArray(data?.posts) ? data.posts : Array.isArray(data) ? data : null
        if (list?.length) {
          posts.splice(0, posts.length, ...list)
        }
      }
    } catch {
      /* keep bundled posts */
    }
    _postsCatalogLoaded = true
    return posts
  })()

  return _postsCatalogPromise
}

/** 文章详情页路由 */
export function postUrl(id) {
  return `/content/${id}`
}

/** 按 id 查找文章 */
export function getPostById(id) {
  return posts.find(p => p.id === Number(id))
}

/** 按标题查找文章（保留兼容） */
export function getPostByTitle(title) {
  return posts.find(p => p.title === title)
}

/** 日期排序（新 → 旧） */
export function getPostsSorted() {
  return [...posts].sort((a, b) => b.date.localeCompare(a.date))
}

/** 日期最新的文章 */
export function getLatestPost() {
  return getPostsSorted()[0]
}

/** 首页精选文章 id（与 posts 里某篇 id 对应，换精选改这里） */
export const FEATURED_POST_ID = 24

/** 分类色条 / 图标色 */
export const CATEGORY_COLORS = {
  前端: '#e85d04',
  Java: '#457b9d',
  Agent: '#7b2cbf',
  部署: '#2a9d8f',
  项目: '#e76f51',
}

export const CATEGORY_ICONS = {
  前端: 'FE',
  Java: 'JV',
  Agent: 'AI',
  部署: 'OP',
  项目: 'PJ',
}

/** PageRails ACG 标签 → 首页 ?tag= 筛选（含别名匹配） */
export const FAN_TAG_FILTERS = {
  'フリーレン': ['フリーレン', 'Frieren', '葬送'],
  'MyGO!!!!!': ['MyGO', 'BanG Dream', 'MyGO!!!!!'],
  BA: ['碧蓝', 'Blue Archive', 'BA'],
}

/** 首页精选（带 url） */
export function getFeaturedPost() {
  const post = getPostById(FEATURED_POST_ID) ?? getLatestPost()
  return { ...post, url: postUrl(post.id) }
}

/** 首页大卡片：精选 + 最新，最多 limit 篇 */
export function getHighlightPosts(limit = 3) {
  const sorted = getPostsSorted().map(p => ({ ...p, url: postUrl(p.id) }))
  const featured = getFeaturedPost()
  const seen = new Set()
  const result = []

  if (featured) {
    result.push({ ...featured, featured: true })
    seen.add(featured.id)
  }

  for (const post of sorted) {
    if (result.length >= limit) break
    if (!seen.has(post.id)) {
      result.push({ ...post, featured: false })
      seen.add(post.id)
    }
  }

  return result
}

export function getRecentPosts(limit = 3) {
  return getPostsSorted()
    .slice(0, limit)
    .map(p => ({ ...p, url: postUrl(p.id) }))
}

export function getCategoryColor(category) {
  return CATEGORY_COLORS[category] || '#5c5c5c'
}

export function getCategoryIcon(category) {
  return CATEGORY_ICONS[category] || category?.slice(0, 2)?.toUpperCase() || '??'
}

export function estimateReadingMinutesFromText(text) {
  const len = String(text || '').replace(/\s+/g, '').length
  return Math.max(1, Math.ceil(len / 450))
}

export function imgUrl(relativePath) {
  if (!relativePath) return ''
  const base = import.meta.env.BASE_URL || '/'
  const path = encodePathSegments(String(relativePath).replace(/^\//, ''))
  return `${base}${path}`
}

/** 判断文章是否匹配 ACG 粉丝标签筛选 */
export function postMatchesFanTag(post, fanTag) {
  const aliases = FAN_TAG_FILTERS[fanTag]
  if (!aliases) return (post.tags || []).includes(fanTag)
  const haystack = `${post.title} ${post.excerpt} ${(post.tags || []).join(' ')}`.toLowerCase()
  return aliases.some(alias => haystack.includes(alias.toLowerCase()))
}

/** 所有分类（去重） */
export function getCategories() {
  return [...new Set(posts.map(p => p.category))]
}

/** 所有标签（去重） */
export function getTags() {
  return [...new Set(posts.flatMap(p => p.tags || []))].sort((a, b) => a.localeCompare(b, 'zh-CN'))
}

/** 标签 + 引用次数，按热度排序 */
export function getTagStats() {
  const counts = new Map()
  for (const post of posts) {
    for (const tag of post.tags || []) {
      counts.set(tag, (counts.get(tag) || 0) + 1)
    }
  }
  return [...counts.entries()]
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag, 'zh-CN'))
}

/** 标签页路由 */
export function tagUrl(tag) {
  return `/tags/${encodeURIComponent(tag)}`
}

/** 按标签筛选（含 ACG 粉丝标签别名） */
export function getPostsByTag(tag) {
  const decoded = decodeURIComponent(tag)
  return getPostsSorted()
    .filter(p => {
      if (FAN_TAG_FILTERS[decoded]) return postMatchesFanTag(p, decoded)
      return (p.tags || []).includes(decoded)
    })
    .map(p => ({ ...p, url: postUrl(p.id) }))
}

/** 文章 OG 封面（cover 优先，兼容 thumb，否则站点默认图） */
export function getPostCover(post) {
  if (!post) return 'img/xiaoqing.png'
  return post.cover || post.thumb || 'img/xiaoqing.png'
}

/** 是否在卡片/预览中展示封面（排除纯默认头像） */
export function hasPostCover(post) {
  return !!(post?.cover || post?.thumb)
}

/** 最近更新日期 */
export function getLastUpdateDate() {
  return getLatestPost()?.date ?? ''
}

/** 相邻文章（newer = 较新，older = 较旧） */
export function getAdjacentPosts(id) {
  const sorted = getPostsSorted()
  const idx = sorted.findIndex(p => p.id === Number(id))
  if (idx === -1) return { newer: null, older: null }
  return {
    newer: idx > 0 ? { ...sorted[idx - 1], url: postUrl(sorted[idx - 1].id) } : null,
    older: idx < sorted.length - 1 ? { ...sorted[idx + 1], url: postUrl(sorted[idx + 1].id) } : null,
  }
}

/** 相关文章（标签 + 分类） */
export function getRelatedPosts(id, limit = 3) {
  const post = getPostById(id)
  if (!post) return []
  const tagSet = new Set(post.tags || [])
  return getPostsSorted()
    .filter(p => p.id !== post.id)
    .map(p => ({
      ...p,
      url: postUrl(p.id),
      score: (p.tags || []).filter(t => tagSet.has(t)).length + (p.category === post.category ? 1 : 0),
    }))
    .filter(p => p.score > 0)
    .sort((a, b) => b.score - a.score || b.date.localeCompare(a.date))
    .slice(0, limit)
}

/** 按年 / 月分组，供归档页使用 */
export function buildArchive() {
  const sorted = getPostsSorted()
  const yearMap = new Map()

  for (const post of sorted) {
    const [year, month] = post.date.split('-')
    const monthNum = parseInt(month, 10)
    if (!yearMap.has(year)) yearMap.set(year, new Map())
    const monthMap = yearMap.get(year)
    if (!monthMap.has(monthNum)) monthMap.set(monthNum, [])
    monthMap.get(monthNum).push({ ...post, url: postUrl(post.id) })
  }

  return Array.from(yearMap.entries())
    .sort((a, b) => Number(b[0]) - Number(a[0]))
    .map(([year, monthMap]) => ({
      year,
      months: Array.from(monthMap.entries())
        .sort((a, b) => b[0] - a[0])
        .map(([month, items]) => ({
          month,
          label: `${month}月`,
          posts: items,
        })),
    }))
}

/** 带 url 字段的列表，供首页使用 */
export function postsWithUrl() {
  return posts.map(p => ({ ...p, url: postUrl(p.id) }))
}

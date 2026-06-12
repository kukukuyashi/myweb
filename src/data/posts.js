/**
 * 文章目录 — 发新文章只需在这里加一条，并放入 Content/ 对应 html 文件
 */
export const SITE_NAME = 'Cyinc 的学习日志'
export const SITE_URL = 'https://kukukuyashi.github.io/myweb'
export const SITE_DESCRIPTION = '前端、Agent 与 Java 学习笔记，踩坑记录与 Twikoo 留言板。'

export const posts = [
  {
    id: 24,
    title: '首页墨染晕染：鼠标 hover 显现线稿',
    date: '2026-06-16',
    category: '前端',
    tags: ['Vue', 'Canvas', 'CSS', '交互', '博客'],
    excerpt: 'InkRevealPanel + Canvas destination-out 遮罩：鼠标划过纸面晕开线稿的实现与参数说明。',
    file: '首页墨染晕染 Canvas 鼠标显现线稿.html'
  },
  {
    id: 23,
    title: '陈皮有多陈：Flask + AI 鉴陈项目笔记',
    date: '2026-06-15',
    category: '项目',
    tags: ['Flask', 'Python', 'AI', 'Qwen', '比赛'],
    excerpt: '传智杯项目复盘：Flask 单体 + 通义千问视觉鉴定陈皮，页面结构、API 流程与降级策略。',
    file: '陈皮有多陈 Flask AI 鉴陈项目笔记.html'
  },
  {
    id: 22,
    title: '博客音乐室：GitHub Pages 上播 FLAC',
    date: '2026-06-14',
    category: '前端',
    tags: ['Vue', '音乐', 'GitHub Pages', 'FLAC', '踩坑'],
    excerpt: '音乐室架构、曲目自动生成、进度条与换页重播 bug 修复，静态站也能当播放器。',
    file: '博客音乐室 GitHub Pages 播 FLAC.html'
  },
  {
    id: 21,
    title: 'GitHub Actions 自动部署 Vue 博客',
    date: '2026-06-13',
    category: '部署',
    tags: ['GitHub Actions', 'CI/CD', 'GitHub Pages', 'Vue', '部署'],
    excerpt: 'push 即发布：workflow 配置、build 脚本、环境变量与常见故障排查。',
    file: 'GitHub Actions 自动部署 Vue 博客.html'
  },
  {
    id: 20,
    title: '个人博客重构记：Vue3 静态站上线',
    date: '2026-06-12',
    category: '前端',
    tags: ['Vue', 'Vite', 'GitHub Pages', '博客', '重构'],
    excerpt: '从老静态页到 Vue3 + Vite 的完整重构历程：选型、目录结构、Pages 踩坑与时间线。',
    file: '个人博客重构记 Vue3 静态站上线.html'
  },
  {
    id: 19,
    title: '留言板 Twikoo 部署笔记',
    date: '2026-06-11',
    category: '部署',
    tags: ['Twikoo', 'Netlify', 'MongoDB', '部署'],
    excerpt: 'Twikoo 留言板完整部署：MongoDB Atlas、Netlify 云函数、博客接入与踩坑记录。',
    file: '留言板 Twikoo 部署笔记.html'
  },
  {
    id: 18,
    title: '从 LLM 到 Agent Skill 笔记',
    date: '2026-06-09',
    category: 'Agent',
    tags: ['Agent', 'LLM', 'Skill', 'MCP', 'AI'],
    excerpt: 'LLM、Token、Context、Prompt、Tool、MCP、Agent、Skill 基础概念梳理，带通俗解释。',
    file: '从 LLM 到 Agent Skill 笔记.html'
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

/** 所有分类（去重） */
export function getCategories() {
  return [...new Set(posts.map(p => p.category))]
}

/** 所有标签（去重） */
export function getTags() {
  return [...new Set(posts.flatMap(p => p.tags || []))].sort((a, b) => a.localeCompare(b, 'zh-CN'))
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

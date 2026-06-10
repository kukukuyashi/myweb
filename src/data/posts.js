/**
 * 文章目录 — 发新文章只需在这里加一条，并放入 Content/ 对应 html 文件
 */
export const posts = [
  {
    id: 18,
    title: '从 LLM 到 Agent Skill 笔记',
    date: '2026-06-09',
    category: 'Agent',
    excerpt: 'LLM、Token、Context、Prompt、Tool、MCP、Agent、Skill 基础概念梳理，带通俗解释。',
    file: '从 LLM 到 Agent Skill 笔记.html'
  },
  {
    id: 12,
    title: 'JAVA笔记一(基本语法)',
    date: '2026-04-03',
    category: 'Java',
    excerpt: 'Java 基本语法学习笔记。',
    file: 'JAVA笔记一(基本语法).html'
  },
  {
    id: 13,
    title: 'JAVA笔记二(流程控制语句)',
    date: '2026-04-03',
    category: 'Java',
    excerpt: 'Java 流程控制语句学习笔记。',
    file: 'JAVA笔记二(流程控制语句).html'
  },
  {
    id: 14,
    title: 'JAVA笔记三(数组)',
    date: '2026-04-03',
    category: 'Java',
    excerpt: 'Java 数组学习笔记。',
    file: 'JAVA笔记三(数组).html'
  },
  {
    id: 15,
    title: 'JAVA笔记四（方法）',
    date: '2026-04-03',
    category: 'Java',
    excerpt: 'Java 方法学习笔记。',
    file: 'JAVA笔记四（方法）.html'
  },
  {
    id: 17,
    title: 'Java的运行原理',
    date: '2026-04-03',
    category: 'Java',
    excerpt: 'Java 运行原理，JVM、内存结构、垃圾回收等。',
    file: 'Java的运行原理.html'
  },
  {
    id: 1,
    title: '前端核心学习表',
    date: '2026-01-30',
    category: '学习',
    excerpt: 'HTML、CSS、JavaScript 核心知识点梳理，适合随时查阅的速查表。',
    file: '前端核心学习表.html'
  },
  {
    id: 2,
    title: 'Vue.js,Three.js和Node.js的区别',
    date: '2025-12-21',
    category: '技术',
    excerpt: '详细介绍 Vue.js、Three.js 和 Node.js 的区别和应用场景。',
    file: 'Vue.js,Three.js和Node.js的区别.html'
  },
  {
    id: 3,
    title: 'RhinoWeb的常见问题',
    date: '2025-12-21',
    category: '小知识',
    excerpt: 'RhinoWeb 使用过程中常见问题的解决方案。',
    file: 'RhinoWeb的常见问题.html'
  },
  {
    id: 10,
    title: 'Web API笔记（四）',
    date: '2025-12-18',
    category: '技术',
    excerpt: 'Web API 综合案例与实战练习。',
    file: 'Web API4.html'
  },
  {
    id: 5,
    title: 'JS进阶笔记（一）',
    date: '2025-12-17',
    category: '技术',
    excerpt: 'JavaScript 进阶知识点，包含闭包、原型链等内容。',
    file: 'JS进阶1.html'
  },
  {
    id: 6,
    title: 'JS进阶笔记（二）',
    date: '2025-12-17',
    category: '技术',
    excerpt: 'JavaScript 进阶知识点，包含异步编程、Promise 等内容。',
    file: 'JS进阶2.html'
  },
  {
    id: 9,
    title: 'Web API笔记（三）',
    date: '2025-12-17',
    category: '技术',
    excerpt: 'Web API 进阶，包含 BOM 操作、本地存储等内容。',
    file: 'Web API3.html'
  },
  {
    id: 8,
    title: 'Web API笔记（二）',
    date: '2025-12-16',
    category: '技术',
    excerpt: 'Web API 进阶，包含事件流、事件委托等内容。',
    file: 'Web API2.html'
  },
  {
    id: 7,
    title: 'Web API学习笔记',
    date: '2025-12-15',
    category: '技术',
    excerpt: 'Web API 核心知识点，包含 DOM 操作、事件监听等内容。',
    file: 'Web API.html'
  },
  {
    id: 11,
    title: 'JS基础笔记',
    date: '2025-12-10',
    category: '技术',
    excerpt: 'JavaScript 基础知识点，变量、数据类型、流程控制等。',
    file: 'JS基础.html'
  },
  {
    id: 4,
    title: 'Vue3学习笔记',
    date: '2025-02-27',
    category: '技术',
    excerpt: 'Vue3 核心知识点学习笔记，包含 Composition API 等新特性。',
    file: 'Vue3学习笔记.html'
  }
]

/** 文章详情页路由 */
export function postUrl(title) {
  return `/content/${title}`
}

/** 按标题查找文章 */
export function getPostByTitle(title) {
  return posts.find(p => p.title === title)
}

/** 日期最新的文章 */
export function getLatestPost() {
  return [...posts].sort((a, b) => b.date.localeCompare(a.date))[0]
}

/** 所有分类（去重） */
export function getCategories() {
  return [...new Set(posts.map(p => p.category))]
}

/** 最近更新日期 */
export function getLastUpdateDate() {
  return getLatestPost()?.date ?? ''
}

/** 按年 / 月分组，供归档页使用 */
export function buildArchive() {
  const sorted = [...posts].sort((a, b) => b.date.localeCompare(a.date))
  const yearMap = new Map()

  for (const post of sorted) {
    const [year, month] = post.date.split('-')
    const monthNum = parseInt(month, 10)
    if (!yearMap.has(year)) yearMap.set(year, new Map())
    const monthMap = yearMap.get(year)
    if (!monthMap.has(monthNum)) monthMap.set(monthNum, [])
    monthMap.get(monthNum).push(post)
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
          posts: items
        }))
    }))
}

/** 带 url 字段的列表，供首页使用 */
export function postsWithUrl() {
  return posts.map(p => ({ ...p, url: postUrl(p.title) }))
}

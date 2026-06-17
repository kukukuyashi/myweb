import { getPostById, postUrl } from './posts'

/**
 * 文章系列 — 发新系列只需在这里加一条，postIds 填 posts.js 里的 id（顺序即阅读顺序）
 */
export const seriesList = [
  {
    slug: 'blog-rebuild',
    title: '博客重构',
    subtitle: 'Vue3 静态站 · CI · 留言 · 音乐 · 墨染',
    description: '从老页面到 CYINC.LOG 的完整演化：重构、部署、互动与视觉实验。',
    accent: '#e85d04',
    postIds: [20, 21, 19, 22, 24],
  },
  {
    slug: 'agent-notes',
    title: 'Agent 笔记',
    subtitle: 'LLM → Tool → MCP → Skill',
    description: 'Agent 相关概念梳理与工具链实践，和 Cursor / Codex 写代码直接相关。',
    accent: '#7b2cbf',
    postIds: [18],
  },
  {
    slug: 'java-basics',
    title: 'Java 基础',
    subtitle: '语法 · 流程 · 数组 · 方法 · JVM',
    description: '早期 Java 学习笔记归档，适合复习基础语法与运行原理。',
    accent: '#457b9d',
    postIds: [12, 13, 14, 15, 17],
  },
]

export function getSeriesBySlug(slug) {
  const series = seriesList.find(s => s.slug === slug)
  if (!series) return null
  return resolveSeries(series)
}

export function getSeriesList() {
  return seriesList.map(resolveSeries)
}

function resolveSeries(series) {
  const posts = series.postIds
    .map(id => {
      const post = getPostById(id)
      if (!post) return null
      return { ...post, url: postUrl(post.id) }
    })
    .filter(Boolean)

  return {
    ...series,
    posts,
    count: posts.length,
    latestDate: posts[0]?.date ?? '',
  }
}

/** 某篇文章所属的系列（可能多篇属于同一系列） */
export function getSeriesForPost(postId) {
  return seriesList
    .filter(s => s.postIds.includes(Number(postId)))
    .map(resolveSeries)
}

/**
 * 项目展示 — 链到博客文章与外部仓库，发新项目在这里加一条
 */
export const projects = [
  {
    slug: 'gerenboke',
    title: 'CYINC.LOG',
    subtitle: '个人博客 · Vue3 SPA',
    description: '工业蓝图风 + ACG 贴纸墙 + 墨染交互 + 音乐室 + Twikoo 留言。GitHub Pages 静态部署。',
    stack: ['Vue 3', 'Vite', 'Pinia', 'Twikoo', 'GitHub Pages'],
    status: 'active',
    postId: 20,
    repo: 'https://github.com/kukukuyashi/myweb',
    demo: 'https://kukukuyashi.github.io/myweb/',
    cover: 'img/xiaoqing.png',
  },
  {
    slug: 'chenpi-ai',
    title: '陈皮有多陈',
    subtitle: 'Flask + 通义千问视觉鉴定',
    description: '传智杯项目：上传陈皮图片，AI 推断年份与品相，含降级策略与 API 流程复盘。',
    stack: ['Flask', 'Python', 'Qwen', 'AI'],
    status: 'archive',
    postId: 23,
    repo: null,
    demo: null,
    cover: null,
  },
]

export function getProjects() {
  return projects
}

export function getProjectBySlug(slug) {
  return projects.find(p => p.slug === slug) ?? null
}

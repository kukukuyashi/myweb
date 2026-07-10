/**
 * 友链与随机传送 — 主站与博客关于页共用
 */
export const friendLinks = [
  {
    name: 'CYINC.LOG',
    url: 'https://kukukuyashi.github.io/myweb/',
    desc: '本站技术博客',
  },
  {
    name: 'GitHub',
    url: 'https://github.com/kukukuyashi/myweb',
    desc: '项目源码',
  },
  {
    name: 'Dify',
    url: 'https://dify.ai/',
    desc: '站内 AI 助手引擎',
  },
  {
    name: 'n8n',
    url: 'https://n8n.io/',
    desc: '发文自动化工作流',
  },
]

/** 留言板空态示例（后端无数据时展示） */
export const guestboardExamples = [
  { name: '友人A', content: '这里可以留言吗？' },
  { name: 'Cyinc', content: '可以，随便写点什么～' },
  { name: '访客', content: '博客和主站有什么区别？' },
]

/** @deprecated 使用 guestboardExamples */
export const cottonExamples = guestboardExamples

/** 随机返回一条友链，用于「随机传送」 */
export function randomFriendLink() {
  const list = friendLinks.filter((l) => !l.url.includes('kukukuyashi.github.io'))
  const pool = list.length ? list : friendLinks
  return pool[Math.floor(Math.random() * pool.length)]
}

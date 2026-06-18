/**
 * 个人资料与 ACG 画廊 — 图片统一用 acg-frame 样式，只在关于页/侧栏展示
 */
export const profile = {
  name: 'Cyinc',
  handle: 'CYINC.LOG',
  tagline: '写代码，也写番剧观后感；Agent 在学，芙莉莲旅途进行中。',
  avatar: 'img/xiaoqing.png',
  email: '1344908013@qq.com',
  github: 'https://github.com/kukukuyashi/myweb',
  blog: 'https://kukukuyashi.github.io/myweb/',

  acgTags: ['葬送のフリーレン', 'MyGO!!!!!', '碧蓝档案', 'OST 厨', 'MAD / AMV', 'Agent'],

  favorites: [
    { label: '最近在听', text: '音乐室里的 葬送のフリーレン OST Disc 1' },
    { label: '最近在看', text: 'Agent 文档比番剧更新还勤（但两者都在追）' },
    { label: '入坑作', text: '从浏览器 F12 到 LLM — 跨度很大，但都很好玩' },
  ],

  /** 侧栏 Now Learning — 改这里即可，不必动组件 */
  learningItems: [
    'AI Agent 架构',
    'MyGO!!!!! / 碧蓝档案',
    'Prompt / Tool Use',
    'Cursor / SDK 实践',
  ],

  /** @deprecated 贴纸墙改用 aboutGallery.js (img/关于/) */
  gallery: [],
}

export function imgUrl(relativePath) {
  const base = import.meta.env.BASE_URL || '/'
  return base + relativePath.replace(/^\//, '')
}

/**
 * 个人资料与 ACG 画廊 — 图片统一用 acg-frame 样式，只在关于页/侧栏展示
 */
export const profile = {
  name: 'Cyinc',
  handle: 'CYINC.LOG',
  tagline: '写代码，也写番剧观后感；Agent 在学，京吹永远进行中。',
  avatar: 'img/xiaoqing.png',
  email: '1344908013@qq.com',
  github: 'https://github.com/kukukuyashi/myweb',
  blog: 'https://kukukuyashi.github.io/myweb/',

  acgTags: ['京吹', 'Galgame', 'OST 厨', 'MAD / AMV', 'Vtuber 切片', '轻小说'],

  favorites: [
    { label: '最近在听', text: '音乐室里的 SANABI / 京吹 / 龙女仆 OST' },
    { label: '最近在看', text: 'Agent 文档比番剧更新还勤（但两者都在追）' },
    { label: '入坑作', text: '从浏览器 F12 到 LLM — 跨度很大，但都很好玩' },
  ],

  /** 画廊：path 相对站点根，caption 可自改 */
  gallery: [
    { path: 'img/xiaoqing.png', caption: '小清 · 站点头像' },
    { path: 'img/huiye1.png', caption: '京吹 chibi' },
    { path: 'img/yuhecy.jpg', caption: '收藏' },
    { path: 'img/guigui.jpg', caption: '收藏' },
    { path: 'img/llk1.jpg', caption: '收藏' },
    { path: 'img/ba2.jpg', caption: '收藏' },
    { path: 'img/ba1.gif', caption: '收藏 · 动图' },
    { path: 'img/1.jfif', caption: '相册' },
    { path: 'img/2.jfif', caption: '相册' },
    { path: 'img/3.jfif', caption: '相册' },
    { path: 'img/4.jfif', caption: '相册' },
    { path: 'img/5.jfif', caption: '相册' },
  ],
}

export function imgUrl(relativePath) {
  const base = import.meta.env.BASE_URL || '/'
  return base + relativePath.replace(/^\//, '')
}

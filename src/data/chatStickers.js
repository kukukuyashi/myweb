/** 自习室表情包,源:img/bqb/。运行时通过 /myweb/img/bqb/<file> 由 nginx 静态服务直出 */
export const chatStickers = [
  { id: 'bqb-1', file: '92AEEFBE902966B7442F5A94B0ED68F3.jpg', label: '微笑' },
  { id: 'bqb-2', file: 'fdb6198e-b4d3-422c-89a2-6a1966162151.png', label: '开心' },
  { id: 'bqb-3', file: 'E1A855C98F49A395C3902284C34A47F4.jpg', label: '酷' },
  { id: 'bqb-4', file: '05625acc8f8279e3143e16ffe8ae4e34.png', label: '困惑' },
  { id: 'bqb-5', file: '89ed7c16d17a9562ea00074b70fb0f6b.gif', label: '哭' },
  { id: 'bqb-6', file: '574b0a80ddfed1e8d2e06ef89db1821a.gif', label: '微醺' },
  { id: 'bqb-7', file: '065e8aa0419625a3b27f57a11f205e84.gif', label: '困' },
  { id: 'bqb-8', file: '0dbdcf4422f09ba56c11de164be73953.gif', label: '搞笑' },
  { id: 'bqb-9', file: '436e521d0491a6ae4b95b3c90874dc1f.jpg', label: '兴奋' },
  { id: 'bqb-10', file: '076e13371464800f8afa3762ee6d5311.gif', label: '真棒' },
]

/** 构造 sticker 在消息里的 URL(走 nginx /myweb/img/ 同域) */
export function stickerUrl(s) {
  return `/myweb/img/bqb/${s.file}`
}
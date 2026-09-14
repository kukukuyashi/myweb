/** 各页墨染背景（固定图，不随 season 切换） */
/* 全部用 .thumb.webp 展示缩略图（~720px）：装饰背景对清晰度不敏感，原图 1MB+ 会拖慢首屏 */

export const HOME_INK_IMAGE = 'img/关于/FrhwkwYaMAE2R6L.thumb.webp'
export const HOME_INK_POSITION = '85% center'

export const ARCHIVE_INK_IMAGE = 'img/关于/FjXsHZJUAAAoQS8.thumb.webp'
export const ARCHIVE_INK_POSITION = '75% center'

export const MUSIC_HEADER_INK_IMAGE = 'img/关于/FjtOo61UoAAWpMY.thumb.webp'
export const MUSIC_HEADER_INK_POSITION = '82% center'

/** 音乐室 · 葬送のフリーレン 专辑区块 */
export const MUSIC_FREREN_INK_IMAGE = 'img/关于/FrhwkwaaYAAQYx4.thumb.webp'
export const MUSIC_FREREN_INK_POSITION = '80% center'

/** 主站各分支 · 墨染头图（img/BA 精选） */
export const PLATFORM_FORUM_INK_IMAGE = 'img/BA/mika/acdcfb54cb622b0e8bdf29af195398f6_720.thumb.webp'
export const PLATFORM_FORUM_INK_POSITION = '70% top'

export const PLATFORM_MUSIC_INK_IMAGE = 'img/BA/魔法伊蕾娜/c9d5e22d00c44a9139f12f3139620173_720.thumb.webp'
export const PLATFORM_MUSIC_INK_POSITION = '75% center'

export const PLATFORM_POMO_INK_IMAGE = 'img/BA/R/日奈/5d0a8942b8224ab477751bdcffa8abc3.thumb.webp'
export const PLATFORM_POMO_INK_POSITION = '68% center'

export const PLATFORM_ME_INK_IMAGE = 'img/BA/X/星野/d6db50f9097db958e26f0fc42c67eb16.thumb.webp'
export const PLATFORM_ME_INK_POSITION = '72% top'

export const PLATFORM_POST_INK_IMAGE = 'img/BA/A/爱莉/2fd0a12728327701054df80f0686eb0f.thumb.webp'
export const PLATFORM_POST_INK_POSITION = '80% center'

/** 论坛页模糊背景候选（img/BA 精选，每次访问随机一张） */
export const FORUM_BACKDROP_POOL = [
  'img/BA/X/星野/d6db50f9097db958e26f0fc42c67eb16.thumb.webp',
  'img/BA/R/日奈/458780fd5ec25ccaefe0fd36ccfbabaa_720.thumb.webp',
  'img/BA/mika/acdcfb54cb622b0e8bdf29af195398f6_720.thumb.webp',
  'img/BA/A/爱莉/2fd0a12728327701054df80f0686eb0f.thumb.webp',
  'img/BA/魔法伊蕾娜/c9d5e22d00c44a9139f12f3139620173_720.thumb.webp',
  'img/BA/G/宫子/07d8a069f0ffec88d536ccf3a067d4d0.thumb.webp',
]

export function pickForumBackdrop() {
  const pool = FORUM_BACKDROP_POOL
  if (!pool.length) return ''
  return pool[Math.floor(Math.random() * pool.length)]
}

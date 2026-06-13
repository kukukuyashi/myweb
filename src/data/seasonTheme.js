/** 按北半球月份切换站点氛围（跑马灯 / 装饰栏；Hero 墨染图见 Home.vue 固定配置） */
export const SEASONS = {
  spring: {
    id: 'spring',
    label: 'SPRING',
    months: [3, 4, 5],
    heroImage: 'img/bkm/2.jfif',
    heroPosition: 'center',
    tickerBoost: ['MyGO!!!!!', 'BanG Dream', '春季刊'],
    railTagline: 'MYGO · LEARNING · AGENT',
  },
  summer: {
    id: 'summer',
    label: 'SUMMER',
    months: [6, 7, 8],
    heroImage: 'img/关于/FjtOo61UoAAWpMY.jfif',
    heroPosition: '82% center',
    tickerBoost: ['BA', '碧蓝档案', 'SUMMER OST'],
    railTagline: 'BA · MUSIC · ACG',
  },
  autumn: {
    id: 'autumn',
    label: 'AUTUMN',
    months: [9, 10, 11],
    heroImage: 'img/关于/FrhwkwYaMAE2R6L.jfif',
    heroPosition: '85% center',
    tickerBoost: ['フリーレン', '葬送', 'AUTUMN LOG'],
    railTagline: 'FRIEREN · AGENT · ACG',
  },
  winter: {
    id: 'winter',
    label: 'WINTER',
    months: [12, 1, 2],
    heroImage: 'img/关于/FjXsHZJUAAAoQS8.jfif',
    heroPosition: '75% center',
    tickerBoost: ['フリーレン', '冬 journey', 'WINTER OST'],
    railTagline: 'FRIEREN · NOTES · WARM',
  },
}

const BASE_TICKER = ['ACG', 'LEARNING', 'AGENT', 'NOTES', 'CYINC.LOG']

export function getSeasonId(date = new Date()) {
  const month = date.getMonth() + 1
  return Object.values(SEASONS).find(s => s.months.includes(month))?.id ?? 'autumn'
}

export function getSeasonConfig(date = new Date()) {
  return SEASONS[getSeasonId(date)] ?? SEASONS.autumn
}

export function getSeasonTickerItems(season = getSeasonConfig()) {
  return [
    { text: season.label, highlight: true },
    ...season.tickerBoost.map(text => ({ text })),
    ...BASE_TICKER.map(text => ({ text })),
    { text: 'hover 晕染', highlight: true },
  ]
}

import { computed, onMounted } from 'vue'
import { getSeasonConfig, getSeasonTickerItems } from '../data/seasonTheme'

export function useSeasonTheme() {
  const season = computed(() => getSeasonConfig())

  const heroImage = computed(() => season.value.heroImage)
  const heroPosition = computed(() => season.value.heroPosition)
  const seasonLabel = computed(() => season.value.label)
  const railTagline = computed(() => season.value.railTagline)
  const tickerItems = computed(() => getSeasonTickerItems(season.value))

  onMounted(() => {
    document.documentElement.setAttribute('data-season', season.value.id)
  })

  return { season, heroImage, heroPosition, seasonLabel, railTagline, tickerItems }
}

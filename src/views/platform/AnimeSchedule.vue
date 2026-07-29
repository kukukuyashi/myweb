<template>
  <div class="anime-schedule platform-page container layout-single">
    <header class="anime-hero platform-panel ink-panel">
      <p class="platform-coord">ANIME · BANGUMI · SCHEDULE</p>
      <h1 class="anime-title">{{ meta.season_label || '本季追番表' }}</h1>
      <p v-if="meta.today_weekday_cn" class="anime-today">
        今天是<strong>{{ meta.today_weekday_cn }}</strong>
        <span v-if="meta.season_count" class="anime-season-count">· 共 {{ meta.season_count }} 部</span>
        <span v-if="meta.updated_at" class="anime-updated">· 数据更新于 {{ formatUpdated(meta.updated_at) }}</span>
      </p>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-else-if="loading" class="muted">加载 Bangumi 放送数据…</p>
    </header>

    <template v-if="!loading && !error">
      <!-- 我的追番 · 今日更新 -->
      <section class="anime-section platform-panel ink-panel">
        <h2>我的追番 · 今日更新</h2>
        <p v-if="!token" class="muted">
          <router-link to="/app/login?redirect=/app/anime">登录</router-link> 后可标记追番，这里会高亮今日更新的番剧。
        </p>
        <div v-else-if="!myToday.length" class="muted">今日没有在追的番更新，去下方时间表添加吧。</div>
        <div v-else class="anime-card-grid">
          <article v-for="item in myToday" :key="item.bangumi_id" class="anime-card is-mine">
            <div class="anime-poster">
              <img v-if="item.cover_url" :src="resolveMediaUrl(item.cover_url)" alt="" class="anime-cover" referrerpolicy="no-referrer" loading="lazy" @error="$event.target.style.display='none'">
              <span v-if="episodeNo(item)" class="anime-ep-badge">第{{ episodeNo(item) }}集</span>
            </div>
            <div class="anime-card-body">
              <h3 :title="displayName(item)">{{ displayName(item) }}</h3>
              <div class="anime-card-actions">
                <AnimeWatchControl
                  :status="watchStatus(item.bangumi_id)"
                  :disabled="busyId === item.bangumi_id"
                  @set="(s) => setWatch(item, s)"
                  @clear="clearWatch(item)"
                />
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- 新番时间表 -->
      <section class="anime-section platform-panel ink-panel anime-timeline">
        <div class="anime-timeline-head">
          <h2>新番时间表</h2>
          <div class="anime-day-tabs">
            <button
              v-for="d in dayTabs"
              :key="d.id"
              type="button"
              class="anime-day-tab"
              :class="{ active: d.id === activeDay }"
              @click="selectDay(d.id)"
            >{{ d.cn }}</button>
          </div>
          <button
            v-if="sortedOfDay.length > pageSize"
            type="button"
            class="anime-more-btn"
            @click="expanded = !expanded"
          >{{ expanded ? '收起' : '更多' }}</button>
        </div>
        <p v-if="!sortedOfDay.length" class="muted">这天暂无热门新番。</p>
        <div v-else class="anime-card-grid anime-timeline-row">
          <article v-for="item in visibleOfDay" :key="item.bangumi_id" class="anime-card" :class="{ 'is-mine': isWatching(item.bangumi_id) }">
            <div class="anime-poster">
              <img v-if="item.cover_url" :src="resolveMediaUrl(item.cover_url)" alt="" class="anime-cover" referrerpolicy="no-referrer" loading="lazy" @error="$event.target.style.display='none'">
              <span v-if="episodeNo(item)" class="anime-ep-badge">第{{ episodeNo(item) }}集</span>
            </div>
            <div class="anime-card-body">
              <h3 :title="displayName(item)">{{ displayName(item) }}</h3>
              <div class="anime-card-actions">
                <AnimeWatchControl v-if="token" :status="watchStatus(item.bangumi_id)" :disabled="busyId === item.bangumi_id" @set="(s) => setWatch(item, s)" @clear="clearWatch(item)" />
                <router-link v-else to="/app/login?redirect=/app/anime" class="platform-btn-ghost sm">登录追番</router-link>
              </div>
            </div>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { usePageMeta } from '../../composables/usePageMeta'
import AnimeWatchControl from '../../components/platform/AnimeWatchControl.vue'
import {
  addAnimeWatchlist,
  fetchAnimeSchedule,
  fetchAnimeWatchlist,
  getPlatformToken,
  removeAnimeWatchlist,
  resolveMediaUrl,
} from '../../api/platform.js'

usePageMeta({ title: '追番表', description: '本季番剧放送表与今日更新。' })

const token = ref(getPlatformToken())
const loading = ref(true)
const error = ref('')
const meta = ref({})
const todayItems = ref([])
const myToday = ref([])
const season = ref([])
const weekdays = ref([])
const watchlist = ref([])
const busyId = ref(null)
const activeDay = ref(1)
const expanded = ref(false)
const pageSize = 7

const dayTabs = [
  { id: 1, cn: '周一' },
  { id: 2, cn: '周二' },
  { id: 3, cn: '周三' },
  { id: 4, cn: '周四' },
  { id: 5, cn: '周五' },
  { id: 6, cn: '周六' },
  { id: 7, cn: '周日' },
]

const watchIds = computed(() => new Set(watchlist.value.map((w) => w.bangumi_id)))
const watchStatusMap = computed(() => {
  const map = {}
  for (const w of watchlist.value) map[w.bangumi_id] = w.status || 'plan'
  return map
})

const itemsByDay = computed(() => {
  const map = {}
  for (const day of weekdays.value) {
    const id = day.weekday?.id
    if (id) map[id] = day.items || []
  }
  if (!Object.keys(map).length) {
    for (const it of season.value) {
      const id = it.air_weekday
      if (!id) continue
      ;(map[id] = map[id] || []).push(it)
    }
  }
  return map
})

const sortedOfDay = computed(() => {
  const list = [...(itemsByDay.value[activeDay.value] || [])]
  list.sort((a, b) => {
    const ra = a.rank || Infinity
    const rb = b.rank || Infinity
    if (ra !== rb) return ra - rb
    return (b.rating || 0) - (a.rating || 0)
  })
  return list
})

const visibleOfDay = computed(() =>
  expanded.value ? sortedOfDay.value : sortedOfDay.value.slice(0, pageSize),
)

function selectDay(id) {
  activeDay.value = id
  expanded.value = false
}

function displayName(item) {
  return item.name_cn || item.name || '未知'
}

function isWatching(id) {
  return watchIds.value.has(id)
}

function watchStatus(id) {
  return watchStatusMap.value[id] || null
}

function episodeNo(item) {
  if (!item.air_date) return null
  const start = new Date(item.air_date + 'T00:00:00')
  if (Number.isNaN(start.getTime())) return null
  const diffDays = Math.floor((Date.now() - start.getTime()) / 86400000)
  if (diffDays < 0) return null
  const ep = Math.floor(diffDays / 7) + 1
  if (ep < 1 || ep > 60) return null
  return ep
}

function formatUpdated(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

async function loadWatchlist() {
  if (!token.value) {
    watchlist.value = []
    return
  }
  try {
    const json = await fetchAnimeWatchlist()
    watchlist.value = json.data?.items || []
  } catch {
    watchlist.value = []
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const json = await fetchAnimeSchedule()
    const data = json.data || {}
    meta.value = data.meta || {}
    weekdays.value = data.weekdays || []
    season.value = data.season || []
    todayItems.value = data.today_items || []
    myToday.value = data.my_updates || []
    activeDay.value = meta.value.today_weekday_id || (new Date().getDay() || 7)
    await loadWatchlist()
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function setWatch(item, status) {
  if (!token.value || busyId.value) return
  busyId.value = item.bangumi_id
  try {
    await addAnimeWatchlist({
      bangumi_id: item.bangumi_id,
      name: item.name,
      name_cn: item.name_cn,
      cover_url: item.cover_url,
      air_weekday: item.air_weekday,
      status,
    })
    await loadWatchlist()
    const json = await fetchAnimeSchedule()
    myToday.value = json.data?.my_updates || []
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

async function clearWatch(item) {
  if (!token.value || busyId.value) return
  busyId.value = item.bangumi_id
  try {
    await removeAnimeWatchlist(item.bangumi_id)
    await loadWatchlist()
    const json = await fetchAnimeSchedule()
    myToday.value = json.data?.my_updates || []
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.anime-hero {
  margin-bottom: 1rem;
  padding: 1.25rem 1.5rem;
}

.anime-title {
  margin: 0.35rem 0 0;
  font-size: clamp(1.4rem, 4vw, 2rem);
}

.anime-today {
  margin: 0.5rem 0 0;
  color: var(--text-muted);
}

.anime-today strong {
  color: var(--orange);
}

.anime-season-count {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--text-muted);
}

.anime-updated {
  font-family: var(--mono);
  font-size: 0.68rem;
}

.anime-section {
  margin-bottom: 1rem;
  padding: 1.15rem 1.25rem;
}

.anime-section h2 {
  margin: 0 0 0.85rem;
  font-size: 1rem;
}

.anime-timeline-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.anime-more-btn {
  margin-left: auto;
  border: 1px solid var(--orange);
  background: var(--orange);
  color: #fff;
  font: inherit;
  font-size: 0.76rem;
  padding: 0.3rem 0.85rem;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.anime-more-btn:hover {
  opacity: 0.85;
}

.anime-timeline-head h2 {
  margin: 0;
}

.anime-day-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.anime-day-tab {
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-muted);
  font: inherit;
  font-size: 0.78rem;
  padding: 0.3rem 0.7rem;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.anime-day-tab:hover {
  color: var(--text);
  border-color: var(--steel);
}

.anime-day-tab.active {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.anime-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.85rem;
}

.anime-timeline-row {
  grid-template-columns: repeat(7, 1fr);
}

.anime-card {
  border: 1px solid var(--border);
  background: var(--bg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.anime-card.is-mine {
  border-color: rgba(232, 93, 4, 0.45);
  box-shadow: 0 0 0 1px rgba(232, 93, 4, 0.15);
}

.anime-poster {
  position: relative;
}

.anime-cover {
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
  background: var(--border);
  display: block;
}

.anime-ep-badge {
  position: absolute;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.72);
  color: #fff;
  font-size: 0.66rem;
  padding: 0.15rem 0.4rem;
  border-top-left-radius: 4px;
}

.anime-card-body {
  padding: 0.55rem 0.6rem;
  display: grid;
  gap: 0.35rem;
}

.anime-card-body h3 {
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.35;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.anime-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}

.platform-btn-primary.sm,
.platform-btn-ghost.sm {
  font-size: 0.68rem;
  padding: 0.3rem 0.55rem;
}

.error { color: #c0392b; }
.muted { color: var(--text-muted); }

@media (max-width: 900px) {
  .anime-timeline-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 560px) {
  .anime-timeline-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
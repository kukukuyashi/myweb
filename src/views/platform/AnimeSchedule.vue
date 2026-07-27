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
      <div v-if="fallbackNotice" class="anime-fallback-banner">
        <p>{{ fallbackNotice }}</p>
        <button type="button" class="platform-btn-ghost sm" :disabled="loading" @click="load">重试拉取</button>
      </div>
    </header>

    <template v-if="!loading && !error">
      <!-- 今日更新 -->
      <section class="anime-section platform-panel ink-panel">
        <h2>我的追番 · 今日更新</h2>
        <p v-if="!token" class="muted">
          <router-link to="/app/login?redirect=/app/anime">登录</router-link> 后可标记追番，这里会高亮今日更新的番剧。
        </p>
        <div v-else-if="!myToday.length" class="muted">今日没有在追的番更新，去下方本季列表添加吧。</div>
        <div v-else class="anime-card-grid">
          <article v-for="item in myToday" :key="item.bangumi_id" class="anime-card is-mine">
            <img v-if="item.cover_url" :src="item.cover_url" alt="" class="anime-cover" referrerpolicy="no-referrer" loading="lazy" @error="$event.target.style.display='none'">
            <div class="anime-card-body">
              <h3>{{ displayName(item) }}</h3>
              <div class="anime-card-actions">
                <a
                  v-if="item.watch_url"
                  :href="item.watch_url"
                  class="platform-btn-ghost sm anime-watch-link"
                  target="_blank"
                  rel="noopener noreferrer"
                >去追番</a>
                <button type="button" class="platform-btn-ghost sm" @click="toggleWatch(item)">取消追番</button>
              </div>
            </div>
          </article>
        </div>

        <details class="anime-all-today">
          <summary>全部今日更新（{{ todayItems.length }}）</summary>
          <ul class="anime-today-list">
            <li v-for="item in todayItems" :key="item.bangumi_id">
              <span>{{ displayName(item) }}</span>
              <div class="anime-list-actions">
                <a
                  v-if="item.watch_url"
                  :href="item.watch_url"
                  class="platform-btn-ghost sm anime-watch-link"
                  target="_blank"
                  rel="noopener noreferrer"
                >去追番</a>
                <button
                  v-if="token"
                  type="button"
                  class="platform-btn-ghost sm"
                  @click="toggleWatch(item)"
                >
                  {{ isWatching(item.bangumi_id) ? '已追' : '追番' }}
                </button>
              </div>
            </li>
          </ul>
        </details>
      </section>

      <!-- 本季浏览 -->
      <section class="anime-section platform-panel ink-panel">
        <div class="anime-section-head">
          <h2>{{ meta.season_label || '本季番剧' }}</h2>
          <input v-model="search" type="search" placeholder="搜索番名…" class="anime-search">
        </div>
        <div class="anime-card-grid">
          <article v-for="item in filteredSeason" :key="item.bangumi_id" class="anime-card">
            <img v-if="item.cover_url" :src="item.cover_url" alt="" class="anime-cover" referrerpolicy="no-referrer" loading="lazy" @error="$event.target.style.display='none'">
            <div class="anime-card-body">
              <h3>{{ displayName(item) }}</h3>
              <p class="anime-air">
                <template v-if="item.air_weekday">周{{ weekdayLabel(item.air_weekday) }} 更新</template>
                <template v-else>放送日未定</template>
              </p>
              <div class="anime-card-actions">
                <a
                  v-if="item.watch_url"
                  :href="item.watch_url"
                  class="platform-btn-ghost sm anime-watch-link"
                  target="_blank"
                  rel="noopener noreferrer"
                >去追番</a>
                <button
                  v-if="token"
                  type="button"
                  class="platform-btn-primary sm"
                  :class="{ active: isWatching(item.bangumi_id) }"
                  @click="toggleWatch(item)"
                >
                  {{ isWatching(item.bangumi_id) ? '★ 追番中' : '追番' }}
                </button>
                <router-link v-else to="/app/login?redirect=/app/anime" class="platform-btn-ghost sm">登录追番</router-link>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- 周视图 -->
      <section class="anime-section platform-panel ink-panel">
        <h2>周放送表</h2>
        <div class="anime-week-grid">
          <div
            v-for="day in weekdays"
            :key="day.weekday?.id"
            class="anime-week-col"
            :class="{ 'is-today': day.weekday?.id === meta.today_weekday_id }"
          >
            <h3>{{ day.weekday?.cn }}</h3>
            <ul>
              <li
                v-for="item in sortedWeekItems(day.items)"
                :key="item.bangumi_id"
                :class="{ mine: isWatching(item.bangumi_id) }"
              >
                <span v-if="isWatching(item.bangumi_id)" class="star">★</span>
                {{ displayName(item) }}
              </li>
            </ul>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { usePageMeta } from '../../composables/usePageMeta'
import {
  addAnimeWatchlist,
  fetchAnimeSchedule,
  fetchAnimeWatchlist,
  getPlatformToken,
  removeAnimeWatchlist,
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
const search = ref('')
const busyId = ref(null)
const fallbackNotice = ref('')

const watchIds = computed(() => new Set(watchlist.value.map((w) => w.bangumi_id)))

const filteredSeason = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return season.value
  return season.value.filter((i) =>
    (i.name_cn || i.name || '').toLowerCase().includes(q)
    || (i.name || '').toLowerCase().includes(q),
  )
})

function displayName(item) {
  return item.name_cn || item.name || '未知'
}

function weekdayLabel(id) {
  const map = { 1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日' }
  return map[id] || '?'
}

function isWatching(id) {
  return watchIds.value.has(id)
}

function sortedWeekItems(items) {
  const list = [...(items || [])]
  list.sort((a, b) => {
    const am = isWatching(a.bangumi_id) ? 0 : 1
    const bm = isWatching(b.bangumi_id) ? 0 : 1
    return am - bm
  })
  return list
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
  fallbackNotice.value = ''
  try {
    const json = await fetchAnimeSchedule()
    const data = json.data || {}
    meta.value = data.meta || {}
    weekdays.value = data.weekdays || []
    season.value = data.season || []
    todayItems.value = data.today_items || []
    myToday.value = data.my_updates || []
    if (meta.value.source === 'fallback' || meta.value.source === 'stale_cache') {
      fallbackNotice.value = meta.value.error || '当前为离线示例数据，Bangumi 暂不可用'
    }
    await loadWatchlist()
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function toggleWatch(item) {
  if (!token.value || busyId.value) return
  busyId.value = item.bangumi_id
  try {
    if (isWatching(item.bangumi_id)) {
      await removeAnimeWatchlist(item.bangumi_id)
    } else {
      await addAnimeWatchlist({
        bangumi_id: item.bangumi_id,
        name: item.name,
        name_cn: item.name_cn,
        cover_url: item.cover_url,
        air_weekday: item.air_weekday,
      })
    }
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

.anime-fallback-banner {
  margin-top: 0.65rem;
  padding: 0.55rem 0.75rem;
  border: 1px dashed rgba(232, 93, 4, 0.45);
  background: rgba(232, 93, 4, 0.06);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.anime-fallback-banner p {
  margin: 0;
  font-size: 0.78rem;
  color: var(--text-muted);
  flex: 1;
  min-width: 200px;
}

.anime-section {
  margin-bottom: 1rem;
  padding: 1.15rem 1.25rem;
}

.anime-section h2 {
  margin: 0 0 0.85rem;
  font-size: 1rem;
}

.anime-section-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.anime-section-head h2 {
  margin: 0;
}

.anime-search {
  border: 1px solid var(--border);
  padding: 0.45rem 0.65rem;
  font: inherit;
  background: var(--bg);
  color: var(--text);
  min-width: 180px;
}

.anime-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.85rem;
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

.anime-cover {
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
  background: var(--border);
}

.anime-card-body {
  padding: 0.65rem;
  display: grid;
  gap: 0.35rem;
}

.anime-card-body h3 {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.35;
}

.anime-air {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.anime-card-actions,
.anime-list-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}

.anime-watch-link {
  text-decoration: none;
  border-color: rgba(232, 93, 4, 0.35);
  color: var(--orange);
}

.anime-watch-link:hover {
  background: rgba(232, 93, 4, 0.08);
}

.anime-all-today {
  margin-top: 1rem;
}

.anime-all-today summary {
  cursor: pointer;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--steel);
}

.anime-today-list {
  list-style: none;
  padding: 0.5rem 0 0;
  margin: 0;
  display: grid;
  gap: 0.4rem;
}

.anime-today-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  border-bottom: 1px dashed var(--border);
  padding-bottom: 0.35rem;
}

.anime-week-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.5rem;
  overflow-x: auto;
}

.anime-week-col {
  border: 1px solid var(--border);
  padding: 0.55rem;
  min-height: 120px;
  background: var(--bg);
}

.anime-week-col.is-today {
  border-color: var(--orange);
  background: rgba(232, 93, 4, 0.06);
}

.anime-week-col h3 {
  margin: 0 0 0.5rem;
  font-size: 0.78rem;
  font-family: var(--mono);
  color: var(--text-muted);
}

.anime-week-col.is-today h3 {
  color: var(--orange);
}

.anime-week-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.35rem;
  font-size: 0.72rem;
  line-height: 1.35;
}

.anime-week-col li.mine {
  color: var(--orange);
  font-weight: 500;
}

.star {
  margin-right: 0.15rem;
}

.platform-btn-primary.sm,
.platform-btn-ghost.sm {
  font-size: 0.68rem;
  padding: 0.3rem 0.55rem;
}

.platform-btn-primary.active {
  opacity: 0.85;
}

.error { color: #c0392b; }
.muted { color: var(--text-muted); }

@media (max-width: 900px) {
  .anime-week-grid {
    grid-template-columns: repeat(3, minmax(140px, 1fr));
  }
}

@media (max-width: 520px) {
  .anime-week-grid {
    grid-template-columns: repeat(2, minmax(140px, 1fr));
  }
}
</style>

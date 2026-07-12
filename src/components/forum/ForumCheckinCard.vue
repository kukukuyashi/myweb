<template>
  <div class="forum-checkin-card" :class="{ 'is-checked': status?.checked_today, 'is-busy': busy }">
    <div v-if="!token" class="checkin-guest">
      <p class="checkin-title">每日签到</p>
      <p class="checkin-sub">登录后签到积累等级，解锁徽章与头像框</p>
      <router-link to="/app/login?redirect=/app/forum" class="platform-btn-primary checkin-btn">
        登录签到
      </router-link>
    </div>

    <template v-else-if="status">
      <div class="checkin-head">
        <div>
          <p class="checkin-title">每日签到</p>
          <p class="checkin-level">
            Lv.{{ status.level }}
            <span class="checkin-title-name">{{ status.title }}</span>
          </p>
        </div>
        <div v-if="status.streak > 0" class="checkin-streak">
          <span class="streak-flame">🔥</span>
          <strong>{{ status.streak }}</strong>
          <span>天</span>
        </div>
      </div>

      <div class="checkin-progress">
        <div class="checkin-progress-bar">
          <span :style="{ width: `${status.progress?.progress_pct || 0}%` }" />
        </div>
        <p class="checkin-progress-text">
          <template v-if="status.progress?.next_level">
            距 Lv.{{ status.progress.next_level }} {{ status.progress.next_title }} 还需 {{ status.progress.xp_to_next }} XP
          </template>
          <template v-else>已满级 · {{ status.xp }} XP</template>
        </p>
      </div>

      <button
        v-if="!status.checked_today"
        type="button"
        class="platform-btn-primary checkin-btn"
        :disabled="busy"
        @click="onCheckin"
      >
        {{ busy ? '签到中…' : '签到领 XP' }}
      </button>
      <div v-else class="checkin-done">
        <span class="checkin-stamp">已签到</span>
        <span class="checkin-done-xp">今日已完成</span>
      </div>

      <Transition name="xp-pop">
        <p v-if="xpPop" class="xp-pop">+{{ xpPop }} XP</p>
      </Transition>
      <p v-if="toast" class="checkin-toast">{{ toast }}</p>

      <details v-if="status.xp_actions?.length" class="checkin-xp-actions">
        <summary>今日经验获取方式</summary>
        <ul>
          <li v-for="row in status.xp_actions" :key="row.action">
            {{ row.label }} +{{ row.xp }} XP/次 · 每日最多 {{ row.daily_max }} 次（上限 {{ row.daily_cap_xp }} XP）
          </li>
        </ul>
      </details>
    </template>

    <p v-else-if="error" class="checkin-error">{{ error }}</p>
    <p v-else class="checkin-sub muted">加载签到状态…</p>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { doCheckin, fetchCheckinStatus } from '../../api/platform.js'

const props = defineProps({
  token: { type: String, default: '' },
})

const status = ref(null)
const busy = ref(false)
const error = ref('')
const toast = ref('')
const xpPop = ref(0)

async function load() {
  if (!props.token) {
    status.value = null
    return
  }
  error.value = ''
  try {
    const json = await fetchCheckinStatus()
    status.value = json.data
  } catch (e) {
    error.value = e.message
  }
}

async function onCheckin() {
  busy.value = true
  toast.value = ''
  xpPop.value = 0
  try {
    const json = await doCheckin()
    const data = json.data || {}
    xpPop.value = data.xp_gained || 0
    toast.value = json.message || '签到成功'
    if (data.is_level_up) {
      setTimeout(() => {
        toast.value = `升级！Lv.${data.level} ${data.title}`
      }, 1200)
    }
    const refreshed = await fetchCheckinStatus()
    status.value = refreshed.data
    window.dispatchEvent(new CustomEvent('platform-checkin-done'))
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
    setTimeout(() => { xpPop.value = 0 }, 1800)
    setTimeout(() => { toast.value = '' }, 4000)
  }
}

watch(() => props.token, load)
onMounted(load)
</script>

<style scoped>
.forum-checkin-card {
  position: relative;
  min-width: min(280px, 100%);
  padding: 1rem 1.1rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  display: grid;
  gap: 0.75rem;
}

.checkin-title {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.checkin-level {
  margin: 0.2rem 0 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.checkin-title-name {
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--orange);
  margin-left: 0.35rem;
}

.checkin-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.checkin-streak {
  display: flex;
  align-items: baseline;
  gap: 0.2rem;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--orange);
}

.checkin-streak strong {
  font-size: 1.25rem;
}

.streak-flame {
  animation: flame-pulse 1.2s ease-in-out infinite;
}

@keyframes flame-pulse {
  50% { transform: scale(1.15); }
}

.checkin-progress-bar {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.checkin-progress-bar span {
  display: block;
  height: 100%;
  background: var(--orange);
  transition: width 0.4s ease;
}

.checkin-progress-text {
  margin: 0.35rem 0 0;
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.checkin-btn {
  width: 100%;
  justify-content: center;
  text-decoration: none;
  text-align: center;
}

.checkin-done {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.checkin-stamp {
  font-family: var(--mono);
  font-size: 0.82rem;
  color: var(--orange);
  border: 2px solid var(--orange);
  padding: 0.2rem 0.55rem;
  transform: rotate(-8deg);
  animation: stamp-in 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes stamp-in {
  from { transform: scale(1.8) rotate(-8deg); opacity: 0; }
  to { transform: scale(1) rotate(-8deg); opacity: 1; }
}

.checkin-done-xp {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.checkin-guest .checkin-sub,
.checkin-sub {
  margin: 0.35rem 0 0.75rem;
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.xp-pop {
  position: absolute;
  right: 1rem;
  top: 0.75rem;
  margin: 0;
  font-family: var(--mono);
  font-size: 1rem;
  color: var(--orange);
  font-weight: 700;
  pointer-events: none;
}

.xp-pop-enter-active {
  animation: xp-float 1.6s ease-out forwards;
}

@keyframes xp-float {
  0% { opacity: 0; transform: translateY(8px); }
  20% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-24px); }
}

.checkin-toast {
  margin: 0;
  font-size: 0.78rem;
  color: #2d6a4f;
}

.checkin-xp-actions {
  margin-top: 0.25rem;
}

.checkin-xp-actions summary {
  cursor: pointer;
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--steel);
}

.checkin-xp-actions ul {
  margin: 0.45rem 0 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.25rem;
  font-size: 0.68rem;
  color: var(--text-muted);
  line-height: 1.4;
}

[data-theme="dark"] .checkin-toast {
  color: #95d5b2;
}

.checkin-error {
  margin: 0;
  font-size: 0.78rem;
  color: #c0392b;
}

.muted { color: var(--text-muted); }
</style>

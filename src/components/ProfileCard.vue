<template>
  <div class="profile-card">
    <router-link to="/about" class="profile-link">
      <div class="acg-frame acg-frame--avatar">
        <img :src="avatarUrl" :alt="profile.name" width="72" height="72">
      </div>
      <div class="profile-text">
        <span class="profile-name">{{ profile.name }}</span>
        <span class="profile-handle">{{ profile.handle }}</span>
        <p class="profile-blurb">{{ blurb }}</p>
      </div>
    </router-link>
    <div class="acg-chips">
      <span v-for="t in chipTags" :key="t" class="acg-chip">{{ t }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { profile, imgUrl } from '../data/profile'

const avatarUrl = computed(() => imgUrl(profile.avatar))

const blurb = '前端 · Agent · ACG 浓度偏高'

const chipTags = profile.acgTags.slice(0, 4)
</script>

<style scoped>
.profile-card {
  margin-bottom: 0;
}

.profile-link {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  text-decoration: none;
  color: inherit;
  margin-bottom: 0.75rem;
}

.profile-link:hover .profile-name {
  color: var(--orange);
}

.profile-text {
  flex: 1;
  min-width: 0;
}

.profile-name {
  display: block;
  font-weight: 600;
  font-size: 0.95rem;
  transition: color 0.15s;
}

.profile-handle {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
}

.profile-blurb {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
  line-height: 1.45;
}

.acg-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.acg-chip {
  font-family: var(--mono);
  font-size: 0.58rem;
  padding: 0.12rem 0.4rem;
  border: 1px solid var(--border);
  color: var(--steel);
  background: var(--bg);
}
</style>

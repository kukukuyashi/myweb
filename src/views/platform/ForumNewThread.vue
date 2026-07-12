<template>
  <div class="container layout-single">
    <PlatformSubPageHeader coord="FORUM · NEW">
      <router-link to="/app/forum" class="back">← 论坛</router-link>
      <h1 class="page-title">发帖</h1>
    </PlatformSubPageHeader>

    <section v-if="!token" class="platform-panel ink-panel">
      <p>请先 <router-link to="/app/login?redirect=/app/forum/new">登录</router-link> 后再发帖。</p>
    </section>

    <form v-else class="platform-panel ink-panel" @submit.prevent="submit">
      <label>
        板块
        <select v-model="form.category_id" required>
          <option disabled value="">选择板块</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </label>
      <label>
        标题
        <input v-model="form.title" required maxlength="200" placeholder="帖子标题" />
      </label>
      <CoverImageField v-model="form.cover_url" scope="forum" />
      <label>
        内容
        <MarkdownEditor
          v-model="form.content"
          :rows="12"
          placeholder="正文内容 · 可点击「上传图片」，或直接拖拽 / 粘贴图片"
          enable-image-upload
        />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" class="btn-primary" :disabled="loading">发布</button>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PlatformSubPageHeader from '../../components/platform/PlatformSubPageHeader.vue'
import { usePageMeta } from '../../composables/usePageMeta'
import MarkdownEditor from '../../components/MarkdownEditor.vue'
import CoverImageField from '../../components/CoverImageField.vue'
import { createForumThread, fetchForumCategories, getPlatformToken } from '../../api/platform.js'

usePageMeta({ title: '发帖', description: '在论坛发布新帖。' })

const router = useRouter()
const route = useRoute()
const token = ref(getPlatformToken())
const categories = ref([])
const loading = ref(false)
const error = ref('')
const form = ref({ category_id: '', title: '', content: '', cover_url: '' })

onMounted(async () => {
  if (!token.value) return
  try {
    const json = await fetchForumCategories()
    categories.value = json.data || []
    const slug = route.query.category
    if (slug) {
      const cat = categories.value.find((c) => c.slug === slug)
      if (cat) form.value.category_id = cat.id
    }
  } catch (e) {
    error.value = e.message
  }
})

async function submit() {
  error.value = ''
  if (!form.value.content.trim()) {
    error.value = '内容不能为空'
    return
  }
  loading.value = true
  try {
    const json = await createForumThread({
      category_id: Number(form.value.category_id),
      title: form.value.title.trim(),
      content: form.value.content.trim(),
      cover_url: form.value.cover_url?.trim() || null,
    })
    router.push(`/app/forum/t/${json.data.id}`)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.back {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--orange);
  text-decoration: none;
}

.card {
  margin-top: 1rem;
  border: 1px solid var(--border);
  background: var(--bg-paper);
  padding: 1.25rem;
}

form { display: grid; gap: 0.85rem; }

label {
  display: grid;
  gap: 0.35rem;
  font-family: var(--mono);
  font-size: 0.78rem;
}

input, select, textarea {
  border: 1px solid var(--border);
  padding: 0.55rem 0.65rem;
  font: inherit;
  background: var(--bg);
}

textarea { resize: vertical; }

.btn-primary {
  width: fit-content;
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.5rem 1rem;
  background: var(--orange);
  border: 1px solid var(--orange);
  color: #fff;
  cursor: pointer;
}

.btn-primary:disabled { opacity: 0.55; }
.error { color: #c0392b; font-size: 0.85rem; }

.card a { color: var(--orange); }
</style>

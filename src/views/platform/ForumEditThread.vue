<template>
  <div class="container layout-single">
    <header class="page-header">
      <router-link :to="`/app/forum/t/${id}`" class="back">← 返回帖子</router-link>
      <h1 class="page-title">编辑帖子</h1>
    </header>

    <section v-if="!token" class="card">
      <p>请先 <router-link to="/app/me">登录</router-link>。</p>
    </section>

    <p v-else-if="loading" class="muted">加载中…</p>
    <p v-else-if="error && !form.title" class="error">{{ error }}</p>

    <form v-else class="card" @submit.prevent="submit">
      <label>
        板块
        <select v-model="form.category_id" required>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </label>
      <label>
        标题
        <input v-model="form.title" required maxlength="200" />
      </label>
      <label>
        内容
        <MarkdownEditor v-model="form.content" :rows="12" />
      </label>
      <div class="actions">
        <button type="submit" class="btn-primary" :disabled="saving">保存</button>
        <button type="button" class="btn-danger" :disabled="saving" @click="remove">删除帖子</button>
      </div>
      <p v-if="msg" class="success">{{ msg }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePageMeta } from '../../composables/usePageMeta'
import MarkdownEditor from '../../components/MarkdownEditor.vue'
import {
  deleteForumThread,
  fetchForumCategories,
  fetchForumThread,
  fetchProfile,
  getPlatformToken,
  updateForumThread,
} from '../../api/platform.js'

const props = defineProps({ id: { type: [String, Number], required: true } })

const router = useRouter()
const token = ref(getPlatformToken())
const categories = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const msg = ref('')
const form = ref({ category_id: '', title: '', content: '' })

usePageMeta({ title: '编辑帖子', description: '编辑论坛帖子。' })

onMounted(async () => {
  if (!token.value) {
    loading.value = false
    return
  }
  try {
    const [catJson, threadJson, meJson] = await Promise.all([
      fetchForumCategories(),
      fetchForumThread(props.id),
      fetchProfile(),
    ])
    categories.value = catJson.data || []
    const t = threadJson.data
    if (t.author?.id !== meJson.data.id) {
      error.value = '无权编辑此帖'
      return
    }
    form.value = {
      category_id: t.category_id,
      title: t.title,
      content: t.content,
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function submit() {
  error.value = ''
  msg.value = ''
  if (!form.value.content.trim()) {
    error.value = '内容不能为空'
    return
  }
  saving.value = true
  try {
    await updateForumThread(props.id, {
      category_id: Number(form.value.category_id),
      title: form.value.title.trim(),
      content: form.value.content.trim(),
    })
    msg.value = '帖子已更新'
    setTimeout(() => router.push(`/app/forum/t/${props.id}`), 400)
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!window.confirm('确定删除这篇帖子？回复也会一并删除。')) return
  saving.value = true
  error.value = ''
  try {
    await deleteForumThread(props.id)
    router.push({ path: '/app/me', query: { tab: 'threads' } })
  } catch (e) {
    error.value = e.message
    saving.value = false
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
  background: var(--card-bg, #fff);
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

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-primary, .btn-danger {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border: 1px solid var(--border);
}

.btn-primary {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.btn-danger {
  background: transparent;
  border-color: #c0392b;
  color: #c0392b;
}

.btn-primary:disabled, .btn-danger:disabled { opacity: 0.55; }

.error { color: #c0392b; font-size: 0.85rem; }
.success { color: #2d6a4f; font-size: 0.85rem; }
.muted { color: var(--text-muted); }

.card a { color: var(--orange); }
</style>

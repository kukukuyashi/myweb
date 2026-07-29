<template>
  <div class="container layout-single">
    <PlatformSubPageHeader
      coord="POST · EDITOR"
      :image="PLATFORM_POST_INK_IMAGE"
      :position="PLATFORM_POST_INK_POSITION"
    >
      <router-link to="/app/me" class="back">← 个人中心</router-link>
      <h1 class="page-title">{{ isEdit ? '编辑文章' : '写文章' }}</h1>
    </PlatformSubPageHeader>

    <section v-if="!token" class="platform-panel ink-panel">
      <p>请先 <router-link to="/app/me">登录</router-link> 后再写文章。</p>
    </section>

    <p v-else-if="loadingPost" class="muted">加载中…</p>

    <form v-else class="platform-panel ink-panel" @submit.prevent="submit">
      <label>
        标题
        <input v-model="form.title" required maxlength="200" placeholder="文章标题" />
      </label>
      <CoverImageField v-model="form.cover_url" scope="post" />
      <label>
        URL 别名（slug，可选）
        <input v-model="form.slug" maxlength="200" placeholder="留空则根据标题自动生成" />
      </label>
      <label>
        分类
        <input v-model="form.category" maxlength="50" placeholder="未分类" />
      </label>
      <label>
        标签（逗号分隔）
        <input v-model="tagsText" placeholder="Vue, FastAPI" />
      </label>
      <label>
        状态
        <select v-model="form.status">
          <option value="draft">草稿</option>
          <option value="published">发布</option>
        </select>
      </label>
      <div class="editor-field">
        <span class="field-label">正文</span>
        <MarkdownEditor
          v-model="form.content"
          :rows="18"
          placeholder="正文内容 · 可点击「上传图片」，或直接拖拽 / 粘贴图片"
          enable-image-upload
          image-upload-scope="post"
        />
      </div>
      <div class="actions">
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '保存中…' : '保存' }}
        </button>
        <button
          v-if="isEdit"
          type="button"
          class="btn-ghost"
          :disabled="summaryLoading"
          @click="runSummary"
        >
          {{ summaryLoading ? '生成中…' : 'AI 摘要' }}
        </button>
        <router-link v-if="isEdit && form.status === 'published'" :to="previewLink" class="btn-link">
          预览
        </router-link>
      </div>
      <p v-if="msg" class="success">{{ msg }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlatformSubPageHeader from '../../components/platform/PlatformSubPageHeader.vue'
import { PLATFORM_POST_INK_IMAGE, PLATFORM_POST_INK_POSITION } from '../../data/inkTheme.js'
import { usePageMeta } from '../../composables/usePageMeta'
import MarkdownEditor from '../../components/MarkdownEditor.vue'
import CoverImageField from '../../components/CoverImageField.vue'
import {
  createPost,
  fetchPost,
  generatePostSummary,
  getPlatformToken,
  updatePost,
} from '../../api/platform.js'

const props = defineProps({
  id: { type: [String, Number], default: null },
})

const route = useRoute()
const router = useRouter()
const token = ref(getPlatformToken())
const loading = ref(false)
const loadingPost = ref(false)
const summaryLoading = ref(false)
const error = ref('')
const msg = ref('')
const tagsText = ref('')
const form = ref({
  title: '',
  slug: '',
  content: '',
  category: '未分类',
  status: 'draft',
  cover_url: '',
})

const isEdit = computed(() => props.id != null && props.id !== '')
const previewLink = computed(() => `/app/posts/${props.id}`)

usePageMeta(() => ({
  title: isEdit.value ? '编辑文章' : '写文章',
  description: '主站文章编辑器。',
}))

function parseTags(text) {
  return text
    .split(/[,，]/)
    .map((t) => t.trim())
    .filter(Boolean)
}

function buildPayload() {
  const payload = {
    title: form.value.title.trim(),
    content: form.value.content.trim(),
    category: form.value.category.trim() || '未分类',
    tags: parseTags(tagsText.value),
    status: form.value.status,
    cover_url: form.value.cover_url?.trim() || null,
  }
  const slug = form.value.slug.trim()
  if (slug) payload.slug = slug
  return payload
}

async function loadPost() {
  if (!isEdit.value || !token.value) return
  loadingPost.value = true
  error.value = ''
  try {
    const json = await fetchPost(props.id, { auth: true })
    const p = json.data
    form.value = {
      title: p.title,
      slug: p.slug,
      content: p.content,
      category: p.category,
      status: p.status,
      cover_url: p.cover_url || '',
    }
    tagsText.value = (p.tags || []).join(', ')
  } catch (e) {
    error.value = e.message
  } finally {
    loadingPost.value = false
  }
}

async function submit() {
  error.value = ''
  msg.value = ''
  if (!form.value.content.trim()) {
    error.value = '正文不能为空'
    return
  }
  loading.value = true
  try {
    const payload = buildPayload()
    if (isEdit.value) {
      await updatePost(props.id, payload)
      msg.value = '文章已更新'
    } else {
      const json = await createPost(payload)
      router.replace(`/app/posts/${json.data.id}/edit`)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function runSummary() {
  if (!isEdit.value) return
  summaryLoading.value = true
  error.value = ''
  msg.value = ''
  try {
    const json = await generatePostSummary(props.id)
    if (json.data.summary) {
      msg.value = `摘要已生成：${json.data.summary.slice(0, 80)}${json.data.summary.length > 80 ? '…' : ''}`
    } else {
      msg.value = json.message || '摘要请求已发送'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    summaryLoading.value = false
  }
}

watch(() => props.id, loadPost)
onMounted(loadPost)
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

.editor-field { display: grid; gap: 0.35rem; }
.field-label { font-family: var(--mono); font-size: 0.78rem; }

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.btn-primary, .btn-ghost {
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

.btn-primary:disabled, .btn-ghost:disabled { opacity: 0.55; }

.btn-ghost { background: transparent; }

.btn-link {
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--orange);
}

.error { color: #c0392b; font-size: 0.85rem; }
.success { color: #2d6a4f; font-size: 0.85rem; }
.muted { color: var(--text-muted); }

.card a { color: var(--orange); }
</style>

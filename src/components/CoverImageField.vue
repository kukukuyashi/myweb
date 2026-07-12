<template>
  <div class="cover-field">
    <span class="cover-label">{{ label }}</span>
    <div class="cover-box">
      <img v-if="previewUrl" :src="previewUrl" alt="" class="cover-preview">
      <div v-else class="cover-placeholder">暂无封面</div>
      <div class="cover-actions">
        <input
          ref="inputRef"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          class="hidden"
          @change="onPick"
        >
        <button type="button" class="platform-btn-ghost sm" :disabled="uploading" @click="pick">
          {{ uploading ? '上传中…' : (previewUrl ? '更换封面' : '上传封面') }}
        </button>
        <button
          v-if="modelValue"
          type="button"
          class="platform-btn-ghost sm danger"
          :disabled="uploading"
          @click="clear"
        >
          移除
        </button>
      </div>
      <p class="cover-hint">建议 16:9 横图 · JPG/PNG/WebP/GIF · 不超过 5MB</p>
      <p v-if="error" class="cover-error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { resolveMediaUrl, uploadForumImage, uploadPostImage } from '../api/platform.js'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '封面图片' },
  scope: { type: String, default: 'post' },
})

const emit = defineEmits(['update:modelValue'])

const inputRef = ref(null)
const uploading = ref(false)
const error = ref('')

const previewUrl = computed(() => resolveMediaUrl(props.modelValue))

function pick() {
  inputRef.value?.click()
}

function clear() {
  error.value = ''
  emit('update:modelValue', '')
}

async function onPick(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    error.value = '图片不能超过 5MB'
    return
  }
  error.value = ''
  uploading.value = true
  try {
    const uploader = props.scope === 'forum' ? uploadForumImage : uploadPostImage
    const json = await uploader(file)
    const url = json.data?.url
    if (!url) throw new Error('上传失败')
    emit('update:modelValue', url)
  } catch (err) {
    error.value = err.message || '封面上传失败'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.cover-field {
  display: grid;
  gap: 0.35rem;
}

.cover-label {
  font-family: var(--mono);
  font-size: 0.78rem;
}

.cover-box {
  border: 1px solid var(--border);
  padding: 0.75rem;
  background: var(--bg);
  display: grid;
  gap: 0.65rem;
}

.cover-preview {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border: 1px solid var(--border);
  aspect-ratio: 16 / 9;
  background: var(--bg-paper);
}

.cover-placeholder {
  aspect-ratio: 16 / 9;
  display: grid;
  place-items: center;
  border: 1px dashed var(--border);
  color: var(--text-muted);
  font-size: 0.82rem;
  background: color-mix(in srgb, var(--bg-paper) 60%, var(--bg));
}

.cover-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.cover-hint {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

.cover-error {
  margin: 0;
  font-size: 0.78rem;
  color: #c0392b;
}

.danger {
  color: #c0392b;
  border-color: rgba(192, 57, 43, 0.35);
}

.hidden {
  display: none;
}
</style>

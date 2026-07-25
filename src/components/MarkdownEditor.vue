<template>
  <div class="md-editor">
    <div class="md-toolbar">
      <div class="mode-tabs">
        <button
          v-for="m in modes"
          :key="m.id"
          type="button"
          :class="{ active: viewMode === m.id }"
          :title="m.hint"
          @click="switchMode(m.id)"
        >
          {{ m.label }}
        </button>
      </div>
      <div class="fmt-btns">
        <button type="button" class="ico" title="加粗" @click="applyFormat('bold')"><strong>B</strong></button>
        <button type="button" class="ico" title="斜体" @click="applyFormat('italic')"><em>I</em></button>
        <button type="button" class="ico" title="删除线" @click="applyFormat('strike')"><s>S</s></button>

        <span class="sep" />

        <label class="fmt-select" title="字号">
          <select :value="''" @change="onFontSizeChange">
            <option value="" disabled>字号</option>
            <option v-for="s in fontSizes" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
        </label>

        <div class="color-group" title="文字颜色">
          <button
            v-for="c in presetColors"
            :key="c"
            type="button"
            class="swatch"
            :style="{ background: c }"
            @click="applyColor(c)"
          />
          <label class="swatch swatch-pick" :style="{ background: customColor }">
            <input type="color" v-model="customColor" @change="applyColor(customColor)" />
          </label>
        </div>

        <span class="sep" />

        <button type="button" class="txt" title="标题" @click="applyFormat('heading')">标题</button>
        <button type="button" class="txt" title="引用" @click="applyFormat('quote')">引用</button>
        <button type="button" class="txt" title="无序列表" @click="applyFormat('ul')">• 列表</button>
        <button type="button" class="txt" title="有序列表" @click="applyFormat('ol')">1. 编号</button>
        <button type="button" class="txt" title="代码" @click="applyFormat('code')">代码</button>
        <button type="button" class="txt" title="插入链接" @click="applyFormat('link')">链接</button>
        <button
          type="button"
          class="txt upload"
          :title="enableImageUpload ? '上传图片' : '插入图片链接'"
          :disabled="imageUploading"
          @click="onImageClick"
        >
          {{ imageUploading ? '上传中…' : (enableImageUpload ? '图片' : '图片') }}
        </button>
      </div>
    </div>

    <p v-if="viewMode === 'rich'" class="md-hint">
      直接打字就行。想改样式：先选中文字，再点上方按钮（加粗 / 字号 / 颜色…）。
    </p>

    <input
      ref="imageInputRef"
      type="file"
      accept="image/jpeg,image/png,image/webp,image/gif"
      class="hidden-file"
      multiple
      @change="onImagePick"
    />

    <div
      class="md-panes"
      :class="[
        `mode-${viewMode}`,
        {
          'is-uploading': imageUploading,
          'can-upload': enableImageUpload,
          'drag-over': dragOver,
        },
      ]"
      @dragover.prevent="onDragOver"
      @dragleave="onDragLeave"
      @drop.prevent="onDrop"
    >
      <div v-show="viewMode === 'rich'" class="pane rich-pane">
        <div
          ref="richRef"
          class="rich-area"
          contenteditable="true"
          spellcheck="false"
          :data-placeholder="placeholder"
          @input="onRichInput"
          @blur="syncRichToModel"
          @paste="onPaste"
        />
      </div>

      <div v-show="viewMode === 'md' || viewMode === 'split'" class="pane md-pane">
        <textarea
          ref="textareaRef"
          :value="modelValue"
          :rows="rows"
          :placeholder="placeholder"
          @input="onTextareaInput"
          @paste="onPaste"
        />
      </div>

      <div v-show="viewMode === 'preview' || viewMode === 'split'" class="pane preview-pane">
        <div v-if="!modelValue.trim()" class="preview-empty">预览区域</div>
        <MarkdownBody v-else :content="modelValue" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import MarkdownBody from './MarkdownBody.vue'
import { htmlToMarkdown, markdownToHtml, sanitizeInlineStyle } from '../utils/markdown.js'
import { resolveMediaUrl, uploadForumImage, uploadPostImage } from '../api/platform.js'

const props = defineProps({
  modelValue: { type: String, default: '' },
  rows: { type: Number, default: 16 },
  placeholder: { type: String, default: '支持 Markdown · 可切换富文本模式' },
  enableImageUpload: { type: Boolean, default: false },
  /** forum | post —— 决定图片上传到哪个目录 */
  imageUploadScope: { type: String, default: 'forum' },
  /** 默认显示模式 */
  defaultMode: { type: String, default: 'rich' },
})

const emit = defineEmits(['update:modelValue'])

const modes = [
  { id: 'rich', label: '所见即所得', hint: '直接写，不用记语法' },
  { id: 'md', label: 'Markdown', hint: '纯文本 Markdown 源码' },
  { id: 'split', label: '分屏', hint: '左源码、右预览' },
  { id: 'preview', label: '预览', hint: '只看最终渲染效果' },
]

const fontSizes = [
  { label: '小字 12px', value: '12px' },
  { label: '正文 14px', value: '14px' },
  { label: '稍大 16px', value: '16px' },
  { label: '大字 18px', value: '18px' },
  { label: '标题 20px', value: '20px' },
]

const presetColors = [
  '#e85d04',
  '#0096c7',
  '#38b000',
  '#d00000',
  '#ffbe0b',
]

const viewMode = ref(props.defaultMode)
const textareaRef = ref(null)
const richRef = ref(null)
const richDirty = ref(false)
const imageInputRef = ref(null)
const imageUploading = ref(false)
const dragOver = ref(false)
const customColor = ref('#e85d04')

function triggerImageUpload() {
  imageInputRef.value?.click()
}

function insertMarkdownImage(url, alt = 'image') {
  const insert = `![${alt}](${url})`
  const richActive = viewMode.value === 'rich'
    || (viewMode.value === 'split' && document.activeElement === richRef.value)

  if (richActive && richRef.value) {
    richRef.value.focus()
    document.execCommand('insertImage', false, resolveMediaUrl(url))
    richDirty.value = true
    syncRichToModel()
    return
  }

  if (viewMode.value === 'preview') {
    viewMode.value = 'md'
  }
  const ta = textareaRef.value
  const start = ta?.selectionStart ?? props.modelValue.length
  const text = props.modelValue
  const before = text.slice(0, start)
  const after = text.slice(start)
  const lead = before && !before.endsWith('\n\n') ? (before.endsWith('\n') ? '\n' : '\n\n') : ''
  const trail = after && !after.startsWith('\n') ? '\n\n' : ''
  emitValue(before + lead + insert + trail + after)
  nextTick(() => {
    ta?.focus()
    if (viewMode.value === 'rich' || viewMode.value === 'split') {
      fillRichFromModel()
    }
  })
}

function onImageClick() {
  if (props.enableImageUpload) {
    triggerImageUpload()
    return
  }
  applyFormat('image')
}

async function uploadImageFile(file) {
  if (!file || !file.type?.startsWith('image/')) return
  if (file.size > 5 * 1024 * 1024) {
    window.alert('图片不能超过 5MB')
    return
  }
  imageUploading.value = true
  try {
    const uploader = props.imageUploadScope === 'post' ? uploadPostImage : uploadForumImage
    const json = await uploader(file)
    const url = json.data?.url
    if (!url) throw new Error('上传失败')
    const alt = file.name.replace(/\.[^.]+$/, '') || 'image'
    insertMarkdownImage(url, alt)
  } catch (err) {
    window.alert(err.message || '图片上传失败')
  } finally {
    imageUploading.value = false
  }
}

async function onImagePick(e) {
  const files = Array.from(e.target.files || [])
  e.target.value = ''
  for (const file of files) {
    await uploadImageFile(file)
  }
}

function onDragOver() {
  if (!props.enableImageUpload) return
  dragOver.value = true
}

function onDragLeave() {
  dragOver.value = false
}

async function onDrop(e) {
  dragOver.value = false
  if (!props.enableImageUpload) return
  const files = Array.from(e.dataTransfer?.files || []).filter((f) => f.type.startsWith('image/'))
  for (const file of files) {
    await uploadImageFile(file)
  }
}

async function onPaste(e) {
  if (!props.enableImageUpload) return
  const items = Array.from(e.clipboardData?.items || [])
  const imageItem = items.find((item) => item.type.startsWith('image/'))
  if (!imageItem) return
  const file = imageItem.getAsFile()
  if (!file) return
  e.preventDefault()
  await uploadImageFile(file)
}

function emitValue(val) {
  emit('update:modelValue', val)
}

function onTextareaInput(e) {
  emitValue(e.target.value)
}

function onRichInput() {
  richDirty.value = true
}

function syncRichToModel() {
  if (!richRef.value || !richDirty.value) return
  emitValue(htmlToMarkdown(richRef.value.innerHTML))
  richDirty.value = false
}

function fillRichFromModel() {
  if (!richRef.value) return
  richRef.value.innerHTML = markdownToHtml(props.modelValue)
  richDirty.value = false
}

async function switchMode(next) {
  if (viewMode.value === 'rich' && next !== 'rich') {
    syncRichToModel()
  }
  viewMode.value = next
  if (next === 'rich' || next === 'split') {
    await nextTick()
    fillRichFromModel()
  }
}

function wrapTextarea(before, after, placeholder = '文字') {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const text = props.modelValue
  const selected = text.slice(start, end) || placeholder
  const next = text.slice(0, start) + before + selected + after + text.slice(end)
  emitValue(next)
  nextTick(() => {
    ta.focus()
    const pos = start + before.length + selected.length + after.length
    ta.setSelectionRange(pos, pos)
  })
}

function insertLinePrefix(prefix) {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const text = props.modelValue
  const lineStart = text.lastIndexOf('\n', start - 1) + 1
  const next = `${text.slice(0, lineStart)}${prefix}${text.slice(lineStart)}`
  emitValue(next)
  nextTick(() => ta.focus())
}

function applyRichStyle(prop, val) {
  const selection = window.getSelection()
  if (!selection || !selection.toString().trim()) return
  document.execCommand('styleWithCSS', false, 'true')
  document.execCommand(prop, false, val)
  richDirty.value = true
  syncRichToModel()
}

function onFontSizeChange(e) {
  if (viewMode.value === 'rich' || viewMode.value === 'split') {
    if (viewMode.value === 'split') richRef.value?.focus()
    applyRichStyle('fontSize', e.target.value)
  }
  e.target.value = ''
}

function applyColor(color) {
  if (viewMode.value === 'rich' || viewMode.value === 'split') {
    if (viewMode.value === 'split') richRef.value?.focus()
    document.execCommand('styleWithCSS', false, 'true')
    document.execCommand('foreColor', false, color)
    richDirty.value = true
    syncRichToModel()
  }
}

function applyFormat(type) {
  if (viewMode.value === 'rich' || (viewMode.value === 'split' && document.activeElement === richRef.value)) {
    applyRichFormat(type)
    richDirty.value = true
    syncRichToModel()
    return
  }

  if (viewMode.value === 'preview') {
    viewMode.value = 'md'
  }

  switch (type) {
    case 'bold':
      wrapTextarea('**', '**')
      break
    case 'italic':
      wrapTextarea('*', '*')
      break
    case 'strike':
      wrapTextarea('~~', '~~')
      break
    case 'heading':
      insertLinePrefix('## ')
      break
    case 'quote':
      insertLinePrefix('> ')
      break
    case 'ul':
      insertLinePrefix('- ')
      break
    case 'ol':
      insertLinePrefix('1. ')
      break
    case 'code':
      wrapTextarea('`', '`', 'code')
      break
    case 'link': {
      const url = window.prompt('链接 URL', 'https://')
      if (url) wrapTextarea('[', `](${url})`, '链接文字')
      break
    }
    case 'image':
      if (props.enableImageUpload) {
        triggerImageUpload()
        break
      }
      {
        const url = window.prompt('图片 URL', 'https://')
        if (url) {
          const alt = window.prompt('图片描述', 'image') || 'image'
          const ta = textareaRef.value
          const start = ta?.selectionStart ?? props.modelValue.length
          const text = props.modelValue
          const insert = `![${alt}](${url})`
          emitValue(text.slice(0, start) + insert + text.slice(start))
        }
      }
      break
    default:
      break
  }
}

function applyRichFormat(type) {
  const el = richRef.value
  if (!el) return
  el.focus()
  document.execCommand('styleWithCSS', false, 'true')
  switch (type) {
    case 'bold':
      document.execCommand('bold')
      break
    case 'italic':
      document.execCommand('italic')
      break
    case 'strike':
      document.execCommand('strikeThrough')
      break
    case 'heading':
      document.execCommand('formatBlock', false, 'h2')
      break
    case 'quote':
      document.execCommand('formatBlock', false, 'blockquote')
      break
    case 'ul':
      document.execCommand('insertUnorderedList')
      break
    case 'ol':
      document.execCommand('insertOrderedList')
      break
    case 'code':
      wrapTextarea('`', '`', 'code')
      break
    case 'link': {
      const url = window.prompt('链接 URL', 'https://')
      if (url) document.execCommand('createLink', false, url)
      break
    }
    case 'image':
      if (props.enableImageUpload) {
        triggerImageUpload()
        break
      }
      {
        const url = window.prompt('图片 URL', 'https://')
        if (url) document.execCommand('insertImage', false, url)
      }
      break
    default:
      break
  }
}

watch(
  () => props.modelValue,
  () => {
    if (viewMode.value === 'rich' || viewMode.value === 'split') {
      if (!richDirty.value) fillRichFromModel()
    }
  },
)
</script>

<style scoped>
.md-editor {
  border: 1px solid var(--border);
  background: var(--bg-paper);
  color: var(--text);
}

.md-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0.55rem;
  border-bottom: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg) 72%, var(--bg-paper));
}

.mode-tabs {
  display: flex;
  gap: 0.25rem;
}

.mode-tabs button,
.fmt-btns button {
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg-paper) 55%, var(--bg));
  color: var(--text);
  cursor: pointer;
  line-height: 1.2;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.fmt-btns button.ico {
  min-width: 2rem;
}

.mode-tabs button:hover:not(.active),
.fmt-btns button:hover {
  border-color: color-mix(in srgb, var(--orange) 55%, var(--border));
  color: var(--orange);
}

.mode-tabs button.active {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.fmt-btns {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem;
}

.fmt-btns .sep {
  width: 1px;
  height: 1.1rem;
  background: var(--border);
  margin: 0 0.15rem;
}

.fmt-select select {
  font-family: var(--mono);
  font-size: 0.72rem;
  padding: 0.3rem 0.4rem;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg-paper) 55%, var(--bg));
  color: var(--text);
  cursor: pointer;
}

.color-group {
  display: flex;
  align-items: center;
  gap: 0.2rem;
}

.color-group .swatch {
  width: 1.15rem;
  height: 1.15rem;
  min-width: 0;
  padding: 0;
  border: 1px solid color-mix(in srgb, #000 20%, var(--border));
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.color-group .swatch:hover {
  transform: scale(1.12);
}

.color-group .swatch-pick input[type='color'] {
  position: absolute;
  inset: -4px;
  width: calc(100% + 8px);
  height: calc(100% + 8px);
  border: none;
  padding: 0;
  background: transparent;
  cursor: pointer;
  opacity: 0;
}

.md-hint {
  margin: 0;
  padding: 0.4rem 0.7rem;
  font-size: 0.74rem;
  color: var(--text-muted);
  background: color-mix(in srgb, var(--orange) 8%, transparent);
  border-bottom: 1px solid var(--border);
}

.md-panes {
  display: grid;
  min-height: 280px;
}

.md-panes.can-upload.drag-over,
.md-panes.can-upload.is-uploading {
  outline: 2px dashed color-mix(in srgb, var(--orange) 55%, var(--border));
  outline-offset: -2px;
}

.mode-split {
  grid-template-columns: 1fr 1fr;
}

.mode-rich,
.mode-md,
.mode-preview {
  grid-template-columns: 1fr;
}

.pane {
  min-height: 280px;
  overflow: auto;
  background: var(--bg-paper);
}

.md-pane textarea,
.rich-area {
  width: 100%;
  min-height: 280px;
  border: none;
  padding: 0.75rem;
  font: inherit;
  font-size: 0.9rem;
  line-height: 1.65;
  resize: vertical;
  background: transparent;
  color: var(--text);
  caret-color: var(--orange);
  box-sizing: border-box;
}

.rich-area {
  outline: none;
}

.rich-area:empty::before {
  content: attr(data-placeholder);
  color: var(--text-muted);
  pointer-events: none;
}

.rich-area :deep(h2) {
  font-size: 1.1rem;
  margin: 0.75em 0 0.35em;
  color: var(--text);
}

.rich-area :deep(p),
.rich-area :deep(li) {
  color: var(--text);
}

.rich-area :deep(blockquote) {
  margin: 0.5em 0;
  padding-left: 0.75em;
  border-left: 3px solid var(--orange);
  color: var(--text-muted);
}

.rich-area :deep(img) {
  max-height: 240px;
  width: auto;
  max-width: 100%;
}

.preview-pane {
  padding: 0.75rem 1rem;
  border-left: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
}

.preview-pane :deep(img) {
  max-height: 240px;
  width: auto;
  max-width: 100%;
}

.mode-md .preview-pane,
.mode-rich .preview-pane,
.mode-preview .preview-pane {
  border-left: none;
}

.preview-empty {
  color: var(--text-muted);
  font-size: 0.88rem;
}

@media (max-width: 720px) {
  .mode-split {
    grid-template-columns: 1fr;
  }
  .preview-pane {
    border-left: none;
    border-top: 1px solid var(--border);
  }
  .md-toolbar {
    gap: 0.35rem;
  }
}

.hidden-file {
  display: none;
}
</style>

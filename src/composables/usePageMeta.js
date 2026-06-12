import { onMounted, onUnmounted, watch, isRef } from 'vue'

export const SITE_NAME = 'Cyinc 的学习日志'
export const SITE_URL = 'https://kukukuyashi.github.io/myweb'
export const SITE_DESCRIPTION = '前端、Agent 与 Java 学习笔记，踩坑记录与 Twikoo 留言板。'

function setMeta(attr, key, content) {
  if (!content) return
  let el = document.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function removeMeta(attr, key) {
  document.querySelector(`meta[${attr}="${key}"]`)?.remove()
}

export function usePageMeta(getMeta) {
  let restoreTitle = document.title

  function apply() {
    const meta = typeof getMeta === 'function' ? getMeta() : getMeta
    const title = meta.title
      ? `${meta.title} · ${SITE_NAME}`
      : SITE_NAME
    const description = meta.description || SITE_DESCRIPTION
    const url = meta.url || `${SITE_URL}${import.meta.env.BASE_URL}`
    const image = meta.image || `${SITE_URL}${import.meta.env.BASE_URL}img/xiaoqing.png`

    document.title = title
    setMeta('name', 'description', description)
    setMeta('property', 'og:title', title)
    setMeta('property', 'og:description', description)
    setMeta('property', 'og:url', url)
    setMeta('property', 'og:type', meta.type || 'website')
    setMeta('property', 'og:image', image)
    setMeta('name', 'twitter:card', 'summary')
    setMeta('name', 'twitter:title', title)
    setMeta('name', 'twitter:description', description)
  }

  onMounted(apply)
  if (isRef(getMeta)) {
    watch(getMeta, apply, { deep: true })
  }

  onUnmounted(() => {
    document.title = restoreTitle
    removeMeta('name', 'description')
    ;['og:title', 'og:description', 'og:url', 'og:type', 'og:image'].forEach(k => removeMeta('property', k))
    ;['twitter:card', 'twitter:title', 'twitter:description'].forEach(k => removeMeta('name', k))
  })
}

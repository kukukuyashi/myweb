import { onMounted, onUnmounted, watch, isRef } from 'vue'
import { useRoute } from 'vue-router'

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

function setCanonical(href) {
  if (!href) return
  let el = document.querySelector('link[rel="canonical"]')
  if (!el) {
    el = document.createElement('link')
    el.rel = 'canonical'
    document.head.appendChild(el)
  }
  el.href = href
}

function removeCanonical() {
  document.querySelector('link[rel="canonical"]')?.remove()
}

export function pageUrl(path = '') {
  const basePath = (import.meta.env.BASE_URL || '/').replace(/\/$/, '')
  const clean = path.replace(/^\//, '')
  const parts = [SITE_URL, basePath, clean].filter(Boolean)
  return parts.join('/').replace(/([^:]\/)\/+/g, '$1')
}

export function usePageMeta(getMeta) {
  const route = useRoute()
  let restoreTitle = document.title

  function defaultUrl() {
    const path = route.path === '/' ? '' : route.path.replace(/^\//, '')
    return pageUrl(path)
  }

  function apply() {
    const meta = typeof getMeta === 'function' ? getMeta() : getMeta
    const title = meta.title
      ? `${meta.title} · ${SITE_NAME}`
      : SITE_NAME
    const description = meta.description || SITE_DESCRIPTION
    const url = meta.url || defaultUrl()
    const image = meta.image || pageUrl('img/xiaoqing.png')

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
    setCanonical(url)
  }

  onMounted(apply)
  if (isRef(getMeta)) {
    watch(getMeta, apply, { deep: true })
  }
  watch(() => route.fullPath, apply)

  onUnmounted(() => {
    document.title = restoreTitle
    removeMeta('name', 'description')
    ;['og:title', 'og:description', 'og:url', 'og:type', 'og:image'].forEach(k => removeMeta('property', k))
    ;['twitter:card', 'twitter:title', 'twitter:description'].forEach(k => removeMeta('name', k))
    removeCanonical()
  })
}

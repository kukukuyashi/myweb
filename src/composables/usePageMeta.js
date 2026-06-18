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

const JSON_LD_ID = 'cyinc-json-ld'

function setJsonLd(data) {
  removeJsonLd()
  if (!data) return
  const script = document.createElement('script')
  script.id = JSON_LD_ID
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(data)
  document.head.appendChild(script)
}

function removeJsonLd() {
  document.getElementById(JSON_LD_ID)?.remove()
}

export function pageUrl(path = '') {
  const clean = path.replace(/^\//, '')
  const root = SITE_URL.replace(/\/$/, '')
  if (!clean) return `${root}/`
  return `${root}/${clean}`.replace(/([^:]\/)\/+/g, '$1')
}

export function absoluteAssetUrl(relativePath) {
  const asset = String(relativePath || 'img/xiaoqing.png').replace(/^\//, '')
  return pageUrl(asset)
}

/** 文章页 BlogPosting 结构化数据 */
export function buildArticleJsonLd(post, options = {}) {
  if (!post) return null
  const url = options.url || pageUrl(`content/${post.id}`)
  const image = options.image || absoluteAssetUrl(options.cover || post.cover)
  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.excerpt,
    datePublished: post.date,
    dateModified: post.updated || post.date,
    author: {
      '@type': 'Person',
      name: 'Cyinc',
      url: SITE_URL,
    },
    publisher: {
      '@type': 'Person',
      name: 'Cyinc',
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': url,
    },
    url,
    image,
    keywords: (post.tags || []).join(', '),
    articleSection: post.category,
    inLanguage: 'zh-CN',
  }
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
    const image = meta.image || absoluteAssetUrl('img/xiaoqing.png')

    document.title = title
    setMeta('name', 'description', description)
    setMeta('property', 'og:title', title)
    setMeta('property', 'og:description', description)
    setMeta('property', 'og:url', url)
    setMeta('property', 'og:type', meta.type || 'website')
    setMeta('property', 'og:image', image)
    setMeta('name', 'twitter:card', 'summary_large_image')
    setMeta('name', 'twitter:title', title)
    setMeta('name', 'twitter:description', description)
    setMeta('name', 'twitter:image', image)
    setCanonical(url)
    setJsonLd(meta.jsonLd)
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
    ;['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'].forEach(k => removeMeta('name', k))
    removeCanonical()
    removeJsonLd()
  })
}

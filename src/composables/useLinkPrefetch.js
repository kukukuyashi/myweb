import router from '../router'

const prefetchedRoutes = new Set()
const prefetchedArticles = new Set()

function scheduleIdle(fn) {
  if (typeof requestIdleCallback === 'function') {
    requestIdleCallback(fn, { timeout: 2000 })
  } else {
    setTimeout(fn, 80)
  }
}

/** 预加载路由 chunk（鼠标悬停导航时） */
export function prefetchRouteByName(name) {
  if (!name || prefetchedRoutes.has(name)) return
  const route = router.getRoutes().find((r) => r.name === name)
  const comp = route?.components?.default
  if (typeof comp !== 'function') return
  prefetchedRoutes.add(name)
  comp()
}

/** 预加载文章 HTML（悬停文章链接时） */
export function prefetchArticleFile(file) {
  if (!file || prefetchedArticles.has(file)) return
  prefetchedArticles.add(file)
  const base = import.meta.env.BASE_URL || '/'
  fetch(`${base}Content/${encodeURIComponent(file)}`, { priority: 'low' }).catch(() => {})
  prefetchRouteByName('Content')
}

export function onNavHover(name) {
  scheduleIdle(() => prefetchRouteByName(name))
}

export function onArticleHover(post) {
  if (!post?.file) return
  scheduleIdle(() => prefetchArticleFile(post.file))
}

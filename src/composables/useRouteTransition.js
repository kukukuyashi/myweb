import { ref } from 'vue'

function prefersReducedMotion() {
  return typeof window !== 'undefined'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/** 列表 ↔ 文章 方向性过渡名 */
export function useRouteTransition(router) {
  const transitionName = ref('page-fade')

  router.beforeEach((to, from) => {
    if (prefersReducedMotion()) {
      transitionName.value = 'page-fade'
      return true
    }

    const toContent = to.name === 'Content'
    const fromContent = from.name === 'Content'

    if (toContent && !fromContent) {
      transitionName.value = 'slide-forward'
    } else if (!toContent && fromContent) {
      transitionName.value = 'slide-back'
    } else if (toContent && fromContent) {
      transitionName.value = 'slide-forward-soft'
    } else {
      transitionName.value = 'page-fade'
    }

    return true
  })

  return { transitionName }
}

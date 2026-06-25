import { ref } from 'vue'

function prefersReducedMotion() {
  return typeof window !== 'undefined'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/** 列表 ↔ 文章 方向性过渡名 */
export function useRouteTransition(router) {
  const transitionName = ref('page-fade')

  router.beforeEach((to, from) => {
    // 路由切换时显示动态光标
    document.documentElement.classList.add('cursor-busy')
    
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

  router.afterEach(() => {
    // 路由切换完成后恢复普通光标（延迟一点等待过渡动画）
    setTimeout(() => {
      document.documentElement.classList.remove('cursor-busy')
    }, 300)
  })

  return { transitionName }
}

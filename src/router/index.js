import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  },
  {
    path: '/archive',
    name: 'Archive',
    component: () => import('../views/Archive.vue')
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('../views/Projects.vue')
  },
  {
    path: '/changelog',
    name: 'Changelog',
    component: () => import('../views/Changelog.vue')
  },
  {
    path: '/tags/:tag',
    name: 'Tag',
    component: () => import('../views/TagView.vue'),
    props: true
  },
  {
    path: '/music',
    name: 'Music',
    component: () => import('../views/Music.vue')
  },
  {
    path: '/guestbook',
    name: 'Guestbook',
    component: () => import('../views/Guestbook.vue')
  },
  {
    path: '/content/:id',
    name: 'Content',
    component: () => import('../views/Content.vue'),
    props: true
  },
  // 须在 catch-all 之前注册；异步 addRoute 会导致首屏 /admin 被 NotFound 抢走
  ...(import.meta.env.DEV
    ? [
        {
          path: '/admin',
          name: 'NotesAdmin',
          component: () => import('../views/admin/NotesAdmin.vue'),
        },
      ]
    : []),
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory('/myweb/'),
  routes
})

export default router
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
    path: '/ai',
    redirect: '/app/forum',
  },
  {
    path: '/app',
    component: () => import('../layouts/PlatformLayout.vue'),
    children: [
      {
        path: '',
        name: 'PlatformHome',
        component: () => import('../views/platform/PlatformHome.vue'),
      },
      {
        path: 'ai',
        redirect: '/app/forum',
      },
      {
        path: 'forum',
        name: 'ForumCategories',
        component: () => import('../views/platform/ForumCategories.vue'),
      },
      {
        path: 'forum/c/:slug',
        name: 'ForumCategory',
        component: () => import('../views/platform/ForumCategory.vue'),
        props: true,
      },
      {
        path: 'forum/new',
        name: 'ForumNewThread',
        component: () => import('../views/platform/ForumNewThread.vue'),
      },
      {
        path: 'forum/t/:id/edit',
        name: 'ForumEditThread',
        component: () => import('../views/platform/ForumEditThread.vue'),
        props: true,
      },
      {
        path: 'forum/t/:id',
        name: 'ForumThread',
        component: () => import('../views/platform/ForumThread.vue'),
        props: true,
      },
      {
        path: 'posts/new',
        name: 'PostNew',
        component: () => import('../views/platform/PostEditor.vue'),
      },
      {
        path: 'posts/:id/edit',
        name: 'PostEdit',
        component: () => import('../views/platform/PostEditor.vue'),
        props: true,
      },
      {
        path: 'posts/:id',
        name: 'PostDetail',
        component: () => import('../views/platform/PostDetail.vue'),
        props: true,
      },
      {
        path: 'me',
        name: 'Me',
        component: () => import('../views/Me.vue'),
      },
      {
        path: 'u/:id',
        name: 'UserProfile',
        component: () => import('../views/platform/UserProfile.vue'),
        props: true,
      },
      {
        path: 'login',
        name: 'Login',
        component: () => import('../views/auth/Login.vue'),
        meta: { guestOnly: true },
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('../views/auth/Register.vue'),
        meta: { guestOnly: true },
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: () => import('../views/auth/ForgotPassword.vue'),
        meta: { guestOnly: true },
      },
      {
        path: 'pomo',
        name: 'Pomo',
        component: () => import('../views/Pomo.vue'),
      },
      {
        path: 'music',
        name: 'PlatformMusic',
        component: () => import('../views/platform/PlatformMusic.vue'),
      },
      {
        path: 'anime',
        name: 'AnimeSchedule',
        component: () => import('../views/platform/AnimeSchedule.vue'),
      },
      {
        path: 'arcade',
        name: 'Arcade',
        component: () => import('../views/platform/Arcade.vue'),
      },
    ],
  },
  { path: '/hub', redirect: '/app' },
  { path: '/me', redirect: '/app/me' },
  { path: '/pomo', redirect: '/app/pomo' },
  { path: '/forum', redirect: '/app/forum' },
  {
    path: '/content/:id',
    name: 'Content',
    component: () => import('../views/Content.vue'),
    props: true
  },
  {
    path: '/admin',
    name: 'NotesAdmin',
    component: () => import('../views/admin/NotesAdmin.vue'),
    meta: { title: '笔记管理台' },
  },
  {
    path: '/admin/acg-bot',
    name: 'AcgBotAdmin',
    component: () => import('../views/admin/AcgBotAdmin.vue'),
    meta: { title: 'ACG 资讯机器人' },
  },
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

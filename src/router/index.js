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
    path: '/app/pomo',
    name: 'FocusSpace',
    component: () => import('../views/platform/FocusSpace.vue')
  },
  {
    path: '/ai',
    redirect: '/app',
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
        redirect: '/app',
      },
      { path: 'forum', redirect: '/app' },
      { path: 'forum/c/:slug', redirect: '/app' },
      { path: 'forum/new', redirect: '/app' },
      { path: 'forum/t/:id/edit', redirect: '/app' },
      { path: 'forum/t/:id', redirect: '/app' },
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
        redirect: '/app',
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
        path: 'chat',
        name: 'ChatRoom',
        component: () => import('../views/platform/ChatRoom.vue'),
        meta: { title: '聊天室' },
      },
      {
        path: 'music',
        name: 'PlatformMusic',
        component: () => import('../views/platform/PlatformMusic.vue'),
      },
      {
        path: 'anime',
        redirect: '/app',
      },
      {
        path: 'arcade',
        name: 'Arcade',
        component: () => import('../views/platform/Arcade.vue'),
      },
      {
        path: 'arcade/schulte',
        name: 'ArcadeSchulte',
        component: () => import('../views/platform/ArcadeSchulte.vue'),
      },
      {
        path: 'arcade/stroop',
        name: 'ArcadeStroop',
        component: () => import('../views/platform/ArcadeStroop.vue'),
      },
      {
        path: 'arcade/dots',
        name: 'ArcadeDots',
        component: () => import('../views/platform/ArcadeDots.vue'),
      },
      {
        path: 'arcade/reaction',
        redirect: '/app/arcade',
      },
      {
        path: 'arcade/size',
        name: 'ArcadeSize',
        component: () => import('../views/platform/ArcadeSize.vue'),
      },
      {
        path: 'links',
        name: 'FriendLinks',
        component: () => import('../views/platform/FriendLinks.vue'),
      },
    ],
  },
  { path: '/hub', redirect: '/app' },
  { path: '/me', redirect: '/app/me' },
  { path: '/pomo', redirect: '/app/pomo' },
  { path: '/forum', redirect: '/app' },
  {
    path: '/content/:id',
    name: 'Content',
    component: () => import('../views/Content.vue'),
    props: true
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminConsole.vue'),
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/AdminDashboard.vue'),
        meta: { title: '管理控制台 · 仪表盘' },
      },
      {
        path: 'notes',
        name: 'NotesAdmin',
        component: () => import('../views/admin/NotesAdmin.vue'),
        props: { embedded: true },
        meta: { title: '笔记管理' },
      },
      {
        path: 'glossary',
        name: 'GlossaryAdmin',
        component: () => import('../views/admin/GlossaryAdmin.vue'),
        props: { embedded: true },
        meta: { title: '术语库' },
      },
      {
        path: 'links',
        name: 'FriendLinksAdmin',
        component: () => import('../views/admin/FriendLinksAdmin.vue'),
        props: { embedded: true },
        meta: { title: '友链管理' },
      },
      {
        path: 'pages',
        name: 'SitePagesAdmin',
        component: () => import('../views/admin/SitePagesAdmin.vue'),
        meta: { title: '页面管理' },
      },
      {
        path: 'acg-bot',
        name: 'AcgBotAdmin',
        component: () => import('../views/admin/AcgBotAdmin.vue'),
        props: { embedded: true },
        meta: { title: 'ACG 资讯机器人' },
      },
      {
        path: 'data',
        name: 'DataAdmin',
        component: () => import('../views/admin/DataAdmin.vue'),
        meta: { title: '数据管理' },
      },
      {
        path: 'study-room',
        name: 'StudyRoomAdmin',
        component: () => import('../views/admin/StudyRoomAdmin.vue'),
        meta: { title: '聊天室管理' },
      },
      {
        path: 'qa',
        name: 'QaAdmin',
        component: () => import('../views/admin/QaAdmin.vue'),
        meta: { title: '留言板设置' },
      },
    ],
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

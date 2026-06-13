<template>
  <div class="not-found">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <SystemHaltPanel
            code="404"
            message="页面不存在或已被移除。"
            status="ROUTE_FAULT"
            :lines="diagLines"
            home-label="← 返回首页"
          />
        </div>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import SiteFooter from '../components/SiteFooter.vue'
import SystemHaltPanel from '../components/SystemHaltPanel.vue'
import { usePageMeta } from '../composables/usePageMeta'

const route = useRoute()

usePageMeta({ title: '404', description: '页面不存在或已被移除。' })

const diagLines = computed(() => [
  `ERR:: ROUTE NOT FOUND`,
  `PATH:: ${route.fullPath}`,
  `TIME:: ${new Date().toISOString().slice(0, 19).replace('T', ' ')} UTC`,
  `NODE:: CYINC.LOG / HALT`,
])
</script>

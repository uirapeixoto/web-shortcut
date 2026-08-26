<template>
  <div id="app-root">
    <TopMenu v-if="route.path !== '/'" />
    <div class="layout" v-if="route.path !== '/'">
      <SideMenu />
      <main class="main-content" :class="{ expanded: !store.sideOpen }">
        <router-view />
      </main>
    </div>
    <router-view v-else />
    <TaskAlarm />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { onMounted, onUnmounted } from 'vue'
import TopMenu from './components/TopMenu.vue'
import SideMenu from './components/SideMenu.vue'
import TaskAlarm from './components/TaskAlarm.vue'
import { useStore } from './store/index.js'
import { useSchedulerStore } from './store/scheduler.js'
import { useThemeStore } from './store/theme.js'

const route = useRoute()
const store = useStore()
const scheduler = useSchedulerStore()
const theme = useThemeStore()

onMounted(() => {
  theme.initTheme()
  store.fetchCategories()
  scheduler.init()
})
onUnmounted(() => scheduler.destroy())
</script>

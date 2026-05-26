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
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'
import TopMenu from './components/TopMenu.vue'
import SideMenu from './components/SideMenu.vue'
import { useStore } from './store/index.js'

const route = useRoute()
const store = useStore()
onMounted(() => store.fetchCategories())
</script>

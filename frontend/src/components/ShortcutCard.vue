<template>
  <a :href="shortcut.url" target="_blank" rel="noopener" class="shortcut-card" :style="{ '--card-color': shortcut.color }">
    <div class="card-icon">{{ shortcut.icon }}</div>
    <div class="card-body">
      <div class="card-name">{{ shortcut.name }}</div>
      <div class="card-desc">{{ shortcut.description }}</div>
    </div>
    <div class="card-arrow">→</div>
  </a>
</template>

<script setup>
defineProps({ shortcut: Object })
</script>

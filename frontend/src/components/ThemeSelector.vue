<template>
  <div class="theme-selector">
    <button class="theme-btn" @click="showDropdown = !showDropdown" :title="`Tema: ${capitalize(theme.currentTheme)}`">
      <svg v-if="theme.currentTheme === 'dark'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
      <svg v-else-if="theme.currentTheme === 'light'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5"/>
        <line x1="12" y1="1" x2="12" y2="3"/>
        <line x1="12" y1="21" x2="12" y2="23"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
        <line x1="1" y1="12" x2="3" y2="12"/>
        <line x1="21" y1="12" x2="23" y2="12"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="16 18 22 12 16 6"/>
        <polyline points="8 6 2 12 8 18"/>
      </svg>
    </button>

    <div v-if="showDropdown" class="theme-dropdown">
      <button
        v-for="t in theme.themes"
        :key="t"
        @click="selectTheme(t)"
        :class="['theme-option', { active: theme.currentTheme === t }]"
      >
        <span class="theme-icon">
          <svg v-if="t === 'dark'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
          <svg v-else-if="t === 'light'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="16 18 22 12 16 6"/>
            <polyline points="8 6 2 12 8 18"/>
          </svg>
        </span>
        <span class="theme-label">{{ capitalize(t) }}</span>
        <span v-if="theme.currentTheme === t" class="theme-check">✓</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useThemeStore } from '../store/theme.js'

const theme = useThemeStore()
const showDropdown = ref(false)

function selectTheme(themeName) {
  theme.setTheme(themeName)
  showDropdown.value = false
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}
</script>

<style scoped>
.theme-selector {
  position: relative;
}

.theme-btn {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  color: var(--text2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
}

.theme-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  background: var(--bg2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  min-width: 140px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  overflow: hidden;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.theme-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: none;
  background: none;
  color: var(--text2);
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.15s ease;
}

.theme-option:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
}

.theme-option.active {
  background: var(--bg3);
  color: var(--accent);
}

.theme-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.theme-label {
  flex: 1;
  text-align: left;
}

.theme-check {
  font-size: 0.7rem;
  font-weight: 700;
  margin-left: auto;
}
</style>

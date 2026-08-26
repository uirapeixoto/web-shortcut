import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref('dark')

  const themes = {
    light: {
      bg: '#ffffff',
      bg2: '#f5f5f7',
      bg3: '#ececf1',
      accent: '#0066cc',
      accent2: '#7c3aed',
      text: '#1f2937',
      text2: '#6b7280',
    },
    dark: {
      bg: '#0f0f1a',
      bg2: '#16162a',
      bg3: '#1e1e35',
      accent: '#6366f1',
      accent2: '#a855f7',
      text: '#e2e8f0',
      text2: '#94a3b8',
    },
    code: {
      bg: '#1e1e1e',
      bg2: '#252526',
      bg3: '#2d2d30',
      accent: '#007acc',
      accent2: '#646695',
      text: '#d4d4d4',
      text2: '#858585',
    },
  }

  function initTheme() {
    const saved = localStorage.getItem('app-theme')
    if (saved && Object.keys(themes).includes(saved)) {
      currentTheme.value = saved
    }
    applyTheme()
  }

  function applyTheme() {
    const theme = themes[currentTheme.value]
    const root = document.documentElement

    Object.entries(theme).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value)
    })

    root.setAttribute('data-theme', currentTheme.value)
  }

  function setTheme(themeName) {
    if (Object.keys(themes).includes(themeName)) {
      currentTheme.value = themeName
      localStorage.setItem('app-theme', themeName)
      applyTheme()
    }
  }

  watch(() => currentTheme.value, applyTheme)

  return {
    currentTheme,
    themes: Object.keys(themes),
    setTheme,
    initTheme,
  }
})

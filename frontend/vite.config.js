import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8010', rewrite: p => p.replace(/^\/api/, '') }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          mermaid: ['mermaid'],
          marked: ['marked']
        }
      }
    },
    chunkSizeWarningLimit: 800
  }
})

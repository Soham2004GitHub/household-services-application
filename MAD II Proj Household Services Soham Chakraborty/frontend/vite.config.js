import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      'vue': 'vue/dist/vue.esm-bundler.js' // ✅ Fix for runtime compilation issue
    }
  },
  server: {
    watch: {
      usePolling: true,
    },
    host: "localhost",
    port: 5000,
  },
})
/*
plugins: [vue()],
  

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },

*/
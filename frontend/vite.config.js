import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Загружаем .env.[mode]
  const env = loadEnv(mode, process.cwd(), '')

  return {
    // В продакшн сборке все ассеты будут под URL-префиксом /static/
    base: '/static/',

    plugins: [vue()],

    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },

    define: {
      // Позволяет использовать import.meta.env.VITE_API_URL в коде
      'process.env': {},
    },

    // Настройки сборки
    build: {
      // Выводим результат сборки прямо в папку Flask-проекта
      outDir: path.resolve(__dirname, '../backend/frontend/dist'),
      emptyOutDir: true,
      rollupOptions: {
        input: path.resolve(__dirname, 'index.html'),
      }
    },

    server: {
      port: Number(env.VITE_DEV_PORT) || 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:5000',
          changeOrigin: true,
          rewrite: p => p.replace(/^\/api/, '/api'),
        },
        '/media': {
          target: env.VITE_API_URL || 'http://localhost:5000',
          changeOrigin: true,
        }
      }
    }
  }
})
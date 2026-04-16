import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { APP_BASE_PATH } from './src/config/paths'

export default defineConfig({
  base: APP_BASE_PATH + '/',
  plugins: [react()],
  server: {
    proxy: {
      '/vecsearch': {
        target: 'https://innoflow.study.sensetime.com',
        changeOrigin: true,
        secure: false,
        headers: {
          'Access-Control-Allow-Origin': '*'
        }
      },
      '/v1': {
        target: 'https://innoflow.study.sensetime.com',
        changeOrigin: true,
        secure: false,
        headers: {
          'Access-Control-Allow-Origin': '*'
        }
      }
    }
  }
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://revenue-maximizer-backend.onrender.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
  preview: {
    host: '0.0.0',
    port: 5173,
    allowedHosts: ['revenue-maximizer-frontend.onrender.com'],
    proxy: {
      '/api': {
        target: 'https://revenue-maximizer-backend.onrender.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Add this line to listen on all interfaces
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://revenue-maximizer-frontend.onrender.com',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
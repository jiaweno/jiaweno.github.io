import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Frontend dev server port
    proxy: {
      // Proxy API requests to backend during development
      '/api': {
        target: 'http://localhost:8000', // Your backend address
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // if your backend doesn't have /api prefix
      }
    }
  }
})

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The API is proxied under /api by the dev server. That keeps the browser on a
// single origin: no CORS, and a friend on the LAN only needs this server's
// address, not the backend's.
const API_TARGET = process.env.CHESS_API_TARGET ?? 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

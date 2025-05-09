/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Ensure base path works when served from FastAPI
  base: './',
  // Production build settings
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  // Allow external hosts for demo purposes
  server: {
    host: true, // Listen on all addresses
    port: 3000,
    strictPort: false,
    cors: true,
    // Disable host checking completely
    hmr: {
      clientPort: 3000,
      host: 'localhost'
    },
    fs: {
      strict: false
    },
    // Allow all cloudflare tunnel domains
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '.trycloudflare.com'
    ]
  },
})

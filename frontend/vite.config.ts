/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
  },
  // Ensure base path works when served from FastAPI
  base: './',
  // Production build settings
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})

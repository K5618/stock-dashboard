import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages 預設需要儲存庫名稱作為根路徑
  base: '/stock-dashboard/',
})

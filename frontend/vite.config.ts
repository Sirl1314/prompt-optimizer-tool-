import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 允许所有地址访问，等价于 0.0.0.0
    port: 5173,
    // 👇 解决公网域名访问被拒绝的问题
    allowedHosts: true, // 临时允许所有主机，测试用最省事
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
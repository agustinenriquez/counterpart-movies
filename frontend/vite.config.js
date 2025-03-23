import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    setupFiles: "./src/setupTests.ts",
    environment: "jsdom",
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
    // Proxy /api requests to the backend
    '/api': {
      target: 'http://web:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '/api'),
      secure: false,
      },
    },
  },
});

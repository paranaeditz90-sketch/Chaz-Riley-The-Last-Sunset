import { defineConfig } from "vite";

// base relativa: o build roda em qualquer pasta (Capacitor, página de teste)
export default defineConfig({
  base: "./",
  build: { assetsInlineLimit: 0, chunkSizeWarningLimit: 2000 },
});

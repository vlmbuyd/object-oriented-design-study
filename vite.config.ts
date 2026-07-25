import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// dojo 실습 전용 최소 설정. 진입점은 index.html → playground/main.tsx.
export default defineConfig({
  plugins: [react()],
  server: { open: true },
});

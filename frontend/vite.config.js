import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En GitHub Pages el sitio vive en /respiragdl/
export default defineConfig({
  plugins: [react()],
  base: process.env.GITHUB_PAGES ? "/respiragdl/" : "/",
});

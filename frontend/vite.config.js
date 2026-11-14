import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base relativa: los assets se piden junto a index.html, así funciona en
// GitHub Pages sin importar el nombre del repo (/RespiraGDL/, /respiragdl/)
// y también en local. Las rutas de la app son con hash (#/tablero).
export default defineConfig({
  plugins: [react()],
  base: "./",
});
